#!/usr/bin/python

import os,sys,time,dbm,httplib,shutil

host = 'level3.allisonhouse.com'

sites = ['DGX']

#prods = ['GSM', 'N0Q']
prods = ['DAA',  'DTA',  'DSD',  'HHC',  'N0M',  'N0U',  'N1C',  'N1P',  'N1X',  'N2M',  'N2X',  'N3M',  'N3U',  'NAM',  'NBC',  'NBQ',  'NET',  'NVW',  'SPD',  'TR2',
         'DHR',  'DU3',  'DVL',  'N0C',  'N0Q',  'N0V',  'N1H',  'N1Q',  'N2C',  'N2Q',  'N3C',  'N3X',  'NAC',  'NAQ',  'NBH',  'NBU',  'NMD',  'NTP',  'TZL',  'TV0',
         'DPR',  'DU6',  'EET',  'N0H',  'N0R',  'N0X',  'N1K',  'N1S',  'N2H',  'N2S',  'N3H',  'N3Q',  'NAH',  'NAU',  'NBK',  'NBX',  'NST',  'OHA',  'TR0',  'TV1',
         'DSP',  'DOD',  'GSM',  'N0K',  'N0S',  'N0Z',  'N1M',  'N1U',  'N2K',  'N2U',  'N3K',  'N3S',  'NAK',  'NAX',  'NBM',  'NCR',  'NVL',  'PTA',  'TR1',  'TV2' ]

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

for site  in sites:
    for prod in prods:
        conn.request('GET', '/level3/%s/data/nexrad/%s/%s/dir.list' % (akey, site, prod))
        resp = conn.getresponse()
        cont = resp.read()
        flist = cont.splitlines()
        
        for ff in flist:
            upath = '/level3/%s/data/nexrad/%s/%s/%s' % (akey,site,prod,ff)
            if not seen.has_key(upath):
		print "FF %s UPATH %s" % (ff,upath)
                conn.request('GET', upath)
                fp = open(ff,"w")
                fp.write(conn.getresponse().read())
                fp.close()
                shutil.move(ff,'/awips2/edex/data/manual')
                seen[upath] = str(time.time())
            else:
                print "Skipping previously seen",upath
