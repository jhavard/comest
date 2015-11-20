"""
WSR-88D Level 3 info decoder, based off of the implementation in
http://arm-doe.github.io/pyart-docs-travis/index.html but that
did not work for me, which is why I had to create this.  What I need
is the ability to get the VCP from a product.  Everything else is
gravy.
"""

import struct

import zlib

class NEXRADLevel3File:
    """
    Simple class for getting the metadata about a Level III product
    """

    vcp = 0

    def __init__(self, filename):
        """ load a file and do all the fun stuff """
        fp = open(filename)
        self.buf = fp.read()
        buf = self.buf
        self.text_header = buf[:30]
        #print self.text_header
        bpos = 30
	if struct.unpack("bb", buf[bpos:bpos+2]) == (0x78,0x9A):
		print "*** ZLIB DETECTED ***"
		dcb = zlib.decompress(buf[bpos:])
		buf = dcb
		bpos = 54 # the header in the zlib version is longer, but still regular	
        self.msg_header = _unpack_from_buf(buf, bpos, MESSAGE_HEADER)
        bpos += 18
        self.product_desc = _unpack_from_buf(buf, bpos, PRODUCT_DESCRIPTION)
        self.vcp = self.product_desc['vcp']
                                           

def _unpack_structure(string, structure):
    """ unpack a structure from a string"""
    fmt = '>' + ''.join([i[1] for i in structure])
    lst = struct.unpack(fmt, string)
    return dict(zip([i[0] for i in structure], lst))


def nexrad_level3_message_code(filename):
    fhl = open(filename, 'r')
    buf = fhl.read(48)
    fhl.close()
    msg_header = _unpack_from_buf(buf, 30, MESSAGE_HEADER)
    return msg_header['code']

def _int16_to_float16(val):
    """ Convert a 16 bit interger into a 16 bit float. """
    # NEXRAD Level III float16 format defined on page 3-33.
    # Differs from IEEE 768-2008 format so np.float16 cannot be used.
    sign = (val & b0b1000000000000000) / 0b1000000000000000
    exponent = (val & 0b0111110000000000) / 0b0000010000000000
    fraction = (val & 0b0000001111111111)
    if exponent == 0:
        return (-1)**sign * 2 * (0 + (fraction/2**10.))
    else:
        return (-1)**sign * 2**(exponent-16) * (1 + fraction/2**10.)

def _datetime_from_mdate_mtime(mdate, mtime):
    """ Returns a datetime for a given message date and time. """
    epoch = datetime.utcfromtimestamp(0)
    return epoch + timedelta(days=mdate - 1, seconds=mtime)


def _structure_size(structure):
    """ Find the size of a structure in bytes. """
    return struct.calcsize('>' + ''.join([i[1] for i in structure]))


def _unpack_from_buf(buf, pos, structure):
    """ Unpack a structure from a buffer. """
    size = _structure_size(structure)
    return _unpack_structure(buf[pos:pos + size], structure)
        

_8_OR_16_LEVELS = [19, 20, 25, 27, 28, 30, 56, 78, 79, 80, 169, 171, 181]

PRODUCT_RANGE_RESOLUTION = {
    19: 1.,     # 124 nm
    20: 2.,     # 248 nm
    25: 0.25,   # 32 nm
    27: 1.,
    28: 0.25,
    30: 1.,
    32: 1.,
    34: 1.,
    56: 1.,
    78: 1.,
    79: 1.,
    80: 1.,
    94: 1.,
    99: 0.25,
    134: 1000.,
    135: 1000.,
    138: 1.,
    159: 0.25,
    161: 0.25,
    163: 0.25,
    165: 0.25,
    169: 1.,
    170: 1.,
    171: 1.,
    172: 1.,
    173: 1.,
    174: 1.,
    175: 1.,
    177: 0.25,
    181: 150.,
    182: 150.,
    186: 300.,
}

# format of structure elements
# Figure E-1, page E-1
BYTE = 'B'      # not in table but used in Product Description
INT2 = 'h'
INT4 = 'i'
UINT4 = 'I'
REAL4 = 'f'

# 3.3.1 Graphic Product Messages

