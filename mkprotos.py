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

data = re.findall(r"(/\*\*.+?\*/)?\s+([^\n\t;\{\}=/\*]+\**)\s+([\w_]+)\s?\(([^\)]*?)\)$", fp.read(),
        re.MULTILINE | re.DOTALL)

for group in data:
    # Doctype
    if "@private" in group[0]:
        continue

    # Handle the type
    type = group[1]
    ptr = ""
    while type.endswith("*"):
        ptr += "*"
        type = type[:-1]
    if not ptr:
        ptr = " "

    # Number of tabs after the type
    tabs = (ptabs - int(len(type) / 8)) * "\t"

    # Parameters
    params = re.split(",\s+", group[3])
    cleaned = []
    width = len(group[2]) + 1
    for param in params:
        tokens = param.split(" ")
        varname = tokens[-1]
        if varname.startswith("*"):
            tokens[-1] = "*"
        else:
            del tokens[-1]
        cparam = " ".join(tokens)
        if width + len(cparam) >= 53:
            cparam = "\n\t" + ("\t" * ptabs) + cparam
            width = 8

        width += len(cparam) + 2
        cleaned.append(cparam)

    print("%s%s%s%s(%s);" % (type, tabs, ptr, group[2], ", ".join(cleaned)))

