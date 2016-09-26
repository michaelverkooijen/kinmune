#!/usr/bin/env python3
import requests
import json
from urllib.parse import quote

# TODO: suspend session instead of logging in
# TODO: make module, return session
headers = {'Connection': 'Keep alive', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Flightmare/bot'}

# TODO: Log in to Community Central to avoid SSL Certificate errors.
def login(wiki, username, password):
    session = requests.Session()
    payload = {'action': 'login', 'lgname': username, 'lgpassword': password, 'format': 'json'}
    r = session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers)
    payload['lgtoken'] = r.json()['login']['token']
    r = session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers)
    # print(r.json()['login']['result'])
    # TODO: test for login failures
    return session

# bool: true if logged in as provided user, false for other user or anon
def is_logged_in(session, username, wiki):
    payload = {'action': 'query', 'meta': 'userinfo', 'format': 'json'}
    r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload, headers=headers)
    return r.json()['query']['userinfo']['name'] == username

def get_edit_token(session, wiki):
    payload = {'action': 'query', 'prop': 'info', 'intoken': 'edit', 'titles': '#', 'format': 'json'}
    r = session.post('https://'+wiki+'.wikia.com/api.php', data=payload, headers=headers)
    return r.json()['query']['pages']['-1']['edittoken']

def get_wiki_id(session, wiki):
    payload = {'action': 'query', 'meta': 'siteinfo', 'siprop': 'wikidesc', 'format': 'json'}
    r = session.get('https://'+wiki+'.wikia.com/api.php', params=payload, headers=headers)
    return r.json()['query']['wikidesc']['id']
