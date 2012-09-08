#/usr/bin/python
"""
spotify.py - An api interface to spotify lookups
Copyright 2012
Patrick Andrew <missionsix@gmail.com>
"""

import httplib
import json
import sys

from datetime import timedelta


class NotModifiedError(Exception):
    def __init__(self):
        super(NotModifiedError, self).__init__(
            "The data hasn't changed since your last request.")

class ForbiddenError(Exception):
    def __init__(self):
        super(ForbiddenError, self).__init__(
            "The rate-limiting has kicked in.  Please try again later.")

class NotFoundException(LookupError):
    def __init__(self):
        super(NotFoundException, self).__init__(
            "Could not find that Spotify URI.")

class BadRequestException(LookupError):
    def __init__(self):
        super(BadRequestException, self).__init__(
            "The request was not understood.")

class InternalServerError(Exception):
    def __init__(self):
        super(InternalServerError, self).__init__(
            "The server encounted an unexpected problem.")

class ServiceUnavailable(Exception):
    def __init__(self):
        super(ServiceUnavailable, self).__init__(
            "The API is temporarily unavailable.")

SpotifyStatusCodes = {
    304: NotModifiedError,
    400: BadRequestException,
    403: ForbiddenError,
    404: NotFoundException,
    500: InternalServerError,
    503: ServiceUnavailable
    }


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
        try:
            raise SpotifyStatusCodes[resp.status]
        except ValueError:
            raise Exception("Unknown response from the Spotify API")


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)

def print_album(jenni, album):
    jenni.say(album['name'])
    jenni.say("   Artist: %s"% album['artist'])
    jenni.say("   Released: %s"%album['released'])

def print_artist(jenni, artist):
    jenni.say("Artist: %s" % artist['name'])

def print_track(jenni, track):
    length = str(timedelta(seconds=track['length']))[2:7]
    if length[0] == '0':
        length = length[1:]
    jenni.say("%s by %s" % (track['name'],track['artists'][0]['name']))
    jenni.say("   Length: %s" % length)
    jenni.say("   Album: \"%s\" " % track['album']['name'])


def query(jenni, input):
    spotify = Spotify()
    result = None
    try:
        result = spotify.lookup(input)
    except:
        e = sys.exec_info()[0]
        notify(jenni, input.nick, e)
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
        notify(jenni, input.nick, "Unknown response from API server")

query.rule = r'spotify:(.*)$'
query.priority = 'low'
