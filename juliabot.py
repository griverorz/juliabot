# Retrieve latests questions from Julia
# Gonzalo

import requests
import json
import re
import pandas as pd
import tweepy
import sys
import getopt
import time


class questions(object):

    def __init__(self, tags, tdelta):
        self.tags = tags
        self.todate = int(time.time())
        self.fromdate = self.todate - tdelta
        self.raw = None
        self.data = None

    def __getitem__(self, key):
        return self.data[key]

    def get(self):
        payload = {'tagged': self.tags, 'site': 'stackoverflow', 
                   'fromdate': self.fromdate, 'todate': self.todate,
                   'sort': 'creation', 'order': 'desc'}
        url='https://api.stackexchange.com/2.2/questions'
        data = requests.get(url, params=payload).text
        self.raw = json.loads(data)
        

    def parse(self):

        def _clean_string(string):
            string = unicode(string).encode('utf-8')
            return re.sub('\n[ ]?', '', string)
        if len(self.raw['items']) > 0:
            self.data = [{'title': self.raw['items'][i]['title'],
                          'link': self.raw['items'][i]['link'],
                          'time': self.raw['items'][i]['creation_date']}
                         for i in xrange(len(self.raw))]


class tweet(object):

    def __init__(self, credentials, data):
        creds = pd.read_csv(credentials, header=None)
        auth = tweepy.OAuthHandler(creds.ix[0, 1], creds.ix[1, 1])
        auth.set_access_token(creds.ix[2, 1], creds.ix[3, 1])
        self.api = tweepy.API(auth)
        self.data = data.data
        self.tweets = None

    def __getitem__(self, key):
        return self.data[key]

    def create_tweets(self):
        def _shorten(string):
            if len(string) > 120:
                string = string[0:116] + '...'
            return(string)
        if self.data is not None:
            self.tweets = ['{0} {1} {2}'.format(_shorten(i['title']), i['link'])
                           for i in self.data]

    def publish(self, sleeptime):
        if self.tweets is None:
            print 'No tweet to publish'
        else:
            for i in self.tweets:
                try:
                    self.api.update_status(i)
                    print 'Status: "' + i[0:50] + '" succesfully tweeted'
                except tweepy.TweepError as e:
                    print e
                time.sleep(sleeptime)


def main(argv):
    tdelta = 3600
    tags = ('julia-lang',)
    publish = True
    try:
        opts, args = getopt.getopt(argv, 'c:m:t:n')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'juliabot.py -c <str> -t <int> -n'
            sys.exit()
        if opt == '-c':
            credentials = str(arg)
        if opt == '-t':
            tdelta = int(tdelta)
        if opt == '-n':
            publish = False
    data = questions(tags, tdelta)
    data.get()
    data.parse()

    tw = tweet(credentials, data)
    tw.create_tweets()
    if publish:
        tw.publish(1)
    else:
        if tw.tweets is not None:
            for i in tw.tweets:
                print i + '\n'
        else:
            print "No candidates"


if __name__ == "__main__":
    main(sys.argv[1:])
