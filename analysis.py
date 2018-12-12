#
#  analysis.py
#
# USAGE:
# $ python analysis.py (tweet_size_data|merge_speed|merge_ratio|merge_sizing)
#
# tweet_size_data: creates a file that lists (per user in the downloaded_tweets folder):
#   -Size of All Collected Tweets (in bytes)
#   -Total # of Tweets
#   -Avg Tweet Size, Min Tweet Size, Max Tweet Size
#   -User Object Size
#
# merge_speed|merge_ratio|merge_sizing: go to the README for an explanation of these
# 

import os, json, sys
from datetime import datetime
from collections import defaultdict

# Creates a file with detailed information about tweet data sizes for each Twitter user
def tw_data_by_user():
    new_f = 'analysis/tweet_sizes.csv'
    tweet_sizes_file = open(new_f, 'w+')
    tweet_sizes_file.write('Twitter Handle,Size of All Collected Tweets (in bytes),Total # of Tweets,Avg Tweet Size,Min Tweet Size,Max Tweet Size,User Object Size\n')

    workingdir = 'downloaded_tweets'

    for filename in os.listdir(workingdir):
        if filename.endswith('.json'):
            data_line = filename[:-5]

            tweet_file = os.path.join(workingdir, filename)
            twfile = open(tweet_file, 'r')

            alldata = json.load(twfile)
            twdata = alldata['tweets']
            usdata = alldata['user_object']

            twfile.close()

            # skip tweets that couldn't be scraped
            if (twdata==[]) or (usdata['protected']):
                continue

            # Size of collected tweets
            tw_size_sum = len(json.dumps(twdata))
            data_line += ','+str(tw_size_sum)

            # Total # of tweets
            num_total_tweets = len(twdata)
            data_line += ','+str(num_total_tweets)

            # Avg size of tweets
            avgsize = float(tw_size_sum)/num_total_tweets
            data_line += ','+str(avgsize)

            # Min & max sizes
            minsize = 999999
            maxsize = 0

            maxid = 0
            minid = 0

            for tweet in twdata:
                twsize = len(json.dumps(tweet))
                if twsize < minsize:
                    minsize = twsize
                    minid = tweet
                elif twsize > maxsize:
                    maxsize = twsize
                    maxid = tweet

            data_line += ','+str(minsize)
            data_line += ','+str(maxsize)

            # Size of Twitter user object
            usr_obj_size = len(json.dumps(usdata))
            data_line += ','+str(usr_obj_size)+'\n'

            tweet_sizes_file.write(data_line)


    tweet_sizes_file.close()
    return new_f

# Creates one merged file per compression method
def merge_files(arg):
    prefixes = ['brotli', 'zstandard', 'zstandard_dict', 'zstandard_pers_dict']
    new_fs = []

    for p in prefixes:
        x = write_data(p, arg)
        if x:
            new_fs.append(x)
    return new_fs

def write_data(prefix, arg):
    workingdir = 'analysis/'
    collection = defaultdict(list)
    nums = []

    # collects the ratio/speed/sizing data from individual timing files
    # that used the <prefix> compression method
    for i in range(1,23):
        fname = workingdir+prefix+'_'+str(i)+'_compression_timing.csv'
        if not os.path.isfile(fname):
            continue
        nums.append(i)

        starting_sizes = 0
        ending_sizes = 0        

        f = open(fname, 'r')
        f.readline()

        for line in f:
            data = line.split(',')
            # collect ratio data
            if arg == 'ratio':
                collection[data[0]].append(float(data[2])/float(data[3]))
            # collect speed data
            elif arg == 'speed':
                collection[data[0]].append(float(data[2])/1048576/float(data[1]))
            # collect sizing data
            starting_sizes += int(data[2])
            ending_sizes += int(data[3])
        if arg == 'sizing':
            collection[i] = [starting_sizes, ending_sizes, float(starting_sizes)/ending_sizes]

    if not nums:
        return None

    new_fname = workingdir+prefix+'_'+arg+'.csv'
    new_file = open(new_fname, 'w+')

    # create the title line for the csv file, including only the compression
    # levels found in the workingdir
    topline = 'Twitter Handle,'
    for n in nums:
        topline += 'Level '+str(n)+','
    topline = topline[:-1] +'\n'

    if arg in ('ratio','speed'):
        new_file.write(topline)
    elif arg == 'sizing':
        new_file.write('Level,Starting Size (sum),Ending Size (sum),Ratio\n')

    # write the merged file
    for key, values in collection.iteritems():
        dataline = str(key) + ','
        for v in values:
            dataline += str(v)+','
        dataline = dataline[:-1]+'\n'
        new_file.write(dataline)

    new_file.close()

    return new_fname

def err_msg(msg=None):
    if msg:
        print(msg)
    print('USAGE:\n$ python analysis.py (tweet_size_data|merge_speed|merge_ratio|merge_sizing)\n')
    sys.exit(1)

if __name__ == '__main__':
    if not os.path.exists('analysis/'):
        os.makedirs('analysis/')

    if len(sys.argv) != 2:
        err_msg()

    arg = sys.argv[1]

    if arg == 'tweet_size_data':
        new_f = tw_data_by_user()
        print('SUCCESS: created ' + new_f + '\n')
    elif arg in ('merge_speed', 'merge_ratio', 'merge_sizing'):
        new_fs = merge_files(arg[6:])
        if new_fs:
            print('SUCCESS: created files:\n')
            for f in new_fs:
                print('\t'+f)
            print('')
        else:
            print('No files found to merge\n')
    else:
        err_msg('ERROR: Not a valid argument\n')



