import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collections import defaultdict


# event and results codes as arguments
event_id = sys.argv[1]
response_code = sys.argv[2]

# get results page
r = requests.get('http://whenisgood.net/{}/results/{}'.format(event_id,
                                                              response_code))
soup = BeautifulSoup(r.text)
# get the script at the bottom
raw = soup.find_all('script')[-1].text.splitlines()
# filter out beginning and end rows
results = [r.strip() for r in raw if r.strip().startswith('r')]

# parse events
events = defaultdict(list)
person = ''
for r in results:
    # if a line with a name
    if '.name = ' in r:
        person = r[r.find('"') + 1:r.rfind('"')]
    # line with available times
    elif '.myCanDos = ' in r:
        # find the times
        available = r[r.find('"') + 1: r.find('"', r.find('"') + 1)]
        # convert to datetime and add to dict
        for a in available.split(','):
            a_dt = datetime.fromtimestamp(int(a) / 1000, timezone.utc)
            events[a_dt].append(person)
