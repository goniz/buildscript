#!/usr/bin/python2

import imp
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=False, type=str, default='buildscript.py')
    parser.add_argument('-j', '--jobs', required=False, type=int, default=1)
    parser.add_argument('-v', '--verbose', required=False, action='store_true', default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('action', metavar='action', nargs='*', default=['build'])
    options = parser.parse_args()

    if not os.path.exists(options.file):
        print 'buildscript.py not found'
        return 1

    buildscript = imp.load_source('buildscript', options.file)
    buildscript.builder.verbose = options.verbose
    if 'clean' in options.action:
        buildscript.builder.clean()
    if 'configure' in options.action:
        buildscript.builder.configure()
    if 'build' in options.action:
        buildscript.builder.build(jobs=options.jobs)
    if 'rebuild' in options.action:
        buildscript.builder.clean()
        buildscript.builder.build(jobs=options.jobs)

    os.unlink(options.file + 'c')
    return 0


if '__main__' == __name__:
    sys.exit(main())
