================
 Random Scripts
================

This is a collection of scattered scripts that do not need to be packaged
individually. Feel free to use them and update them, they are all licensed
under the ISC-License.

mkprotos.py
===========
Create all the prototypes for a bunch of C functions. This is typically used in
vim where you would copy all the functions of a file in your .h file, select
them, hit ":" and type: !mkprotos.py

Another faster way to do it is to go in your header file and hit::
    :r!mkprotos.py myfile.c
which will insert directly the prototypes in your header file.

Note that all the function with @private in their docstring will not be 
included in the header.

fusic.py
========

This small script makes use of the fact that the LG Fusic phone shows up as a
serial device when plugged on a Linux box. It returns a few details about the
identity of the phone (manufacturer, model, revision and serial number) but
also the battery level and the signal strength.

litter.py
=========

Keep track of when the cat's litter was done using ~/.litterrc as a JSON list.

Example::

    $ litter.py
    Last changed 4 days 3 hours 44 minutes ago

    $ litter.py now
    Who (default: LastPerson): 
    Type (default: Random Brand): 
    Next change on Wednesday October 27

psdfontlist.py
==============

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

geurp.py
========

Silly module to parse/alter files, grep style.

The goal of this module is to have a simple interface to do grep-style and
in-place alterations to files allowing each line to be either completely
removed or replaced by multiple lines.

Use example::

    # For every .txt file in recipes/, replace apple by lemon.
    import geurp

    def derper(line):
        return [ line.replace("apple", "lemon") ]

    geurp.derp("recipes/*.txt", derper)

playrar.sh
==========

This script is used to play a movie out of a series of RAR files. This is
particularily useful when downloading a movie in the right order since it
allows you to start watching the movie almost as soon as you start your
download.

Usage example::

    playrar random_movie.part01.rar

