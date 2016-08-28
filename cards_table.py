#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote
import sys
import re

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']

# Log in to Wikia network
session = core.login(wiki, username, password)

print(core.is_logged_in(session, username, wiki))

wiki_id = core.get_wiki_id(session, wiki)
edit_token = core.get_edit_token(session, wiki)

payload = {'action': 'query', 'list': 'categorymembers', 'cmtitle': 'Category:Legends: Endurance', 'cmnamespace': '0', 'cmlimit': '5000', 'format': 'json'}
r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload)

for page in r.json()['query']['categorymembers']:
    #sys.stdout.buffer.write((page['title']).encode('utf-8'))

    # get page contents
    payload = {'action': 'raw'}
    body = session.get('https://'+wiki+'.wikia.com/wiki/'+page['title'], params=payload).text

    # clear dictionary for every pages
    dictionary = {'title': page['title'], 'unique': 'No', 'text': ''} #fallback title in case there is no title in the infobox

    for line in body.splitlines():
        data = re.search(r'\s*\|([a-z]+)\s*=\s*(.*)', line)

        if data:
            dictionary[data.group(1)] = data.group(2)

    print('|-')
    if page['title'] is not dictionary['title']:
        print('| [[' + page['title'] + '|' + dictionary['title'] + ']]')
    else:
        print('| [[' + page['title'] + ']]')
    print('| ' + dictionary['cost'])
    print('| ' + dictionary['attack'])
    print('| ' + dictionary['health'])
    #print('| ' + dictionary['set']) TODO: enable when expension packs happen?
    print('| ' + dictionary['type'])
    print('| ' + dictionary['subtype'])
    print('| ' + dictionary['rarity'])
    print('| ' + dictionary['unique'])
    print('| ' + dictionary['text'])
