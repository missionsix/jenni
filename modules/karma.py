#!/usr/bin/python
"""
karma.py - Karma module
Copyright 2012
    John Ryan
    Patrick Andrew
"""
import copy
import datetime
import operator
import pickle
import re
import time

twoseconds=datetime.timedelta(seconds=2)

# dict of channel/last person to talk that didn't say +1
LAST_NICK = dict()

class kdict(dict):

      db_file = 'karma.pkl'

      def __init__(self):
            print "Loading karma"
            # read python dict back from the file
            try:
                  pkl_file = open(self.db_file, 'rb')
                  self.__dict__  = pickle.load(pkl_file)
                  pkl_file.close()
            except IOError:
                  self.__dict__ = {}

            print '\tKarma DB loaded.'

      def __savekarma(self):
            # write python dict to a file
            output = open(self.db_file, 'wb')
            pickle.dump(self.__dict__, output)
            output.close()

      def __getitem__(self, key):
            try:
                  return self.__dict__[key]
            except KeyError:
                  return 0

      def __setitem__(self, key, value):
            try:
                  self.__dict__[key] += value
            except KeyError:
                  self.__dict__[key] = value

            self.__savekarma()

      def iteritems(self):
            return self.__dict__.iteritems()


KARMADICT = kdict()


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)


def plusplus(jenni, input):
    name = input.group(1).lstrip().rstrip()

    #print "name=%s, LAST_NICK=%s" % (name, LAST_NICK.get(input.sender, 'aaa'))

    if name == '' or not name or len(name) == 0:
        name = LAST_NICK.get(input.sender, 'ShazBot')

    #print "name=%s, LAST_NICK=%s" % (name, LAST_NICK.get(input.sender, 'aaa'))

    if name == input.nick:
        print "%s downvoting %s" % (input.nick, name)
        KARMADICT[name] = -1
    else:
        print "%s upvoting %s" % (input.nick, name)
        KARMADICT[name] = 1

    #notify(jenni,input.nick,"%s is now at %d karma." % (name, KARMADICT[name]))

plusplus.rule = r'\+1(.*)$'
plusplus.priority = 'low'


def minusminus(jenni, input):
    print "%s downvoting %s" % (input.nick, str(input))
    name = input.group(1).lstrip.rstrip()

    if name == '' or not name or len(name) == 0:
        name = LAST_NICK.get(input.sender, 'ShazBot')

    print "%s downvoting %s" % (input.nick, name)
    KARMADICT[name] = -1

    #notify(jenni,input.nick,"%s is now at %d karma." % (name, KARMADICT[name]))

#  else:
#    notify(jenni,input.nick,"Please wait until 5 minutes after %s." % datetime.datetime.fromtimestamp(float(status)))
minusminus.rule = r'-1 (.*)$'
minusminus.priority = 'low'


def askkarma(jenni, input):
    name=input.group(1).lstrip().rstrip() or input.nick
    jenni.say("%s is at %d karma." % (name, KARMADICT[name]))
askkarma.rule=r'\.karma(.*)'


def karmarank(jenni, input):
    sorted_karma = sorted(KARMADICT.iteritems(), key=operator.itemgetter(1))
    if len(sorted_karma) == 0:
          jenni.say('No karma history')
          return
    losers = sorted_karma[:3]
    winners = sorted_karma[-3:]
    msg1 = ''
    for x in winners:
        msg1="%s:%s   " % (x[0], x[1]) + msg1
    msg1 = "Winners: " + msg1
    msg2 = "Losers: "
    for x in losers:
        msg2+="%s:%s   " % (x[0], x[1])
    jenni.say(msg1)
    time.sleep(0.5)
    jenni.say(msg2)
karmarank.rule=r'\.rank$'


def whokarma(jenni, input):
      sorted_karma = sorted(KARMADICT.iteritems(), key=operator.itemgetter(1))
      if len(sorted_karma) == 0:
            jenni.say('No karma history')
            return
      msg = [ "%s: %d" % (x[0], x[1]) for x in sorted_karma ]
      print 'printing karma list'
      jenni.say(', '.join(msg))
whokarma.rule=r'\.stats$'


def lastnick(jenni, input):
    if not '+1' in input.group(0):
          if type(input.sender) != None:
                LAST_NICK[input.sender] = input.nick
lastnick.rule = r'.*'

