================
 Random Scripts
================

This is a collection of scattered scripts that do not need to be packaged
individually. Feel free to use them and update them, they are all licensed
under the ISC-License.

fusic.py
========

This small script makes use of the fact that the LG Fusic phone shows up as a
serial device when plugged on a Linux box. It returns a few details about the
identity of the phone (manufacturer, model, revision and serial number) but
also the battery level and the signal strength.

psdfontlist
===========

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

