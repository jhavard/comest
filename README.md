COMEST Offers Malnourished EDEX Servers Tuck
============================================

So you want to run AWIPS II, and you want to feed it with whatever
data you can, using as few resources as possible.  COMEST to the
rescue!

Right now, the only thing that matters is ahget.py.  Run it as your
awips user, as EDEX will be confused if it does not have write access
to files added to /awips2/edex/data/manual, not to mention that a
non-awips user probably does not have write access to that directory.

From a fresh start, assuming you aren't bandwidth-constrained, all products
for two sites should download in a little under two minutes.  It keeps track
of all URLs it has fetched, so that the next time it runs it can skip those.
If you run it once every five minutes, subsequent runs will probably take 
something like 20 seconds.  If you are using Windstream DSL, be prepared to
wait a while.