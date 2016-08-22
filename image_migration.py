#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']
is_mod = settings['isMod']
dest_wiki = settings['destWiki']

# Log in to Wikia network
session = core.login(wiki, username, password)

edit_token = core.get_edit_token(session, dest_wiki)
print(edit_token)

# Loops until all images are through
def get_images(aifrom=None):
    payload = {'action': 'query', 'list': 'allimages', 'aifrom': aifrom, 'ailimit': '5000', 'format': 'json'}
    decoded_json = session.get('https://'+wiki+'.wikia.com/api.php', params=payload, headers=headers).json()

    for image in decoded_json['query']['allimages']:
        payload = {'action': 'upload', 'filename': image['name'], 'url': image['url'], 'watchlist': 'nochange', 'format': 'json', 'token': edit_token}
        print(session.post('http://'+dest_wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
        print(image['name']+" DONE")

    if 'query-continue' in decoded_json:
        return get_images(decoded_json['query-continue']['allimages']['aifrom'])

    return

get_images()
