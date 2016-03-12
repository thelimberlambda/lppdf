(L)ine(P)rint PDF (lppdf)
=========================

::

   Copyright (C) 2016 Eric W Smith
   
   This program is free software: you can redistribute it and/or modify it under
   the terms of the GNU General Public License as published by the Free Software
   Foundation, either version 3 of the License, or (at your option) any later
   version.
   
   This program is distributed in the hope that it will be useful, but WITHOUT
   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
   FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
   details.
   
   You should have received a copy of the GNU General Public License along with
   this program.  If not, see <http://www.gnu.org/licenses/>.
   
lppdf is a Python-based utility designed to "line print" text files to PDF
format, in particular, files in old "eyeline" format (that is, 132 column and 60
lines, with embedded carriage-return (\x0d), line-feed (\x0a) and form-feed
(\x0c) ASCII control characters).

Installation
------------

1. Ensure that Python 2.7.10+ is installed (lppdf hasn't been tested with
   Python 3);
2. Ensure that ReportLab (http://www.reportlab.com/) is installed (see 
   README_RL.rst for detailed instructions for installing RL using `pip`);
3. Ensure that Ghostscript is installed;
4. Ensure that the path to `gs`/`gswin32c` (Ghostscript command-line tool)
   is set up properly;
5. Ensure that ImageMagick is installed;
6. Confirm that paths to Imagemagick tools are correctly set up by openging a
   console/command prompt and issuing the `identify` and `compare` commands.

Invocation
----------

::

  python lpppdf.py <options> <text-file>

Help
----

::

  python lppdf.py --help

Tests
-----

In the bundle is a Python-based test script and a number of test case files
(under `./tests`).  PDF's are generated based on a given set of arguments, and a
"correct" sample compared-against in order to return a pass/fail condition.

In order to ensure that tests run correctly, the following programs need to be
installed:

* Ghostscript (lppdf uses `gs`/`gswin32`);
* Imagemagick (lppdf uses the `identify` and `compare` programs)

To run all tests:

::

  ./make test

or...

::

  make test

for Windows.
