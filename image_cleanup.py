#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Flightmare/bot'}

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
edit_token = core.get_edit_token(session, wiki, 'User:'+username)
print(edit_token)

# Loops until all images are through
def get_images(aifrom=None):
    payload = {'action': 'query', 'list': 'allimages', 'aifrom': aifrom, 'ailimit': '5000', 'format': 'json'}
    decoded_json = session.get('https://'+wiki+'.wikia.com/api.php', params=payload, headers=headers).json()

    for image in decoded_json['query']['allimages']:
        print(image['title'])

    if 'query-continue' in decoded_json:
        return get_images(decoded_json['query-continue']['allimages']['aifrom'])

    return

get_images()
