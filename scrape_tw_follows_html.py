#
# scrape_tw_follows_html.py
#
# Usage:
#   $python scrape_tw_follows_html.py <path/to/filename.html>
#  
# filename.html MUST be a saved html page of this type:
#    https://twitter.com/<TW_HANDLE>/following
# where all of the follows have been loaded (by scrolling) before saving
#
# Creates a file:
#   resources/<filename>_follows.json
# listing all the followed users in <filename.html>
#

import json, sys, os
from bs4 import BeautifulSoup

def get_follows():
    users = []

    f = open(sys.argv[1], 'r')
    soup = BeautifulSoup(f.read(), 'html.parser')
    div = soup.find("div", {"class": "GridTimeline"})
    divs = div.find_all("b", class_="u-linkComplex-target")

    for u in divs:
        users.append(u.text)

    return users

def write_data(data):
    fname = 'resources/'+sys.argv[1][:-5]+'_follows.json'
    newf = open(fname, 'w')
    json.dump(data, newf)
    newf.close()
    return fname

def set_up():
    if not os.path.exists('resources/'):
        os.makedirs('resources/')

def validate(args):
    if (len(args) != 2) or (args[1][-5:] != ".html"):
        print("Usage:\n$python scrape_tw_follows_html.py path/to/filename.html\n")
        return False

    if not os.path.exists(args[1]):
        print('ERROR: Incorrect path given to html file\n')
        return False

    return True

if __name__ == '__main__':
    set_up()

    if not validate(sys.argv):
        sys.exit(1)

    data = {}
    data['type'] = 'handle'
    data['users'] = get_follows()
    fname = write_data(data)
    print('SUCCESS: created ' + fname + '\n')