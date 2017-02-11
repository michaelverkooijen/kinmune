#!/usr/bin/env python3
import core
import os
import requests
import json

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Flightmare/bot'}

# load settings.json
print(os.environ['HOME'])
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = 'elderscrolls'
username = settings['username']
password = settings['password']
is_mod = settings['isMod']
print(username)

# Log in to Wikia network
session = core.login(wiki, username, password)

print(core.is_logged_in(session, username, wiki))

wiki_id = core.get_wiki_id(session, wiki)
edit_token = core.get_edit_token(session, wiki)
print(edit_token)

#embeddedin for templates, backlinks for whatlinkshere, categorymembers for category
#TODO: auto detect above switch by detecting Template: and Category:

# payload = {'action': 'query', 'list': 'categorymembers', 'cmtitle': 'Category:Documentation Templates', 'cmlimit': '5000', 'format': 'json'}
payload = {'action': 'query', 'list': 'backlinks', 'bltitle': 'NPC Classes (Tribunal)', 'bllimit': '5000', 'format': 'json'}
r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload)
print(r.url)

for page in r.json()['query']['backlinks']:
    #print(page['title'])

    # get page contents
    payload = {'action': 'raw'}
    body = session.get('https://'+wiki+'.wikia.com/wiki/'+page['title'], params=payload).text

    body = body.replace('NPC Classes (Tribunal)', 'Character Classes (Tribunal)')
    payload = {'action': 'edit', 'title': page['title'], 'summary': 'NPC Classes &rarr; Character Classes', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'text': body, 'token': edit_token}
    print(session.post('http://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
