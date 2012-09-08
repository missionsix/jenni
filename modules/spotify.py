#/usr/bin/python
"""
spotify.py - An api interface to spotify lookups
Copyright 2012
Patrick Andrew <missionsix@gmail.com>
"""

import httplib
import json

from datetime import timedelta

class Spotify:

    base_url = "ws.spotify.com"
    service_url = '/lookup/1/.json'

    def __init__(self):
        self.conn = httplib.HTTPConnection(self.base_url)

    def __del__(self):
        self.conn.close()

    def lookup(self, uri, extras=None):
        
        lookup_url = "%s?uri=%s" % (self.service_url, uri)
        if extras is not None:
            lookup_url += "&extras=%s" % extras


        self.conn.request("GET", lookup_url)
        resp = self.conn.getresponse()
        if resp.status == 200:
            result = json.loads(resp.read())
            return result
        raise ValueError


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)

def print_album(jenni, album):
    jenni.say(album['name'])
    jenni.say("   Artist: %s"% album['artist'])
    jenni.say("   Released: %s"%album['released'])

def print_artist(jenni, artist):
    jenni.say("Artist: %s" % artist['name'])

def print_track(jenni, track):        
    jenni.say("%s by %s" % (track['name'],track['artists'][0]['name']))
    jenni.say("   Length: %s" % timedelta(seconds=track['length']))
    jenni.say("   Album: \"%s\" " % track['album']['name'])


def query(jenni, input):
    spotify = Spotify()
    result = None
    try:
        result = spotify.lookup(input)
    except ValueError:
        notify(jenni, input.nick, 'Sorry, I could not lookup %s at this time.' % input)
        return

    formatters = {
        'track': print_track,
        'album': print_album,
        'artist': print_artist
        }

    try:
        type = result['info']['type']
        formatters[type](jenni, result[type])
    except KeyError:
        jenni.say("Unknown response from Spotify API")

query.rule = r'spotify:(.*)$'
query.priority = 'low'
