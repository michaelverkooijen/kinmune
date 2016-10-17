#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']
is_mod = settings['isMod']

# Log in to Wikia network
session = core.login(wiki, username, password)

print(core.is_logged_in(session, username, wiki))

wiki_id = core.get_wiki_id(session, wiki)
print(wiki_id)

def get_threads(page):
    payload = {'limit': '25', 'forumId': '2854567542842721975', 'page': str(page)}
    r = session.get('https://services.wikia.com/discussion/'+wiki_id+'/threads', params=payload, headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
    decoded_json = r.json()
    for post in decoded_json['_embedded']['threads']:
        print(post['id'])
        r = session.put('https://services.wikia.com/discussion/'+wiki_id+'/threads/' + post['id'] + "/lock", headers={'Accept': 'application/hal+json', 'user-agent': 'Flightmare/bot'})
        print(r.text)

    #if decoded_json['_links']['self']['href'] is not decoded_json['_links']['last']['href']:
    if page is not 7:
        get_threads(page + 1)

get_threads(0)
