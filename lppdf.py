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

import getopt
from sys import argv, exit
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape, portrait
from os.path import basename
from reportlab.pdfbase.pdfmetrics import stringWidth


class lppdfConverterParams:

    def set_defaults(self):
        self.columns = 80
        self.rows = 60
        self.fontSize = 10
        self.fontName = "Courier"
        self.pageOrientation = "portrait"
        self.pageSize = A4
        self.fd = None
        self.fileSpec = None
        self.outFileSpec = None
        self.needHelp = False
        self.ignoreFF = False
        self.margins = {
            "l": cm,
            "r": cm,
            "t": cm,
            "b": cm}
        self.auto_font_size = False

    def __init__(self):
        self.set_defaults()


class lppdfConverterSpec:

    def __init__(self, params):
        self.fill_spec(params)

    def __enter__(self):
        pass

    def __exit__(self):
        if self.fd:
            self.fd.close()

    def fill_spec(self, params):
        self.columns = params.columns
        self.rows = params.rows
        self.fontSize = params.fontSize
        self.fontName = params.fontName
        self.pageSize = params.pageSize
        if params.pageOrientation == "portrait":
            self.pageOrientation = portrait
        else:
            self.pageOrientation = landscape
        self.fileSpec = params.fileSpec or "UNNAMED"
        self.ignoreFF = params.ignoreFF
        self.ensure_fd(params)
        self.ensure_outFileSpec(params)
        self.margins = params.margins
        self.auto_font_size = params.auto_font_size

    def ensure_outFileSpec(self, params):
        if params.outFileSpec:
            self.outFileSpec = params.outFileSpec
        else:
            if not self.fileSpec:
                raise Exception("No output file information available")
            self.outFileSpec = self.outFileSpecFrom(self.fileSpec)

    def outFileSpecFrom(self, fs):
        vp = fs.rpartition(';')  # Remove VMS versions
        if vp[1] == ';':
            fs = vp[0]
        ep = fs.rpartition('.')
        if ep[1] == '.':
            fs = ep[0]
        return fs + ".pdf"

    def ensure_fd(self, params):
        self._fd_needs_closing = False
        if not params.fd:
            if not params.fileSpec:
                raise Exception("No file specification provided")
            self.fd = open(self.fileSpec, 'r')
            self._fd_needs_closing = True


class lppdfConverter:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._spec:
            self._spec.__exit__()

    def __init__(self, params):
        self._spec = lppdfConverterSpec(params)
        pass

    def initialize_canvas(self):
        self.finalPageSize = self._spec.pageOrientation(self._spec.pageSize)
        self._canvas = Canvas(self._spec.outFileSpec, bottomup=0,
                              pagesize=self.finalPageSize)
        if self._spec.auto_font_size:
            self.doFontSizeCorrection()
        self.setCanvasState()

    def doFontSizeCorrection(self):
        for s in xrange(self._spec.fontSize, 2, -1):
            tw = stringWidth("O"*self._spec.columns, self._spec.fontName, s)
            s4t = self.spaceForText()
            if s4t > tw:
                self._spec.fontSize = s
                return
        raise Exception("Unable to choose a font small enough to fit " +
                        "all columns on page")

    def spaceForText(self):
        mspace = self._spec.margins["l"] + self._spec.margins["r"]
        return self.finalPageSize[0] - mspace

    def setCanvasState(self):
        self._canvas.setFont(self._spec.fontName, self._spec.fontSize)
        self._canvas.translate(self._spec.margins["l"],
                               self._spec.margins["t"])

    def complete(self):
        self._canvas.save()

    def convert(self):
        self.initialize_canvas()
        self.drawPages()
        self.complete()

    def drawLine(self, line):
        self._canvas.drawString(
            0, self._spec.fontSize*self._line_number,
            line[:self._spec.columns])

    def drawPages(self):
        self._line_number = 0
        for l in self._spec.fd:
            between_ff = l.split('\x0c')
            if len(between_ff) == 1 or self._spec.ignoreFF:
                self.drawLine("".join([s.rstrip() for s in between_ff]))
            else:
                for partix in xrange(0, len(between_ff)):
                    if len(between_ff[partix]) > 0:
                        self.drawLine(between_ff[partix].rstrip())
                    if partix < len(between_ff)-1:
                        self.puntPage()
            self._line_number += 1
            if self._line_number == self._spec.rows:
                self.puntPage()

    def puntPage(self):
        self._canvas.showPage()
        self.setCanvasState()
        self._line_number = 0


