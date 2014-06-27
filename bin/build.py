#!/usr/bin/python2

import imp
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=False, type=str, default='buildscript.py')
    parser.add_argument('-j', '--jobs', required=False, type=int, default=1)
    options = parser.parse_args()

    if not os.path.exists(options.file):
        print 'buildscript.py not found'
        return 1

    buildscript = imp.load_source('buildscript', options.file)
    buildscript.builder.build(jobs=options.jobs)
    os.unlink(options.file + 'c')
    return 0


if '__main__' == __name__:
    sys.exit(main())
