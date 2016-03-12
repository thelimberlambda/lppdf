#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import random


def showUsage():
    print("""
Obfuscates text files by replacing characters within a class with
random entries within the same class.  Classes include A-Z, a-z
and 0-9. All other characters remain the same.

Usage: [python] {proggy} <in-file> <out-file>
""".format(proggy=os.path.basename(sys.argv[0])))

if len(sys.argv) < 3:
    showUsage()
    sys.exit(-1)


def mixup_char(c):
    if c >= 'a' and c <= 'z':
        return chr(random.randrange(ord('a'), ord('z')+1))
    elif c >= 'A' and c <= 'Z':
        return chr(random.randrange(ord('A'), ord('Z')+1))
    elif c >= '0' and c <= '9':
        return chr(random.randrange(ord('0'), ord('9')+1))
    return c

in_file = sys.argv[1]
out_file = sys.argv[2]
random.seed()
with open(in_file, "r") as in_f:
    with open(out_file, "w") as out_f:
        while True:
            c = in_f.read(1)
            if not c:
                break
            out_f.write(mixup_char(c))
