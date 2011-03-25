# Script using SQLAlchemy to populate SQLite database and relevent tables for the Action Archive Feeds application
# Author: Duane Raymond to learn from (since I have minimal programming skills)
# Requires:
# - sqlalchemy: http://www.sqlalchemy.org/
# - pysqlite: http://pysqlite.org
# - pytz: http://pytz.sourceforge.net/
# - stripogram: http://www.zope.org/Members/chrisw/StripOGram
# - Python interface to Yahoo's Term Extraction: http://effbot.org/zone/yahoo-term-extraction.htm
# - pygooglechart: http://pygooglechart.slowchop.com/
# - BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
# - Consider: MailTrends: http://code.google.com/p/mail-trends/

from sqlalchemy import *
from sqlalchemy import select
import imaplib, email
from email.Header import decode_header
import datetime, time
import pytz # Note: Ensure pytz is installed
import stripogram # Note: Ensure html2text is installed
import urllib, urlparse
from BeautifulSoup import BeautifulSoup

from local_settings import emailuser, emailpass

# Create and the database engine
db = create_engine('sqlite:///aafeeds.sqlite')
db.echo = False  # Try changing this to True and see what happens

# Load the table schema
metadata = MetaData(db)
emailindex = Table('EmailIndex', metadata, autoload=True)

# Initialise starting values
emailindexdata = None
s = select([emailindex.c.EmailMessageID]) # Assign select to table instance
rs = s.execute()                          # Assign select execute / run
rows = rs.fetchall()                      # Assign fetch all rows

# Loop through rows to build Python List of EmailMessageIDs
messageids = []
for row in rows: 
    messageids = messageids + [str(row[0])]

#Email access details
emailsrvr = 'mail.webfaction.com'


# Connect to IMAP Folder
mailbox = imaplib.IMAP4(emailsrvr)
mailbox.login(emailuser,emailpass)
mailbox.select(readonly=1)
emailids = mailbox.search(None,'ALL')[1][0].split(' ')
emailcount = len(emailids)

# A Python interface to Yahoo's Term Extraction service:
# 
# "The Term Extraction Web Service provides a list of significant
# words or phrases extracted from a larger content."
# Source: http://effbot.org/zone/yahoo-term-extraction.htm
# UnicodeDecodeError Fixed based on: http://wiki.python.org/moin/UnicodeDecodeError
import urllib
import lxml.etree as ElementTree

appid = 'p.Ndw2LV34HuBKpqWFPmRoLGYvVWTney5WYCOkG3V5k3mEzeA0TqelNQpD5neA--'

URI = "http://api.search.yahoo.com"
URI = URI + "/ContentAnalysisService/V1/termExtraction"

def termExtraction(appid, context, query=None):
    d = dict(
        appid=appid,
        context=context.decode("utf-8","replace").encode("utf-8")
        )
    if query:
        d["query"] = query.encode("utf-8")
    result = []
    f = urllib.urlopen(URI, urllib.urlencode(d))
    for event, elem in ElementTree.iterparse(f):
        if elem.tag == "{urn:yahoo:cate}Result":
            result.append(elem.text)
    return result

