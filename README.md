COMEST Offers Malnourished EDEX Servers Tuck
============================================

So you want to run AWIPS II, and you want to feed it with whatever
data you can, using as few resources as possible.  COMEST to the
rescue!

Right now, the only thing that matters is ahget.py.  Run it as your
awips user, as EDEX will be confused if it does not have write access
to files added to /awips2/edex/data/manual, not to mention that a
non-awips user probably does not have write access to that directory.
