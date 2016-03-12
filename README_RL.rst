ReportLab Installation using Pip
================================

Note: these instructions apply to Python 2.7.10+ and have not been tested with
Python 3+ (although there's no reason why they shouldn't):

1. Make sure that you know the hostname/IP of your proxy server if your're on a
   corporate network--the moniker <proxy-server> will be used to refer to it in
   subsequent points.  If you don't know what a proxy server is, or it's
   difficult to find this information out, or if your proxy server requires NTLM
   authentication, then install Fiddler (http://www.telerik.com/fiddler) and do
   the following in order to use it as a proxy:

   1. After running the install, launch Fiddler and go to Tools|Fiddler
      Options;
   2. Click the Connections tab, and ensure that the "Act as system proxy on
      startup" tick box is checked;
   3. Cancel out of the Fiddler Options dialogue box;
   4. In subsequent instructions make sure that <proxy-server> is replaced with
      localhost:8888.

2. Open a Windows command prompt as Administrator by right-clicking the
   prompt icon and selecting "Run as administrator" in the resultant context
   menu;
3. Issue the following at the command prompt::

     pip install reportlab --proxy <proxy-server> --trusted-host pypi.python.org

