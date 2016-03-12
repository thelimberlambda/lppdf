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
import os
import sys
import glob
import tempfile
from subprocess import check_output, CalledProcessError, STDOUT
from getopt import getopt
import shutil


class DifferenceError(Exception):

    def __init__(self, output):
        Exception.__init__(self)
        self.output = output


class PdfTest:
    """Encapsulate everything related to a PDF comparison test case"""

    _LPPDF = "python lppdf.py -o %(output)s %(args)s %(input)s"
    _COMPEXE = "/usr/bin/compare"
    _IDEXE = "/usr/bin/identify"
    _IDCMD = "%(idexe)s %(fs_o)s"
    _COMPCMD_TMPL = \
        "%(cmpexe)s -metric FUZZ -quiet " + \
        "%(fs_c)s[%(pcount)d] %(fs_o)s[%(pcount)d] %(fs_d)s"

    def __init__(self, test_case_file):
        self.test_case_file = test_case_file
        self.verbose = False
        self.initialize()

    def __enter__(self):
        self.erase_test_output = True
        return self

    def __exit__(self, exc, exctype, traceback):
        if self.erase_test_output and os.path.isfile(self.fs_output):
            os.unlink(self.fs_output)

    def extractFileSpecParts(self):
        self.fs_dir_part = os.path.dirname(self.test_case_file)
        self.fs_name_part = os.path.basename(
            self.test_case_file).rpartition('.')[0]

    def extractInvocationArgs(self):
        with open(self.test_case_file, 'r') as f:
            for l in f.xreadlines():
                if l.startswith("Args:"):
                    self.invocation_args = l.partition(':')[2].strip()
                elif l.startswith("Description:"):
                    self.description = l.partition(":")[2].strip()

    def initialize(self):
        self.extractFileSpecParts()
        self.extractInvocationArgs()
        self.fs_input = self.findInputFile()
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tf:
            self.fs_output = tf.name
        self.fs_control = os.path.join(self.fs_dir_part,
                                       self.fs_name_part + ".pdf")
        if not os.path.isfile(self.fs_control):
            raise Exception(
                "Test control file %s not found" % (self.fs_control,))

    def findInputFile(self):
        glob_pat = os.path.join(self.fs_dir_part, self.fs_name_part + ".*")
        test_f_iter = (p.lower() for p in glob.iglob(glob_pat))
        i_file = [p for p in test_f_iter if p.rpartition('.')[2] not in
                  ("tce", "pdf", "png")][:1]
        if len(i_file) == 0:
            raise Exception(
                'No input file found corresponding to test "%s"' %
                (self.fs_name_part,))
        return i_file.pop(0)

    def generatePdf(self):
        lppdf_cmd = PdfTest._LPPDF % {
            "output": self.fs_output,
            "input": self.fs_input,
            "args": self.invocation_args
            }
        os.system(lppdf_cmd)

    def countPdfPages(self):
        idcmd = PdfTest._IDCMD % {
            "idexe": PdfTest._IDEXE,
            "fs_o":  self.fs_output
            }
        self.page_count = len(
            check_output(idcmd, shell=True, stderr=STDOUT).strip().split("\n"))

    def execute(self):
        self.generatePdf()
        self.countPdfPages()
        with tempfile.NamedTemporaryFile(suffix='.png') as tf:
            png_file = tf.name
        for pcount in xrange(0, self.page_count):
            try:
                compcmd = PdfTest._COMPCMD_TMPL % {
                    "cmpexe": PdfTest._COMPEXE,
                    "fs_c":   self.fs_control,
                    "pcount": pcount,
                    "fs_o":   self.fs_output,
                    "fs_d":   png_file
                    }
                outp = check_output(compcmd, shell=True, stderr=STDOUT)
                difference = float(outp.split()[0])
                if difference > 10:
                    raise DifferenceError(outp)
            except (CalledProcessError, DifferenceError) as e:
                print("The generated PDF does not match the control (%s)" %
                      (self.fs_control,))
                print("... on page: %d of %d" % (pcount+1, self.page_count))
                print("... FUZZ deviation: %s" % (e.output.strip(),))
                print("... Generated output: %s" % (self.fs_output,))
                print("... Difference file: %s" % (png_file,))
                self.erase_test_output = False
                print("Use: python %(pn)s -i %(fs_tc)s %(fs_o)s" % {
                    "pn":    program_name,
                    "fs_tc": self.test_case_file,
                    "fs_o":  self.fs_output
                    })
                print("... to install the generated PDF as the control")
                break
            else:
                os.unlink(png_file)

    def installPdf(self, fs_newpdf):
        try:
            shutil.copy(fs_newpdf, self.fs_control)
        except:
            pass
        else:
            os.unlink(fs_newpdf)

    def displayDescription(self):
        print("Test: {0}".format(self.description))

if __name__ == "__main__":
    program_name = sys.argv[0]

    options = getopt(sys.argv[1:], "i", ["install"])

    for o in options[0]:
        if o[0] in ("-i", "--install"):
            if len(options[1]) < 2:
                raise Exception("Install option requires " +
                                "test case file and PDF arguments")
            with PdfTest(options[1].pop(0)) as pt:
                pt.installPdf(options[1].pop(0))
            sys.exit(0)
    for test_case_file in glob.iglob("./tests/*.tce"):
        with PdfTest(test_case_file) as pt:
            pt.displayDescription()
            pt.execute()
