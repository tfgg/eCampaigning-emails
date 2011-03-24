from sqlalchemy import *

# Create the database engine
db = create_engine('sqlite:////home2/fairsay/duane-scripts/aafeeds/aafeeds.sqlite')

db.echo = False  # Try changing this to True and see what happens

metadata = MetaData(db)

emailindex = Table('EmailIndex', metadata, autoload=True)

# Insert data into table
i = emailindex.insert()
emailindexdata = {'EmailMessageID': '2', 'EmailMailer': 'Outlook'}

i.execute(emailindexdata)




