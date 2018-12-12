#
# get_top_twitter_accounts.py
#
# Usage:
# $ python get_top_twitter_accounts.py
#
# Creates a file:
#   resources/twitter_accounts_top_050.json
# which lists the 50 most followed Twitter users according to Wikipedia
#

import wikipedia
import json, os
from bs4 import BeautifulSoup

# Get the page with the 50 most followed Twitter accounts
def get_popular_accs():
    accs = []

    page = wikipedia.page(pageid='52247588')
    soup = BeautifulSoup(page.html(), 'html.parser')
    table = soup.find('table', attrs={'class':'wikitable sortable'})
    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 0:
            continue
        handle = cols[2].text.strip()[1:]
        accs.append(handle)

    accs.pop()
    return accs

def write_data(data):
    fname = 'resources/twitter_accounts_top_050.json'
    newf = open(fname, 'w')
    json.dump(data, newf)
    newf.close()
    return fname

def set_up():
    if not os.path.exists('resources/'):
        os.makedirs('resources/')

if __name__ == '__main__':
    set_up()
    
    data = {}
    data['type'] = 'handle'
    data['users'] = get_popular_accs()
    fname = write_data(data)
    print('SUCCESS: created ' + fname + '\n')

