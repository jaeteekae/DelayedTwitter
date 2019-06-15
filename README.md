# DelayedTwitter

This is the project code for a paper that analyzes how the brotli and zstandard compression methods can be used with time delays to make Twitter more accessible for users with a lower bandwidth.

### Table of Contents:
 - [Setup](#setup)
 - [Compile a list of Twitter users](#compile)
 - [Scrape tweets](#scrape)
 - [Compression](#compress)
 - [Decompression](#decompress)
 - [Analyze scraped tweets](#analyze)
 
<a name="setup"/>

## Setup

In order to use the scripts, which use the Twitter API, the `secret.py` file needs to be filled out with the authentication information for a Twitter Developer App. An app can be [created here](https://developer.twitter.com/en/apps).

Additionally, run this command before running any scripts:
```
$ pip install -r requirements.txt
```
to install all the required packages.

<a name="compile"/>

## Compile a list of Twitter users 
The tweet scraper needs a list of twitter users to scrape from. There are three options for compiling that list.
### Popular Twitter Accounts
Run the script: 
```
$ python get_top_twitter_accounts.py
```
to create a file `resources/twitter_accounts_top_050.json` that lists the fifty Twitter users with the most followers according to Wikipedia.

### Follows of a Specific Twitter Account
This script will compile a list of all users that a given user follows. To use, run:
```
$ python scrape_tw_follows.py [twitter_handle]
```
where `twitter_handle` is the handle of the user whose follows you want to scrape. If no `twitter_handle` is provided, the script will use the `TWITTER_USER_SCRAPE_FOLLOWS` variable found in `settings.py`.

When the script is run, it creates a file `resources/<twitter_handle>_follows.json` listing the 5000 most recent users that @<twitter_handle> followed.

This script will not work if @<twitter_handle> is a private account, in which case the next option might work.
### Follows of an Account via an HTML file
If you want to scrape the follows from an account that 1. is private and 2. you have the login credentials for, this option will work.

Login to the Twitter account and go to the page:
[https://twitter.com/<your_twitter_handle>/following](https://twitter.com/<put_your_handle_here>/following)
and keep scrolling to the bottom of the page until it stops loading new profile cards. Then save the page to disk as an .html file. Run the script:
```
$ python scrape_tw_follows_html.py <path/to/filename.html>
```
to create a file `resources/<filename>_follows.json` that lists all the follows from the .html page.

<a name="scrape"/>

## Scrape Tweets 

The scraper can be run with:
```
$ python dfs_twitter_scraper.py
```

It will choose the accounts to scrape from using `TWITTER_ACCOUNTS_FILE` variable in `settings.py`. The `INCLUDE_MEDIA_IN_TWEET_DOWNLOAD` variable in `settings.py` will determine whether the media associated with the tweets (pictures, videos, or gifs) will be downloaded along with the text of the tweets (Note that the size of the download can increase over 200x by including media, i.e. 220MB to 57GB). The scraper will download in a depth-first manner.

For every Twitter account listed in the `TWITTER_ACCOUNTS_FILE`, the scraper will download a `<twitter_handle>.json` file into the `downloaded_tweets/` folder. The file will contain a dictionary with two keys:

 - "user_object" : the account's Twitter user object 
 - "tweets" : an array of tweets

The tweet array will only have the 3,200 most recent tweets by the user because of restrictions by the Twitter API.

If `INCLUDE_MEDIA...` is set to True, each Twitter account will have a corresponding `downloaded_tweets/<twitter_handle>_media/` folder created to hold the media. Each piece of media will be named `<tweet_id_number>_<media#>.(jpg|mp4)` (zero-indexed). So the second piece of corresponding media downloaded from the tweet with the id# 105513889 might be named `105513889_1.jpg`.

<a name="compress"/>

## Compression 
The compressor traverses through the `downloaded_tweets` folder and compresses all the JSON files into the specified format. The usage is:
```sh
$ python compressor.py (brotli|zstd) <compression_level> [path_to_dictionary]
```
The brotli format supports compression levels from 1 (least compressed) to 11 (most compressed), and the compressed files have the .br file extension. 

The zstandard format supports compression levels from 1 to 22 (most compressed), and the compressed files have the .zst file extension. Zstandard optionally uses a dictionary to compress the data. If a dictionary is used for compression, the same dictionary must be used for decompression.

The `settings.py` file has compression options for:
  - Writing the compressed files to disk
  - Deleting the original JSON files
  - Creating a data file that lists for every compressed JSON file:
  -- Starting & ending file sizes (bytes)
  -- Time to compress (seconds)
  -- Compression ratio
  -- Compression speed (MBps)

<a name="decompress"/>

## Decompression 
The decompressor traverses through the `downloaded_tweets` folder and decompresses all of the requested files to JSON. The usage is:
```sh
$ python decompressor.py [brotli|zstd] [path_to_dictionary]
```
When run with no arguments, the decompressor will decompress any file with the .br or .zst file extention into a .json file. When run with the `brotli` argument, it will only decompress .br files. When run with the `zstd` argument, it will only decompress .zst files (using a dictionary, if provided).
When run with just a path to a dictionary, it will decompress all files, but it will decompress the .zst files using the dictionary.

The `settings.py` file has an option for deleting the compressed files after they have been decompressed.

<a name="analyze"/>

## Analyze Scraped Tweets 
After downloading (and compressing) tweets, there are some scripts available to make the data more easily consumable. To use, run:
```
$ python analysis.py (tweet_size_data|merge_speed|merge_ratio|merge_sizing)
```
While `tweet_size_data` only uses the `downloaded_tweets` data to run, the `merge` options are only useful if there are multiple compression timing files (of different compression levels) for a single compression algorithm. For example, an `analysis` folder that looks like:
```
analysis
├── zstandard_1_compression_timing.csv
├── zstandard_9_compression_timing.csv
├── zstandard_15_compression_timing.csv
```
or
```
analysis
├── zstandard_7_compression_timing.csv
├── zstandard_11_compression_timing.csv
├── brotli_6_compression_timing.csv
├── brotli_9_compression_timing.csv
```
will get interesting results, but an `analysis` folder that looks like:
```
analysis
├── zstandard_1_compression_timing.csv
├── brotli_3_compression_timing.csv
```
will not get interesting results.

### Tweet Size Data
Traverses the `downloaded_tweets` folder to create an `analysis/tweet_sizes.csv` file. The spreadsheet has one row for every Twitter user with a JSON file in `downloaded_tweets`. A row lists the user's:

 - Summed size of all collected tweets (in bytes)
 - Total # of tweets
 - Avg tweet size, min tweet size, max tweet size (bytes)
 - Twitter User Object size (bytes)

### Merge Sizing
The `merge_sizing` option creates a `<compression_algo>_sizing.csv` file for every distinct compression algorithm found in the `analysis` folder. The file will list for each compression level:
 - Total time elapsed during compression (sec)
 - Summed size (in bytes) of all files pre-compression
 - Summed size (in bytes) of all files post-compression for that compression level
 - Compression ratio (start size ÷ end size)
 
 For example, a `brotli_sizing.csv` file might look like:
```
Level,Elapsed Time(sec),Starting Size (sum),Ending Size (sum),Ratio,Compression Rate (Mbps)
1,45.14965,8859342373,1095044218,8.09039692404,187.131622978
2,67.895273,8859342373,1066110605,8.30996552464,124.440581915
3,74.010295,8859342373,962750153,9.20211993256,114.158811033
```

### Merge Ratio
The `merge_ratio` option creates a `<compression_algo>_ratio.csv` file for every distinct compression algorithm found in the `analysis` folder. The file lists the compression ratio achieved for every individual JSON file in `downloaded_tweets` at each level of compression.

For example, a `brotli_ratio.csv` file might look like:
```
Twitter Handle,Level 4,Level 7,Level 9
BarackObama,11.096364316,12.6569405488,12.8690585438
...
```
### Merge Speed
The `merge_speed` option creates a `<compression_algo>_speed.csv` file for every distinct compression algorithm found in the `analysis` folder. The file lists the compression speed (MBps) achieved for every individual JSON file in `downloaded_tweets` at each level of compression.
For example, a `zstandard_speed.csv` file might look like:
```
Twitter Handle,Level 4,Level 7,Level 9
BarackObama,302.130320164,92.4748581801,68.1657526478
...
```

