#
#  decompressor.py
#
# USAGE:
# $ python decompressor.py [brotli|zstd] [path_to_dictionary]
#
# With no arguments, this will decompress every compressed file with a 
# .br or .zstd extention in the downloaded_tweets folder.
#
# If a dictionary is provided, it must be same dictionary that was used
# to compress the files
# 

import zstandard as zstd
import brotli

import os, sys

import settings

def decompress(fexts, dictionary=None):
    # directory with files to be decompressed
    workingdir = 'downloaded_tweets'
    
    # Set up zstd decompressor
    if dictionary:
        with open(dictionary, 'r') as f:
            dict_data = zstd.ZstdCompressionDict(f.read())
        dctx = zstd.ZstdDecompressor(dict_data=dict_data)
    else:
        dctx = zstd.ZstdDecompressor()

    # decompress files
    for filename in os.listdir(workingdir):
        tw_handle, ext = os.path.splitext(filename)
        if ext in fexts:
            cur_file = os.path.join(workingdir, filename)

            # Decompress the file
            f = open(cur_file, 'r')

            if ext == '.br':
                decompressed = brotli.decompress(f.read())
            elif ext == '.zst':
                decompressed = dctx.decompress(f.read())

            f.close()

            # Write the decompressed .json file
            new_file = os.path.join(workingdir, tw_handle+'.json')
            with open(new_file, 'w') as f:
                f.write(decompressed)

            # Delete old compressed file
            if settings.DECOMPRESSOR_DELETE_COMPRESSED_FILES:
                os.remove(cur_file)

def validated(dict_path):
    if not os.path.exists(dict_path):
        print('ERROR: Incorrect path given to dictionary\n')
        sys.exit(1)
    return dict_path

if __name__ == '__main__':
    fexts = ['.br','.zst']

    if len(sys.argv) == 1:
        decompress(fexts)
    elif sys.argv[1].lower() == 'brotli':
        decompress(['.br'])
    elif sys.argv[1].lower() == 'zstd':
        if len(sys.argv) > 2:
            decompress(['.zst'], validated(sys.argv[2]))
        else:
            decompress(['.zst'])
    else:
        decompress(fexts, validated(sys.argv[2]))