# Fetch attributes from each email
for emailid in emailids:
    # CSO mailbox: Problem emails # 4558, 4559
    emailidstart = 0 #4559 # For limiting purposes
    emailidstop = 6000 # For limiting purposes
    if int(emailid) > emailidstart and int(emailid) < emailidstop: # for limiting purposes
        emailRaw = mailbox.fetch(emailid, '(RFC822)')
        print "Retreived email box #: " + emailid + '/' + str(emailcount)
        
        if isinstance(emailRaw[1][0], tuple):
           msg = email.message_from_string(emailRaw[1][0][1])
           
           if msg['message-id'] not in messageids:
               messageids = messageids + [msg['message-id']] # Add new message id to List
               print "# of message-ids: " + str(len(messageids))
               
               emailToCheck = email.Utils.parseaddr(msg['to'])[1][:8].lower().startswith('emailin.')         
               # Get values from Received header if it exists (deleted if email moved to IMAP from Outlook)
               if msg['received']:
                  receivedHeader = msg['received']
                  receivedFrom = receivedHeader[receivedHeader.find('from ')+5:receivedHeader.find(' ',receivedHeader.find('from ')+5)].lower()
                  receivedFor = receivedHeader[receivedHeader.find('for <')+5:receivedHeader.find('>',receivedHeader.find('for <'))].lower()
                  if emailToCheck: # We don't really need this if the 'To' address is correct
                     receivedFor = None
                     
                  # Date-Time Email was Received
                  DateTimeReceived = receivedHeader[receivedHeader.find('>; ')+3:]
                  utctimestampreceived = email.Utils.mktime_tz(email.Utils.parsedate_tz(DateTimeReceived))
                  utcdatereceived = datetime.datetime.fromtimestamp(utctimestampreceived, pytz.utc)
               else:
                  receivedHeader = None
                  receivedFor = None
                  utcdatereceived = None
                  # Get EmailProcessor from Message ID if there isn't a 'Received' header
                  receivedFrom = msg['message-id'][msg['message-id'].find('@')+1:-1].lower()
                  if receivedFrom.split('.') == 1:
                     receivedFrom = None

               # Date-Time Email was Sent
               DateTimeSent = msg['date']
               utctimestampsent = email.Utils.mktime_tz(email.Utils.parsedate_tz(DateTimeSent))
               utcdatesent = datetime.datetime.fromtimestamp(utctimestampsent, pytz.utc)

               # Determine value to use for EmailSubscribeUser
               if emailToCheck:
                  emailTo = email.Utils.parseaddr(msg['to'])[1].lower()
                  emailsubscribeuser = emailTo[:emailTo.find('@')]
               elif receivedFor:
                  emailsubscribeuser = receivedFor[:receivedFor.find('@')]
               else:
                  emailsubscribeuser = None

               # Get Message body parts
               emailTEXT = None
               emailHTML = None
               contenttype = [msg.get_content_type()]
               if msg.is_multipart():
                  parts = len(msg.get_payload())
                  part = 0
                  for msgpart in msg.get_payload():
                      contenttype += [msg.get_payload(part).get_content_type()]
                      msgparttype = msg.get_payload(part).get_content_type()
                      part += 1
                      payload = msgpart.get_payload(decode=True)
                      if msgparttype == 'text/plain':
                         emailTEXT = payload
                      elif msgparttype == 'text/html':
                         emailHTML = payload
               else:
                  payload = msg.get_payload(decode=True)
                  if contenttype[0] == 'text/plain':
                     emailTEXT = payload
                  elif contenttype[0] == 'text/html':
                     emailHTML = payload
                     
               # If not TEXT version exists, convert HTML version to TEXT
               if not emailTEXT:
                  if emailHTML:
                     emailTEXT = stripogram.html2text(emailHTML.decode("utf-8","replace").encode("utf-8")).lstrip()

               # Get Yahoo Term Extractor generated terms
               # Results in UnicodeDecodeError on some emails which can be ignored similar to this
               # http://code.djangoproject.com/attachment/ticket/1086/feeds.py.2.diff
               # or replace them similar to https://bugs.launchpad.net/gpodder/+bug/252506
               keywords = None
               if emailTEXT:
                  keywords = termExtraction(appid, emailTEXT)[-5:]
                  
               # Encode the emailTEXT and emailHTML for insertion into sqlite newer versions
               if emailTEXT:
                  emailTEXT = emailTEXT.decode('utf-8', 'replace')
               if emailHTML:
                  emailHTML = emailHTML.decode('utf-8', 'replace')

               # Parse-out links in the html
               seen = set( )
               emaillinks = []
               if emailHTML:
                  htmlSoup = BeautifulSoup(emailHTML)
                  for anchor in htmlSoup.fetch('a'):
                      url = anchor.get('href')
                      if url is None or url in seen: continue
                      seen.add(url)
                      pieces = urlparse.urlparse(url)
                      if pieces[0]=='http':
                         pieces = [piece.encode('utf-8') for piece in pieces]
                         emaillinks = emaillinks + [str(urlparse.urlunparse(pieces))]

               # Populate the data to append to emailindex table
               emailindexdata = {
               'EmailMessageID': msg['message-id'],
               'EmailFromName': decode_header(email.Utils.parseaddr(msg['from'])[0])[0][0].decode('utf-8', 'replace'),
               'EmailFromAddress': email.Utils.parseaddr(msg['from'])[1].lower(),
               'EmailToName': email.Utils.parseaddr(msg['to'])[0].decode('utf-8', 'replace'),
               'EmailToAddress': email.Utils.parseaddr(msg['to'])[1].lower(),
               'EmailForAddress': receivedFor,
               'EmailSubscribeUser': emailsubscribeuser,
               'EmailProcessor': receivedFrom,
               'EmailSentDateTime': utcdatesent,
               'EmailReceivedDateTime': utcdatereceived,
               'EmailSubject': decode_header(msg['subject'])[0][0].decode('utf-8', 'replace'),
               'EmailKeywords': str(keywords),
               'EmailLinks': str(emaillinks),
               'EmailMailer': msg['x-mailer'],
               'EmailMailbox': emailuser,
               'EmailMailboxID': int(emailid),
               'EmailBodyContentType': str(contenttype),
               'EmailKeys': str(msg.keys()),
               'EmailBodyTEXT': emailTEXT,
               'EmailBodyHTML': emailHTML,
               'EmailCharset': str(msg.get_charsets()),
               'EmailRawHeader': receivedHeader,
               'EmailRawAll': None,
               }

               # Insert data into table
               i = emailindex.insert()
               i.execute(emailindexdata)
               print "Inserted email box #: " + emailid + '/' + str(emailcount)
           else:
               print "Skipped email (msg id): " + emailid + '/' + str(emailcount)
        else:
            print "No email data?: " + emailid + '/' + str(emailcount)
    else:
        pass
        # print "Skipped email (msg num): " + emailid + '/' + str(emailcount)
else:
    print "EmailIndex Table Populated"

# Close and logout of IMAP mailbox connection
mailbox.close()
mailbox.logout()

# Close Database connection(s) and variables?
db.dispose() 
del db

# Close variables?
del emailindex
del emailindexdata
del messageids
del emailids
del emailRaw
del msg

