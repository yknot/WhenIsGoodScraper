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
soup = BeautifulSoup(r.text, "html.parser")
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
            wday = a_dt.weekday() + 1
            if wday == 7:
                wday = 0
            key = (wday, a_dt.hour)
            events[key].append(person)

# headers
days = ['Sunday', 'Monday', 'Tuesday',
        'Wednesday', 'Thursday', 'Friday', 'Saturday']
print('{: <5}'.format(''), end="")
for d in days:
    print('{: <20}'.format(d), end='')
print()
print()

# get limits
min_hour = min(h for d, h in events.keys())
max_hour = max(h for d, h in events.keys())

# print out calendar
for hour in range(min_hour, max_hour + 1):
    print('{: <5}'.format(hour), end="")
    idx = 0
    while True:
        found = False
        if idx:
            print('{: <5}'.format(''), end="")
        for day in range(7):
            if (day, hour) in events and len(events[(day, hour)]) > idx:
                if len(events[(day, hour)]) - 1 > idx:
                    found = True
                print('{: <20}'.format(events[(day, hour)][idx]), end="")
            else:
                print('{: <20}'.format(''), end="")
        print()
        if not found:
            break
        idx += 1

    print('-' * (5 + 20 * 7))