# Graphic Product Message: Message Header Block
# 18 bytes, 9 halfwords
# Figure 3-3, page 3-7.
MESSAGE_HEADER = (
    ('code', INT2),     # message code
    ('date', INT2),     # date of message, days since 1 Jan, 1970
    ('time', INT4),     # time of message, seconds since midnight
    ('length', INT4),   # length of message in bytes
    ('source', INT2),   # Source ID
    ('dest', INT2),     # Destination ID
    ('nblocks', INT2),  # Number of blocks in the message (inclusive)
)

# Graphic Product Message: Product Description Block
# Description: section 3.3.1.1, page 3-3
# 102 bytes, 51 halfwords (halfwords 10-60)
# Figure 3-6, pages 3-31 and 3-32
PRODUCT_DESCRIPTION = (
    ('divider', INT2),          # Delineate blocks, -1
    ('latitude', INT4),         # Latitude of radar, degrees, + for north
    ('longitude', INT4),        # Longitude of radar, degrees, + for east
    ('height', INT2),           # Height of radar, feet abouve mean sea level
    ('product_code', INT2),     # NEXRAD product code
    ('operational_mode', INT2),  # 0 = Maintenance, 1 = Clean Air, 2 = Precip
    ('vcp', INT2),              # Volume Coverage Pattern of scan strategy
    ('sequence_num', INT2),     # Sequence Number of the request.
    ('vol_scan_num', INT2),     # Volume Scan number, 1 to 80.
    ('vol_scan_date', INT2),    # Volume Scan start date, days since 1/1/1970
    ('vol_scan_time', INT4),    # Volume Scan start time, sec since midnight
    ('product_date', INT2),     # Product Generation Date, days since 1/1/1970
    ('product_time', INT4),     # Product Generation Time, sec since midnight
    ('halfwords_27_28', '4s'),  # Product dependent parameters 1 and 2
    ('elevation_num', INT2),    # Elevation number within volume scan
    ('halfwords_30', '2s'),     # Product dependent parameter 3
    ('threshold_data', '32s'),  # Data to determine threshold level values
    ('halfwords_47_53', '14s'),  # Product dependent parameters 4-10
    ('version', BYTE),          # Version, 0
    ('spot_blank', BYTE),       # 1 = Spot blank ON, 0 = Blanking OFF
    ('offet_symbology', INT4),  # halfword offset to Symbology block
    ('offset_graphic', INT4),   # halfword offset to Graphic block
    ('offset_tabular', INT4)    # halfword offset to Tabular block
)
# Graphic Product Message: Product Symbology Block
# Description
# 16 byte header
# Figure 3-6 (Sheet 8), pages 3-40

SYMBOLOGY_HEADER = (
    ('divider', INT2),          # Delineate blocks, -1
    ('id', INT2),               # Block ID, 1
    ('block_length', INT4),     # Length of block in bytes
    ('layers', INT2),           # Number of data layers
    ('layer_divider', INT2),    # Delineate data layers, -1
    ('layer_length', INT4)      # Length of data layer in bytes
    # Display data packets
)

# Digital Radial Data Array Packet - Packet Code 16 (Sheet 2)
# Figure 3-11c (Sheet 1 and 2), page 3-120.
# and
# Radial Data Packet - Packet Code AF1F
# Figure 3-10 (Sheet 1 and 2), page 3-113.
AF1F = -20705       # struct.unpack('>h', 'AF1F'.decode('hex'))
SUPPORTED_PACKET_CODES = [16, AF1F]       # elsewhere
RADIAL_PACKET_HEADER = (
    ('packet_code', INT2),      # Packet Code, Type 16
    ('first_bin', INT2),        # Location of first range bin.
    ('nbins', INT2),            # Number of range bins.
    ('i_sweep_center', INT2),   # I coordinate of center of sweep.
    ('j_sweep_center', INT2),   # J coordinate of center of sweep.
    ('range_scale', INT2),      # Range Scale factor
    ('nradials', INT2)          # Total number of radials in the product
)

RADIAL_HEADER = (
    ('nbytes', INT2),           # Number of bytes in the radial.
    ('angle_start', INT2),      # Starting angle at which data was collected.
    ('angle_delta', INT2)       # Delta angle from previous radial.
)
         
class L3F(NEXRADLevel3File):
    """
    Short convenience class alias
    """
    None