class lppdfConverterArgsParser:

    def __init__(self, args):
        self._args = args

    def parseMargins(self, margin_str):
        ls, rs, ts, bs = margin_str.split(",")
        margins = list()
        for v in [ls, rs, ts, bs]:
            if v.endswith("mm"):
                margins.append(float(v[:-2])*cm/10)
            else:
                margins.append(float(v))
        self.params.margins = dict(zip(['l', 'r', 't', 'b'], margins))

    def getParams(self):
        self.params = lppdfConverterParams()
        opts, args = getopt.getopt(self._args, "ac:m:o:fr:s:hL",
                                   ["landscape", "help",
                                    "font-size=", "rows=",
                                    "no-ff", "output=",
                                    "margins=", "columns=",
                                    "auto-font-size"])
        for o in opts:
            if o[0] in ("-L", "--landscape"):
                self.params.pageOrientation = "landscape"
            elif o[0] in ("-h", "--help"):
                self.params.needHelp = True
            elif o[0] in ("-s", "--font-size"):
                self.params.fontSize = int(o[1])
            elif o[0] in ("-r", "--rows"):
                self.params.rows = int(o[1])
            elif o[0] in ("-f", "--no-ff"):
                self.params.ignoreFF = True
            elif o[0] in ("-o", "--output"):
                self.params.outFileSpec = o[1]
            elif o[0] in ("-m", "--margins"):
                self.parseMargins(o[1])
            elif o[0] in ("-c", "--columns"):
                self.params.columns = int(o[1])
            elif o[0] in ("-a", "--auto-font-size"):
                self.params.auto_font_size = True
        if self.params.needHelp:
            return self.params
        if len(args) < 1:
            raise Exception("Input file name is required; " +
                            "%s --help for usage" % (argv[0],))
        self.params.fileSpec = args[0]
        return self.params


def exitWithHelp():
    exit("""\
 %(progname)s

 Converts plain text files to PDF using Courier font and A4 paper (either
 portrait or landscape).  Text files can be either LF or CR/LF delimited, and
 form feed characters (0x0c) result in a new page being started.

 Usage: %(progname)s [options] <text file>

 Options:

   -h, --help               Show this help screen
   -s<n>, --font-size=<n>   Set the font size to <n> (def: 10pt)
   -a, --auto-font-size     Use provided column value, page size and margins
                            to determine font size.
   -m<l,r,t,b>
   --margins=<l,r,t,b>      Set margins <l>eft,<r>ight,<t>op,<b>ottom.
                            Default units are pt, but mm can also be specified
                            (def: 10mm,10mm,10mm,10mm)
   -c<n>, --columns=<n>     Set columns per row; truncate further (def: 80)
   -r<n>, --rows=<n>        Set the rows per page to <n> (def: 60)
   -f, --no-ff              Ignore form feed characters (0x0c)
   -o<file> --output=<file> Specify output file of <file>, the default is to
                            use the input file with the extension changed to
                            PDF.
   -L, --landscape          Use landscape mode (def: portrait)
""" % {"progname": basename(argv[0])})

if __name__ == "__main__":
    p = lppdfConverterArgsParser(argv[1:]).getParams()
    if p.needHelp:
        exitWithHelp()
    with lppdfConverter(p) as converter:
        converter.convert()
