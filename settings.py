# --------- Scrape Twitter Follows Settings --------- #
TWITTER_USER_SCRAPE_FOLLOWS = "BarackObama"

# --------- Tweet Scraper Settings --------- #
INCLUDE_MEDIA_IN_TWEET_DOWNLOAD = False

# Uncomment ONE of the following to choose which set of users the tweet scraper
#  will scrape from

TWITTER_ACCOUNTS_FILE = 'resources/twitter_accounts_top_050.json'
# TWITTER_ACCOUNTS_FILE = 'resources/[TWITTER_USER]_follows.json'
# TWITTER_ACCOUNTS_FILE = 'path/to/alternate/file.json'

# --------- Compressor Settings --------- #
COMPRESSOR_WRITE_TIMING_FILES = True
COMPRESSOR_WRITE_COMPRESSED_FILES = False
COMPRESSOR_DELETE_UNCOMPRESSED_FILES = False

# --------- Decompressor Settings --------- #
DECOMPRESSOR_DELETE_COMPRESSED_FILES = False
