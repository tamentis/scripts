#!/usr/bin/env python3
"""psdfontlist - brute force font list for psd files

List all the fonts used within a Photosh*p file (PSD). You will need as much
RAM as possible since the whole file is loaded in memory before being read
byte by byte. I know this is not pretty, it is not meant to be, it works for
me (TM).

If a font is used multiple times, it will only be listed once. The only two
working options are::

    -h    help/usage
    -d    show parsing debug

And this is what you should expect out if it::

    $ psdfontlist myfile.pdf
    OneFont
    AnotherOne
    SomeRandomOtherFont
   
The default for decoding the font names is big endian UTF-16. If you have a
"BOM error":

 - open the ``codecs`` documentation,
 - add the new BOM (byte order mark) to match the data in your file,
 - send your patch
 - ???
 - profit

"""

__author__ = "Bertrand Janin <tamentis@neopulsar.org>"
__license__ = "ISC License"

import sys
import codecs

debug = False

if "-d" in sys.argv:
    sys.argv.remove("-d")
    debug = True

if len(sys.argv) != 2 or "-h" in sys.argv:
    print("usage: psdfontlist [-h] file.pdf")
    sys.exit(-1)

try:
    with open(sys.argv[1], "rb") as fp:
        data = fp.read()
except IOError as e:
    print("Unable to open this file.")
    sys.exit(-1)

fonts = [ ]

header_ascii = bytes("/FontSet [", "ascii")
prefix_ascii = bytes("/Name (", "ascii")
suffix_ascii = ord(")")
footer_ascii = ord("]")

capturing = False

for i in range(len(data)):
    # Looking for the header
    if data.startswith(header_ascii, i):
        if debug:
            print("found font set at {}".format(i))
        capturing = True

    # Looking for the footer
    if capturing and data[i] == footer_ascii:
        if debug:
            print("fount footer at {}".format(i))
        capturing = False

    # Capturing in between any /Name...
    if capturing:
        if data.startswith(prefix_ascii, i):
            bom_start = i + len(prefix_ascii)
            if data.startswith(codecs.BOM_UTF16_BE, bom_start):
                bom = codecs.BOM_UTF16_BE
                codec = "UTF-16BE"
            elif data.startswith(codecs.BOM_UTF8, bom_start):
                bom = codecs.BOM_UTF8
                codec = "UTF-8"
            else:
                raise ValueError("Unknown BOM.")
            fontname_start = bom_start + len(bom)
            fontname_end = data.index(bytes([suffix_ascii]), fontname_start)
            fontname_utf16 = data[fontname_start:fontname_end]
            fontname = str(fontname_utf16, codec)
            if fontname not in fonts:
                print(fontname)
                fonts.append(fontname)
            elif debug:
                print("{} (again)".format(fontname))

