#!/usr/bin/python

import os,sys,time,dbm,httplib,shutil

host = 'level3.allisonhouse.com'

# List the radar sites you care about here
sites = ['DGX', 'GWX']

# The big fat product list
prods = ['DAA',  'DTA',  'DSD',  'HHC',  'N1C',  'N1P',  'N1X',  'N2M',  'N2X',  'N3M',  'N3U',  'NAM',  'NBC',  'NBQ',  'NET',  'NVW',  'SPD',  'TR2',
         'DHR',  'DU3',  'DVL',  'N1H',  'N1Q',  'N2C',  'N2Q',  'N3C',  'N3X',  'NAC',  'NAQ',  'NBH',  'NBU',  'NMD',  'NTP',  'TZL',  'TV0',
         'DPR',  'DU6',  'EET',  'N1K',  'N1S',  'N2H',  'N2S',  'N3H',  'N3Q',  'NAH',  'NAU',  'NBK',  'NBX',  'NST',  'OHA',  'TR0',  'TV1',
         'DSP',  'DOD',  'GSM',  'N1M',  'N1U',  'N2K',  'N2U',  'N3K',  'N3S',  'NAK',  'NAX',  'NBM',  'NCR',  'NVL',  'PTA',  'TR1',  'TV2' ]

#TODO: Add VCP check, and break Big Fat Product List into core products and precip mode products, 
#TODO: then build prods array based on that.

# These come from nexdown, which is part of python-emwin, so no need to fetch them here.  Add to prods if you
# do not use that.
#prods += ['N0C', 'N0H', 'N0K', 'N0M', 'N0Q', 'N0R', 'N0S', 'N0U', 'N0V', 'N0X', 'N0Z']

seen = dbm.open('ahseen.db','c')

try:
    akey = open('/etc/allisonhouse.key', 'r').readline().strip()
except:
    print "Put your allison house key in /etc/allisonhouse.key"
    sys.exit(1)

try:
    os.chdir("data")
except:
    os.mkdir("data")
    os.chdir("data")

conn = httplib.HTTPConnection(host)


for prod in prods:
    for site  in sites:
        try:
            conn.request('GET', '/level3/%s/data/nexrad/%s/%s/dir.list' % (akey, site, prod))
            resp = conn.getresponse()
            cont = resp.read()
            flist = cont.splitlines()
        except:
            print "ERROR Some random exception on",site,prod
            continue
        
        for ff in flist[10:]:
            upath = '/level3/%s/data/nexrad/%s/%s/%s' % (akey,site,prod,ff)
            if not seen.has_key(upath):
                print "%s/%s/%s" % (site,prod,ff)
                conn.request('GET', upath)
                fp = open(ff,"w")
                fp.write(conn.getresponse().read())
                fp.close()
                try:
                    shutil.move(ff,'/awips2/edex/data/manual')
                except:
                    "\tERROR while moving",ff
                seen[upath] = str(time.time())
            else:
                print "Skipping previously seen",upath
