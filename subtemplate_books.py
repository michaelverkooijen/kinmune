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
edit_token = core.get_edit_token(session, wiki)
print(edit_token)

payload = {'action': 'query', 'list': 'embeddedin', 'eititle': 'Template:Book', 'eilimit': '5000', 'format': 'json'}
r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload)
print(r.url)

#TODO: implement continue from articleID in case of resuming after emergency quit
for page in r.json()['query']['embeddedin']:
    #sys.stdout.buffer.write((page['title']).encode('utf-8'))

    # get page contents
    payload = {'action': 'raw'}
    body = session.get('https://'+wiki+'.wikia.com/wiki/'+page['title'], params=payload).text

    game = 'ERROR'
    new_body = ''
    in_gallery = False
    page_number = 1
    in_nested = False
    nested_regex = re.compile('\s*\|[a-z]+\s*=\s*\{\{[Bb]ook/game')
    bracket_count = 0

    # Searches for <gallery type="slideshow" widths="250"> or <gallery type="slideshow"  widths="250" position="center">
    # Some pages have galleries without images, skip these!
    for line in body.splitlines():
        if '</gallery>' in line:
            in_gallery = False

        if in_gallery:
            if '|' not in line:
                line = line + '|Cover ' + str(page_number)
                page_number = page_number + 1

        if '<gallery type="slideshow" widths="250">' in line:
            if '</gallery>' not in line:
                in_gallery = True
                line = '|image = <gallery>'

        if '<gallery type="slideshow" widths="250" position="center">' in line:
            if '</gallery>' not in line:
                in_gallery = True
                line = '|image = <gallery>'

        if not in_nested and not nested_regex.match(line):
            new_body = new_body + line + '\n'

        ########################################################################
        #FIXME: edge case: }}}}{{Main|...
        if in_nested:
            #print(line)
            bracket_count = bracket_count + line.count('{')
            bracket_count = bracket_count - line.count('}')
            data = re.search(r'\s*\|([a-z]+)\s*=\s*(.*)', line)
            if bracket_count < 1:
                in_nested = False

            if data:
                data_name = data.group(1)
                data_value = data.group(2)
                if bracket_count < 1:
                    data_value = data_value[:-2]

                if data_name == 'skill' or data_name == 'weight' or data_name == 'value' or data_name == 'id':
                    #print('|' + game + '/' + data_name + "=" + data_value)
                    new_body = new_body + '|' + game + '/' + data_name + "=" + data_value + '\n'

            #BEFORE OR AFTER? TEST BRACKETS Line can be just }}, If explode result <2 strings break?
            #count brackets first if <1 in_nested = False && insert brackets until bracket_count==0
            #explode line, add line constructed from |game/left=right WHEN left equals skill/weight/value/id

        if nested_regex.match(line):
            #print('SUBTEMPLATE FOUND IN:' + page['title'])
            in_nested = True
            bracket_count = 2
            game = re.search(r'\s*\|([a-z]+)\s*=\s*\{\{[Bb]ook/game', line).group(1)
            new_body = new_body + '|' + game + '/lead=1\n'

    #sys.stdout.buffer.write((new_body).encode('utf-8'))

    payload = {'action': 'edit', 'title': page['title'], 'summary': 'Nested template removal', 'bot': '1', 'watchlist': 'nochange', 'format': 'json', 'text': new_body, 'token': edit_token}
    print(session.post('http://'+wiki+'.wikia.com/api.php', data=payload, headers=headers).text)
