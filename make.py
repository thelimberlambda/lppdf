#!/usr/bin/env python
#
# lppdf -- (L)ine (P)rint PDF
#
# Copyright (C) 2016 Eric W Smith
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import glob
import zipfile
import getopt
import sys
import os
from datetime import datetime
from subprocess import check_output, STDOUT

PKGNAME = "lppdf"


def showUsage():
    print("""
Usage: [python] {0} [zip|clean]

  archive  Create a zip archive of all artifacts
  clean    Clean all made artifacts
  test     Run tests
""".format(os.path.basename(sys.argv[0])))


def getZipFilename():
    return PKGNAME + ".zip"


def doClean():
    for f in glob.glob("*.zip"):
        os.unlink(f)
    if os.path.isfile("gitlog"):
        os.unlink("gitlog")


def getArchiveName():
    dtTemplate = PKGNAME + "-%s.zip"
    return dtTemplate % (datetime.now().strftime("%Y%m%d%H%M%S"),)


def generateGitLog():
    gitout = check_output("git log", shell=True, stderr=STDOUT)
    with open("gitlog", "w") as f:
        f.write(gitout)


def hasGit():
    return os.path.isdir(".git")


def makeArchive():
    with zipfile.ZipFile(getArchiveName(), "w") as zf:
        if hasGit():
            generateGitLog()
            zf.write("gitlog")
        zf.write("LICENSE")
        for f in ("make", "make.bat"):
            zf.write(f)
        for f in glob.glob("*.py"):
            zf.write(f)
        for f in glob.glob("*.rst"):
            zf.write(f)
        for f in glob.glob("tests/*"):
            zf.write(f)

options = getopt.getopt(sys.argv[1:], "")

if len(options[1]) < 1:
    showUsage()
    sys.exit(-1)

o = options[1].pop(0)

if o == "archive":
    makeArchive()
elif o == "clean":
    doClean()
elif o == "test":
    os.system("python " + PKGNAME + "-test.py")
else:
    showUsage()
