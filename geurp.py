"""Silly module to parse/alter files, grep style.

The goal of this module is to have a simple interface to do grep-style and
in-place alterations to files allowing each line to be either completely
removed or replaced by multiple lines.

Use example:

    # For every .txt file in recipes/, replace apple by lemon.
    import geurp

    def derper(line):
        return [ line.replace("apple", "lemon") ]

    geurp.derp("recipes/*.txt", derper)

"""
from __future__ import with_statement
import glob

def derp(glob_pattern, func):
    for filename in glob.glob(glob_pattern):
        with open(filename) as fp_read:
            with open("output/" + filename, "w") as fp_write:
                for i, line in enumerate(fp_read):
                    fp_write.writelines(func(line))

