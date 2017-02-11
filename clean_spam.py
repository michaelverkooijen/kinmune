#!/usr/bin/env python3
import core
import os
import requests
import json
import time

ts = time.time()
update_interval = 120 #in seconds

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
blacklist = json.load(open(os.environ['HOME']+'/.discussions-bot/blacklist.json', 'r'))
username = settings['username']
password = settings['password']

# Log in to Wikia network
session = core.login('community', username, password)

def test_content(wiki_name, wiki_id, post, triggers):
    for trigger in triggers:
        if trigger in post['rawContent']:
            session.put('https://services.wikia.com/discussion/'+str(wiki_id)+'/posts/'+post['id']+'/delete', headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
            print('Deleted: https://'+wiki_name+'.wikia.com/d/p/'+post['threadId']+'/r/'+post['id'])
            # post is already deleted, no reason to check for further validations
            return


for wiki in blacklist['wikis']:
    #TODO: store last post epoch timer, don't depend on system timer.
    payload = {'limit': '25', 'page': '0', 'responseGroup': 'small', 'reported': 'false', 'viewableOnly': 'true'}
    r = session.get('https://services.wikia.com/discussion/'+str(wiki['cityid'])+'/posts', params=payload, headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
    # Error logging
    if r.status_code is not 200:
        print("HTTP status: " + str(r.status_code) + " (" + wiki['name'] + ")")

    for post in r.json()['_embedded']['doc:posts']:
        if int(post['creationDate']['epochSecond']) > ts - update_interval:
            test_content(wiki['name'], wiki['cityid'], post, wiki['triggers'])
