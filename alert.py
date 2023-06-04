# alert.py sends an email if changes are made to any of the subheadings
# on this website.

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

load_dotenv()

URL = 'https://www.eastlakecommons.org/pgAdHousing.aspx'
SUBHEADINGS = ['Houses for Sale', 'Houses for Rent', 'Apartments for Rent', 'Roomates Wanted'] #roomates [sic]
INTERESTED_SUBHEADINGS = ['Houses for Rent', 'Apartments for Rent']
INPUT_FILE = '/home/bragalotwill/Documents/elc_listing_alert/elc.txt'
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

site = requests.get(URL)
soup = BeautifulSoup(site.content)
text = list(filter(None, soup.get_text().split('\n')))
listings = [listitem.get_text() for listitem in soup.find_all('li')]
listing_headings = {}

# find what subheading the listing is under
for li in listings:
    i = 0
    li_index = [i for i, line in enumerate(text) if li in line][0]
    while (i < len(SUBHEADINGS) and li_index > text.index(SUBHEADINGS[i])):
        i += 1
    if i > 0:
        listing_headings[li] = SUBHEADINGS[i - 1]

interested_listings = []
for k, v in listing_headings.items():
    if v in INTERESTED_SUBHEADINGS:
        interested_listings += [v + ': ' + k + '\n']

alert = False
with open(INPUT_FILE, 'r') as f:
    lines = f.readlines()
    for li in interested_listings:
        if li not in lines:
            alert = True


with open(INPUT_FILE, 'w') as f:
    for li in interested_listings:
        f.write(li)

if (alert):
    print('Alerting...')
    msg = MIMEText(''.join(interested_listings))
    msg['Subject'] = 'New ELC listing'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.set_debuglevel(True)
        smtp_server.login(SENDER_EMAIL, PASSWORD)
        smtp_server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    
