# Script using SQLAlchemy to create SQLite database and relevent tables for the Action Archive Feeds application
# Author: Duane Raymond to learn from (since I have minimal programming skills)
# Adapted: http://rmunn.com/sqlalchemy-tutorial/tutorial.html

from sqlalchemy import *

# Create the database engine
db = create_engine('sqlite:///aafeeds.sqlite')

db.echo = False  # Try changing this to True and see what happens

metadata = MetaData(db)

# Table to define extractable elements of emails
emailindex = Table('EmailIndex', metadata,
    Column('EmailMessageID', String, primary_key=True),
    Column('EmailFromName', String),
    Column('EmailFromAddress', String),
    Column('EmailToName', String),
    Column('EmailToAddress', String),
    Column('EmailForAddress', String),
    Column('EmailSubscribeUser', String),
    Column('EmailProcessor', String),
    Column('EmailSentDateTime', DateTime),
    Column('EmailReceivedDateTime', DateTime),
    Column('EmailSubject', String),
    Column('EmailKeywords', String),
    Column('EmailLinks', String),
    Column('EmailMailer', String),
    Column('EmailBodyContentType', String),
    Column('EmailKeys', String),
    Column('EmailBodyTEXT', CLOB),
    Column('EmailBodyHTML', CLOB),
    Column('EmailCharset', String),
    Column('EmailRawHeader', CLOB),
    Column('EmailRawAll', BLOB),
    Column('EmailMailbox', String),
    Column('EmailMailboxID', Numeric)
)
emailindex.create()

# Table to decribe nature of subscription
emailannotations = Table('EmailAnnotations', metadata,
    Column('EmailAnnotationTo', String, primary_key=True),
    Column('EmailAnnotationStatus', String),
    Column('EmailAnnotationOriginator', String),
    Column('EmailAnnotationFrom', String),
    Column('EmailAnnotationDate', String),
    Column('EmailAnnotationContentType', String),
    Column('EmailAnnotationFormatType', String),
    Column('EmailAnnotationAudienceType', String),
    Column('EmailAnnotationOrigin', String),
    Column('EmailAnnotationLang', String),
    Column('EmailAnnotationGeo', String),
    Column('EmailAnnotationThemes', String),
    Column('EmailAnnotationIssues', String),
    Column('EmailAnnotationFocus', String),
    Column('EmailAnnotationKeywords', String),
    Column('EmailAnnotationGivenName', String),
    Column('EmailAnnotationFamilyName', String),
    Column('EmailAnnotationUsername', String),
    Column('EmailAnnotationPassword', String)
)
emailannotations.create()


# Table to describe transformations to normalise the EmailIndex table data before processing
emailtransform = Table('EmailTransforms', metadata,
    Column('EmailTransformFindWhatA', String),
    Column('EmailTransformFindWhereA', String),
    Column('EmailTransformFindWhatB', String),
    Column('EmailTransformFindWhereB', String),
    Column('EmailTransformReplaceWithWhat', String),
    Column('EmailTransformReplaceWithWhere', String)
)
emailtransform.create()


# Table to define the Originator networks 
# e.g. Oxfam International oversees many Oxfams, GCAP oversees many national coalitions
originatornetworks = Table('OriginatorNetworks', metadata,
    Column('OriginatorNetworkName', String),
    Column('OriginatorNetworkType', String),
    Column('OriginatorNetworkGeoScope', String),
    Column('OriginatorNetworkThemes', String)
)
originatornetworks.create()


# Table to define the Originator network members
# e.g. Oxfam GB is a member of Oxfam International
originatoraffiliations = Table('OriginatorAffiliations', metadata,
    Column('OriginatorNetworkName', String),
    Column('OriginatorAffiliateName', String),
    Column('OriginatorAffiliateGeoScope', String),
    Column('OriginatorAffiliateThemes', String)
)
originatoraffiliations.create()

# Close Database connection(s)
db.dispose() 
del db
