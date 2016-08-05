#!/usr/bin/env python3
import core
import os
import requests
import json
from urllib.parse import quote
from datetime import date, timedelta

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
edit_token = core.get_edit_token(session, wiki, 'User:'+username)
print(edit_token)

#get yesterday's date
yesterday = date.today() - timedelta(1)
filepath = os.environ['HOME'] + '/' + yesterday.strftime('%Y%m%d') + '.log'

#TODO: append link to this log to User:KINMUNE/chatlog
with open(filepath, 'r') as logfile:
    payload = {'action': 'edit', 'title': 'User:' + username + '/chatlog/' + yesterday.strftime('%Y%m%d'), 'summary': 'Uploading log', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'text': '{{../}}\n' + logfile.read(), 'token': edit_token}
    print(session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)

prepend_text = '*[[User:KINMUNE/chatlog/' + yesterday.strftime('%Y%m%d') + '|' + yesterday.strftime('%Y%m%d') + ']]\n'
payload = {'action': 'edit', 'title': 'User:' + username + '/chatlog/list', 'summary': 'Uploading log', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'prependtext': prepend_text, 'token': edit_token}
print(session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
