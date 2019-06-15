from twitter import *
import requests

from secret import *
import settings

from datetime import datetime
import json, time, os, sys

# Settings determine whether to download media or not
INCLUDE_MEDIA = settings.INCLUDE_MEDIA_IN_TWEET_DOWNLOAD
ACCOUNTS_FILE = settings.TWITTER_ACCOUNTS_FILE

# Initialize authorization with the Twitter API
def init():
    # Fill out a secret.py with these keys for your Twitter app
    b_token = oauth2_dance(consumer_key, consumer_secret)
    return Twitter(auth=OAuth2(bearer_token=b_token))

# Downloads media files into downloaded_tweets_and_media/[user]/media/
# under [tweet id]_[0|1|2|...].[jpg|mp4] for each media piece in the tweet
# Note: only extracts media one Quote deep
def download_media(tweet, t_id, folder):
    media_pieces = []

    # Add media from quoted tweet
    if tweet['is_quote_status'] == True:
        if ('quoted_status' in tweet) and ('extended_entities' in tweet['quoted_status']):
            media_pieces.extend(tweet['quoted_status']['extended_entities']['media'])

    # Add media from original tweet
    if 'extended_entities' in tweet:
        media_pieces.extend(tweet['extended_entities']['media'])

    for i, media in enumerate(media_pieces):
        url = ''
        ext = ''
        if media['type'] == 'photo':
            url = media['media_url']
            ext = '.jpg'
        elif media['type'] == 'animated_gif':
            url = media['video_info']['variants'][0]['url']
            ext = '.mp4'
        elif media['type'] == 'video':
            best_bitrate = 0
            ext = '.mp4'
            # download the best quality video
            for version in media['video_info']['variants']:
                if version['content_type'] == 'video/mp4' and version['bitrate'] > best_bitrate:
                    best_bitrate = version['bitrate']
            for version in media['video_info']['variants']:
                if 'bitrate' in version and version['bitrate'] == best_bitrate:
                    url = version['url']

        img_data = requests.get(url).content
        with open(folder+t_id+'_'+str(i)+ext, 'wb') as handler:
            handler.write(img_data)

# returns an array of the last 3200 tweets posted by user
def all_tweets(t, user, media_fold_path):
    user_tweets = []
    latest_id = -1
    collected_ids = {}

    # tweet collection
    while(1):

        try:
            args = {'exclude_replies': 'false',
                    'include_rts': 'true',
                    'trim_user': 'true',
                    'count': 200,
                    'tweet_mode': 'extended',
                    'screen_name': user}
            if latest_id > -1:
                args['max_id'] = latest_id

            query = t.statuses.user_timeline(**args)
        except Exception as err:
            # Trying to scrape a private account
            if err.e.code == 401:
                unauth = {'error': True,
                          'error_data': 'This app is not authorized to download this user\'s tweets. ' + \
                                        'The user\'s account may be private.'}
                user_tweets.append(unauth)
                break
            # Rate limited
            elif err.e.code == 429:
                # note: this could be handled more elegantly, but I could
                # never hit the rate limit to test it
                time.sleep(10)
                continue
            else:
                print("Query error: ", err.e.code)
                continue

        # break the loop when the API stops returning tweets (reached max 3200)
        if not query:
            break

        latest_id = query[-1]['id'] - 1

        for tweet in query:
            if tweet['id'] not in collected_ids:
                user_tweets.append(tweet)
                collected_ids[tweet['id']] = 1

                if INCLUDE_MEDIA:
                    download_media(tweet, str(tweet['id']), media_fold_path)
    return user_tweets


# Download tweets from every user in ACCOUNTS_FILE
def write_tweets(t):
    collection_folder = 'downloaded_tweets/'
    media_fold = '_media/'
    is_ids = False

    # create the folder that will hold everything
    if not os.path.exists(collection_folder):
        os.makedirs(collection_folder)

    # get the list of Twitter users to scrape
    f = open(ACCOUNTS_FILE, 'r')
    t_users_dict = json.load(f)
    f.close()
    t_users = t_users_dict['users']
    if t_users_dict['type'] == 'id':
        is_ids = True

    for user in t_users:
        # get the Twitter User object
        if is_ids:
            user_obj = t.users.show(user_id=user)
            user = user_obj['screen_name']
        else:
            user_obj = t.users.show(screen_name=user)

        # create optional <user>_media folder
        if INCLUDE_MEDIA:
            if not os.path.exists(collection_folder+user+media_fold):
                os.makedirs(collection_folder+user+media_fold)


        # get the tweets (max 3200)
        user_tweets = all_tweets(t, user, collection_folder+user+media_fold)
        whole_obj = {'tweets': user_tweets, 'user_object': user_obj}
        
        # write the tweets to file
        tweet_file = open(collection_folder+user+'.json', 'w+')
        json.dump(whole_obj, tweet_file)
        tweet_file.close()


if __name__ == "__main__":
    t = init()
    write_tweets(t)

