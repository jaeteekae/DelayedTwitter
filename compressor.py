#
#  compressor.py
#
# USAGE:
# $ python compressor.py (brotli|zstd) <compression_level> [path_to_dictionary]
#
# Settings found in settings.py
#

import zstandard as zstd
import brotli

import json, os, time, sys, random
from datetime import datetime

import settings

# Returns the appropriate compression function, function arguments, 
#  and file extension for the algo
def algo_to_fun(algo, comp_level, dictionary):
    if algo == 'brotli':
        return brotli.compress, {'quality':comp_level}, 'br'
    elif algo == 'zstd':
        if dictionary:
            with open(dictionary, 'r') as f:
                dict_data = zstd.ZstdCompressionDict(f.read())
            cctx = zstd.ZstdCompressor(level=comp_level, dict_data=dict_data)
        else:
            cctx = zstd.ZstdCompressor(level=comp_level)
        return cctx.compress, {}, 'zst'

def compress(compressor, args, fext):
    # Create csv timing file
    if settings.COMPRESSOR_WRITE_TIMING_FILES:
        timingf = open('analysis/'+algo+'_'+str(comp_level)+'_compression_timing.csv', 'w+')
        timingf.write('Twitter Handle,Seconds Ellapsed,Starting Size (bytes),Ending Size (bytes),Compression Ratio,Speed(MBps\n')

    workingdir = 'downloaded_tweets'

    # Compresses every json file in the downloaded_tweets folder
    for filename in os.listdir(workingdir):
        if filename.endswith('.json'):
            dataline = filename[:-5]+','

            cur_file = os.path.join(workingdir, filename)

            # Compress file & time it
            f = open(cur_file, 'r')

            start = datetime.now()
            compressed = compressor(f.read(),**args)
            end = datetime.now()

            f.close()

            # Write compressed file to disk
            if settings.COMPRESSOR_WRITE_COMPRESSED_FILES:
                r = open(cur_file[:-4]+fext, 'w')
                r.write(compressed)
                r.close()

            # Collect and write stats
            delta = end-start
            dataline += str(delta.total_seconds())

            orig_stats = os.stat(cur_file)
            comp_stats = len(compressed)

            ratio = orig_stats.st_size/float(comp_stats)
            speed = float(orig_stats.st_size)/1048576/delta.total_seconds()

            dataline += ','+str(orig_stats.st_size)+','+str(comp_stats)+','+str(ratio)+','+str(speed)+'\n'

            if settings.COMPRESSOR_WRITE_TIMING_FILES:
                timingf.write(dataline)

            # Delete .json file
            if settings.COMPRESSOR_DELETE_UNCOMPRESSED_FILES:
                os.remove(cur_file)
    if settings.COMPRESSOR_WRITE_TIMING_FILES:
        timingf.close()


def set_up():
    if settings.COMPRESSOR_WRITE_TIMING_FILES:
        if not os.path.exists('analysis/'):
            os.makedirs('analysis/')

def validate(args):
    if len(args) < 3:
        exit_error()

    algo = args[1].lower()
    comp_level = args[2]
    dictionary = None

    # Check the compression algorithm is valid
    if algo not in ('brotli','zstd'):
        exit_error('ERROR: Not a valid compression algorithm\n')

    # Check that compression_level is an int
    try:
        comp_level = int(comp_level)
    except:
        exit_error('ERROR: The compression level must be an integer\n')

    # Check that the dictionary file exits
    if len(args) > 3:
        if algo == 'brotli':
            print("NOTE: this compression algorithm does not use a dictionary\n")
        elif not os.path.exists(args[3]):
            exit_error('ERROR: Incorrect path given to dictionary\n')
        else:
            dictionary = args[3]

    # Check compression level is in the right range
    if algo=='brotli':
        if comp_level not in range(1,12):
            exit_error('ERROR: The compression level for brotli must be an integer from 1 to 11 (inclusive)\n')    
    elif algo=='zstd':
        if comp_level not in range(1,23):
            exit_error('ERROR: The compression level for zstd must be an integer from 1 to 22 (inclusive)\n')

    return algo, comp_level, dictionary

# Ends program with err message
def exit_error(msg=''):
    if msg:
        print(msg)
    print("USAGE:\n$ python compressor.py (brotli|zstd) <compression_level> [path_to_dictionary]\n")
    sys.exit(1)


if __name__ == '__main__':
    set_up()

    algo, comp_level, dictionary = validate(sys.argv)

    compressor, args, fext = algo_to_fun(algo, comp_level, dictionary)

    compress(compressor, args, fext)


