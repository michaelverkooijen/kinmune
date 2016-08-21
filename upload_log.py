#!/usr/bin/env python3
import core
import os
import requests
import json
import sys
from urllib.parse import quote
from datetime import date, timedelta

headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

now_flag = '-now' in sys.argv

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']
is_mod = settings['isMod']

# Log in to Wikia network
session = core.login(wiki, username, password)

edit_token = core.get_edit_token(session, wiki, 'User:'+username)

if now_flag:
    day = date.today() #get today's date
else:
    day = date.today() - timedelta(1) #get yesterday's date

filepath = os.environ['HOME'] + '/' + day.strftime('%Y%m%d') + '.log'

with open(filepath, 'r') as logfile:
    payload = {'action': 'edit', 'title': 'User:' + username + '/chatlog/' + day.strftime('%Y%m%d'), 'summary': 'Uploading log', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'text': '{{../}}\n' + logfile.read(), 'token': edit_token}
    print(session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)

if not now_flag:
    prepend_text = '*[[User:KINMUNE/chatlog/' + day.strftime('%Y%m%d') + '|' + day.strftime('%Y%m%d') + ']]\n'
    payload = {'action': 'edit', 'title': 'User:' + username + '/chatlog/list', 'summary': 'Uploading log', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'prependtext': prepend_text, 'token': edit_token}
    print(session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
