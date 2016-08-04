#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
print(os.environ['HOME'])
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']
is_mod = settings['isMod']
print(username)

# Log in to Wikia network
session = core.login(wiki, username, password)

print(core.is_logged_in(session, username, wiki))

wiki_id = core.get_wiki_id(session, wiki)
print(wiki_id)


payload = {'limit': '25', 'page': '0', 'responseGroup': 'small', 'reported': 'false', 'viewableOnly': 'true'}
r = session.get('https://services.wikia.com/discussion/'+wiki_id+'/posts', params=payload, headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
for post in r.json()['_embedded']['doc:posts']:
    print(post['rawContent'])

    if 'new' in post['rawContent']:
        r = session.put('https://services.wikia.com/discussion/'+wiki_id+'/posts/' + post['id'] + "/delete", headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
        print(r.text)
