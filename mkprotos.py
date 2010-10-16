#!/usr/bin/env python3
"""Create prototypes for all the function dumped on stdin.

This is typically used in vim where you would copy all the functions of a file
in your .h file, select them, hit ":" and type: !mkprotos

"""
import sys
import re

# Number of tabs after the type
ptabs = 3

if len(sys.argv) > 1:
    fp = open(sys.argv[1])
else:
    fp = sys.stdin

data = re.findall(r"^(.*)\n([\w_]+)\((.*)\)", fp.read(), re.MULTILINE)

for group in data:
    # Handle the type
    type = group[0]
    ptr = ""
    while type.endswith("*"):
        ptr += "*"
        type = type[:-1]
    if not ptr:
        ptr = " "

    # Number of tabs after the type
    tabs = (ptabs - int(len(group[0]) / 8)) * "\t"

    # Parameters
    params = group[2].split(", ")
    cleaned = []
    width = len(group[1]) + 1
    for param in params:
        tokens = param.split(" ")
        varname = tokens[-1]
        if varname.startswith("*"):
            tokens[-1] = "*"
        else:
            del tokens[-1]
        cparam = " ".join(tokens)
        if width + len(cparam) >= 50:
            cparam = "\n\t" + ("\t" * ptabs) + cparam
            width = 8
        else:
            width += len(cparam) + 2
        cleaned.append(cparam)

    print("%s%s%s%s(%s);" % (group[0], tabs, ptr, group[1], ", ".join(cleaned)))

