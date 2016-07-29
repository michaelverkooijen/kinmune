#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote
import sys

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

payload = {'action': 'query', 'list': 'embeddedin', 'eititle': 'Template:OblivionBooks', 'eilimit': '5000', 'format': 'json'}
r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload)
print(r.url)

#FIXME: not compatible with articles over 8k in size due to not using multi-part uploads.
#TODO: implement continue from articleID in case of resuming after emergency quit
for page in r.json()['query']['embeddedin']:
    #sys.stdout.buffer.write((page['title']).encode('utf-8'))

    # get page contents
    payload = {'action': 'raw'}
    body = session.get('https://'+wiki+'.wikia.com/wiki/'+page['title'], params=payload).text

    new_body = ''
    in_gallery = False
    page_number = 1

    # Searches for <gallery type="slideshow" widths="250"> or <gallery type="slideshow"  widths="250" position="center">
    # Some pages have galleries without images, skip these!
    for line in body.splitlines():
        if '</gallery>' in line:
            in_gallery = False

        if in_gallery:
            if '|' not in line:
                line = line + '|Page ' + str(page_number)
                page_number = page_number + 1

        if '<gallery type="slideshow" widths="250">' in line:
            if '</gallery>' not in line:
                in_gallery = True
                line = '|image = <gallery>'

        if '<gallery type="slideshow" widths="250" position="center">' in line:
            if '</gallery>' not in line:
                in_gallery = True
                line = '|image = <gallery>'

        new_body = new_body + line + '\n'

    #sys.stdout.buffer.write((new_body).encode('utf-8'))

    #TODO: test body size, break if over 8k.
    if body is not new_body:
        payload = {'action': 'edit', 'title': page['title'], 'summary': 'PI Gallery fix', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'text': new_body, 'token': edit_token}
        print(session.post('http://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
