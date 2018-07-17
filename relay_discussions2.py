#!/usr/bin/env python3
import core
import os
import requests
import json
import time
import re
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

# Error logging
if r.status_code is not 200:
    print("HTTP status: " + str(r.status_code))

for post in reversed(r.json()['_embedded']['doc:posts']):
    if int(post['creationDate']['epochSecond']) > ts - update_interval:
        content = post['rawContent']
        name = post['createdBy']['name']
        avatar = post['createdBy']['avatarUrl']
        forum_name = post['forumName']
        thread_id = post['threadId']
        user_id = post['createdBy']['id']
        post_id = post['id']
        thread_title = post['_embedded']['thread'][0]['title']
        if post['isReply']:
            thread_title = post['_embedded']['thread'][0]['title'] + " (reply)"
        is_reply = post['isReply']

        message = "<https://tes.wikia.com/d/p/" + thread_id + "|" + content.replace('\n', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + "> —  *<http://tes.wikia.com/d/u/" + user_id + "|" + name + ">* in _" + forum_name + "_"
        attachment = json.dumps([{
            "fallback": message,
            "author_name": name,
            "author_link": "https://tes.wikia.com/d/u/" + user_id,
            "author_icon": avatar,
            "title": thread_title,
            "title_link": "https://tes.wikia.com/d/p/" + thread_id,
            "text": content.replace('\n', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
            "footer": forum_name
        }])

        #TODO: test for multiple attachments
        if len(post['_embedded']['contentImages']) > 0:
            image = post['_embedded']['contentImages'][0]['url']
            attachment = json.dumps([{
                "fallback": message,
                "author_name": name,
                "author_link": "https://tes.wikia.com/d/u/" + user_id,
                "author_icon": avatar,
                "title": thread_title,
                "title_link": "https://tes.wikia.com/d/p/" + thread_id,
                "text": content.replace('\n', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                "image_url": image + "/scale-to-width-down/400",
                "footer": forum_name
            }])

        slack_client.api_call("chat.postMessage", channel="discussions-rc", text="", attachments=attachment, as_user=True)

        # Delete symbol spam messages not containing any words.
        if not re.match(r'.*\w+', content.replace('\n', ' ')) and is_mod:
            session.put('https://services.wikia.com/discussion/'+wiki_id+'/posts/'+post_id+'/delete', headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
            print('Deleted: https://tes.wikia.com/d/p/'+thread_id+'/r/'+post_id+' and content was: '+content.replace('\n', ' '))
