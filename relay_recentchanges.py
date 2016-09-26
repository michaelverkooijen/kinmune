#!/usr/bin/env python3
import core
import os
import requests
import json
import sys
from difflib import Differ, SequenceMatcher
from datetime import datetime, timedelta
from slackclient import SlackClient

d = Differ()
ts = datetime.utcnow() - timedelta(minutes=-5)
headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'user-agent': 'Flightmare/bot'}

# load settings.json
settings = json.load(open(os.environ['HOME']+'/.discussions-bot/settings.json', 'r'))
wiki = settings['wiki']
username = settings['username']
password = settings['password']

slack_client = SlackClient(settings['slackToken'])

# Log in to Wikia network
session = core.login(wiki, username, password)

print (ts.strftime('%Y%m%d%H%M%S'))

# TODO: reverse list, put all diffs in tuples and output the longest one!
def get_revisions(rcstart=None):
    payload = {'action': 'query', 'list': 'recentchanges', 'rcshow': 'anon', 'rcnamespace': '0', 'rcprop': 'title|ids|sizes|timestamp|user', 'rcstart': rcstart, 'rcend': ts.strftime('%Y%m%d%H%M%S'), 'format': 'json'}
    decoded_json = session.get('https://'+wiki+'.wikia.com/api.php', params=payload, headers=headers).json()

    for revision in decoded_json['query']['recentchanges']:
        payload = {'action': 'raw', 'oldid': revision['revid']}
        body_new = session.get('https://'+wiki+'.wikia.com/wiki/'+revision['title'], params=payload, headers=headers).text.splitlines()

        payload = {'action': 'raw', 'oldid': revision['old_revid']}
        body_old = session.get('https://'+wiki+'.wikia.com/wiki/'+revision['title'], params=payload, headers=headers).text.splitlines()

        # diff both pages
        result = list(d.compare(body_old, body_new))

        # fetch first difference
        line_left = ''
        line_right = ''
        done = False
        for line in result:
            if not done and line.startswith('-'):
                line_left = line[2:]
                done = True
        done = False
        for line in result:
            if not done and line.startswith('+'):
                line_right = line[2:]
                done = True

        sm = SequenceMatcher(None, line_left, line_right)
        output= []
        for opcode, a0, a1, b0, b1 in sm.get_opcodes():
            if opcode == 'equal':
                output.append(sm.a[a0:a1])
            elif opcode == 'insert':
                output.append("*" + sm.b[b0:b1] + "*")
            elif opcode == 'delete':
                output.append("~" + sm.a[a0:a1] + "~")
            elif opcode == 'replace':
                output.append("*" + sm.b[b0:b1] + "*")
        text = ''.join(output)

        message = revision['title'] + " *(" + str(revision['newlen'] - revision['oldlen']) + ")* — " + text + " — <https://" + wiki + ".wikia.com/wiki/Special:Contributions/" + revision['user'] + "|" + revision['user'] + ">"
        slack_client.api_call("chat.postMessage", channel="recent-changes", text=message, as_user=True)
        #print(message)

    if 'query-continue' in decoded_json:
        return get_revisions(decoded_json['query-continue']['recentchanges']['rcstart'])

get_revisions()
