#!python

import os, sys
from glob import glob
import argparse

SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],

             1024 :   [ 'KiB' ,   'MiB' ,   'GiB' ,   'TiB' ,   'PiB' ,   'EiB' ,   'ZiB' ,   'YiB' ]} 
def  approximate_size ( size ,  a_kilobyte_is_1024_bytes = True ): 
    '''Convert a file size to human-readable form.

    Keyword arguments:
    size -- file size in bytes
    a_kilobyte_is_1024_bytes -- if True (default), use multiples of 1024
                                if False, use multiples of 1000

    Returns: string

    '''
    if  size  <   0 :
        raise   ValueError ( 'number must be non-negative' ) 

    multiple  =   1024   if  a_kilobyte_is_1024_bytes  else   1000
    for  suffix  in  SUFFIXES [ multiple ]:
        size  /=  multiple
        if  size  <  multiple :
            return   '{0:.1f} {1}' . format ( size ,  suffix )

    raise   ValueError ( 'number too large' )


def list_files_by_size(path, format, recursive=True):
    os.chdir(path)
    files_info = []
    if format.lower() == "all":
        files = glob("**", recursive=recursive)
    else:
        if recursive:
            files = glob(f"**/**.{format}", recursive=recursive)
        else:
            files = glob(f"**.{format}", recursive=recursive)
    for name in files:
        size = os.path.getsize(name)
        files_info.append([name, size])
    files_info = sorted(files_info, key=lambda x: x[1], reverse=True)
    return files_info

def main():
    parser = argparse.ArgumentParser(description="List files by size")
    parser.add_argument("-n", "--number", help="show page number", default = 10)
    parser.add_argument('-r', "--recursive", help="recursive", action="store_true")
    parser.add_argument("path", help="Path to list files")
    parser.add_argument("format", help="Format of files, can be 'all' or file format extension like 'jpg'")

    args = parser.parse_args()
    print(f'path: {args.path}, format: {args.format}, recursive: {args.recursive}\n')

    if not os.path.exists(args.path):
        print("Path does not exist: {}".format(args.path))
        sys.exit(1)
    files = list_files_by_size(args.path, args.format, recursive = args.recursive)

    count = 1
    for file in files:
        print(f'{approximate_size(file[1])} - {file[1]} : {file[0]}')
        if count % args.number == 0:
            input("Press Enter to continue...")
        count += 1

if __name__ == "__main__":
    main()


