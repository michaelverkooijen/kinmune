#!/usr/bin/env python3
import core
import os
import requests
import json
import time
from slackclient import SlackClient

ts = time.time()
update_interval = 120 #in seconds

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']
is_mod = settings['isMod']

slack_client = SlackClient(settings['slackToken'])

# Log in to Wikia network
session = core.login(wiki, username, password)

wiki_id = core.get_wiki_id(session, wiki)

#TODO: store last post epoch timer, don't depend on system timer.
payload = {'limit': '25', 'page': '0', 'responseGroup': 'small', 'reported': 'false', 'viewableOnly': 'true'}
r = session.get('https://services.wikia.com/discussion/'+wiki_id+'/posts', params=payload, headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
for post in reversed(r.json()['_embedded']['doc:posts']):
    if int(post['creationDate']['epochSecond']) > ts - update_interval:
        content = post['rawContent']
        name = post['createdBy']['name']
        forum_name = post['forumName']
        thread_id = post['threadId']
        message = "<https://tes.wikia.com/d/p/" + thread_id + "|" + content + "> —  *<http://tes.wikia.com/wiki/User:" + name + "|" + name + ">* in _" + forum_name + "_"
        slack_client.api_call("chat.postMessage", channel="discussions-rc", text=message, as_user=True)
