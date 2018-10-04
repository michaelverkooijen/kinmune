#!/usr/bin/env python3
#wgAllowCopyUploads must be set to true
import core
import os
import requests
import json

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
    decoded_json = session.get('http://'+wiki+'.wikia.com/api.php', params=payload, headers=headers).json()

    for image in decoded_json['query']['allimages']:
        # get page contents
        payload = {'action': 'raw'}
        body = session.get('http://'+wiki+'.wikia.com/wiki/'+image['title'], params=payload).text

        payload = {'action': 'upload', 'filename': image['name'], 'url': image['url'], 'text': body, 'ignorewarnings': 1, 'watchlist': 'nochange', 'format': 'json', 'token': edit_token}
        result = session.post('https://'+dest_wiki+'.wikia.com/api.php', data=payload, headers=headers, verify=False)
        print(result.text)
        # if fail, retry once (connection isn't what it used to be)
        if 'error' in result.json():
            print("retrying...")
            result = session.post('https://'+dest_wiki+'.wikia.com/api.php', data=payload, headers=headers, verify=False)
            print(result.text)
            # still not done? Let user inspect manually
            if 'error' in result.json():
                print("ATTENTION REQUIRED: " + image['name'])

    if 'query-continue' in decoded_json:
        return get_images(decoded_json['query-continue']['allimages']['aifrom'])

    return

get_images()
