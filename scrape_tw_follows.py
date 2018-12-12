#
# scrape_tw_follows.py
# 
# USAGE:
# $ python scrape_tw_follows.py [twitter_handle]
#
# If no twitter_handle is provided, it takes the handle from
# settings.TWITTER_USER_SCRAPE_FOLLOWS in settings.py
# It creates a file:
#   resources/<twitter_handle>_follows.json
# which lists the 5000 most recent users that @<twitter_handle> followed
#

from twitter import *
from secret import *
import settings

import json, sys, os

# Initialize authorization with the Twitter API
def init():
    # Fill out a secret.py with these keys for your Twitter app
    b_token = oauth2_dance(consumer_key, consumer_secret)
    return Twitter(auth=OAuth2(bearer_token=b_token))

def get_followers(t, handle):
    users = []
    query = t.friends.ids(screen_name=handle)
    return query['ids']

def write_data(data, handle):
    fname = 'resources/' + handle + '_follows.json'
    newf = open(fname, 'w')
    json.dump(data, newf)
    newf.close()
    return fname

# Verify handle exists and it not set to private
def verify(t, handle):
    try:
        q = t.users.show(screen_name=handle)
    except:
        print('ERROR: Twitter user ' + handle + ' does not exist')
        return False

    if q['protected']:
        print('ERROR: Twitter user ' + handle + ' is protected.\nIf you have access to this account, try scrape_tw_follows_html.py')
        return False

    return True

def set_up():
    if not os.path.exists('resources/'):
        os.makedirs('resources/')

if __name__ == "__main__":
    set_up()
    t = init()

    if len(sys.argv) == 1:
        handle = settings.TWITTER_USER_SCRAPE_FOLLOWS
    else:
        handle = sys.argv[1]

    if not verify(t, handle):
        sys.exit(1)
        
    data = {}
    data['type'] = 'id'
    data['parent_user'] = handle

    data['users'] = get_followers(t, handle)
    fname = write_data(data, handle)
    print('SUCCESS: created ' + fname + '\n')


