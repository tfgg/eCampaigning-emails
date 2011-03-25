import sqlite3
import json
from collections import Counter
import urllib2
import sys
import time

#print "Loading words"
#words = json.loads(open('/Users/tim/news/news/ngram/merged.json').read())

def opencalais(doc):
  url = "http://api.opencalais.com/tag/rs/enrich"
  headers = {'x-calais-licenseID': 'gymjcqhavxmfqx6gsg6r38he',
             'content-type': 'text/raw',
             'accept': 'application/json',}
  request = urllib2.Request(url, doc, headers)
  f = urllib2.urlopen(request)
  data = json.loads(f.read())

  people = []
  for key in data.keys():
    if key != 'doc':
      #print data[key]
      if '_type' in data[key] and data[key]['_type'] == 'Person': 
        people.append(data[key]['name'])
  return people


print "Loading db"
i = sqlite3.connect('aafeeds.sqlite')

rs = i.execute("SELECT * FROM EmailIndex")

people_count = Counter()

total = 0
for r in rs:
  subject = r[10]
  body = r[16]

  print subject
  time.sleep(0.5)
  people = opencalais(body.encode('utf-8'))
  for person in people:
    people_count[person] += 1
  print people 
  total += 1

print people_count.most_common(10)

i.close()

