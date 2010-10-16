#!/usr/bin/python
"""Create prototypes for all the C functions dumped on stdin.

This is typically used in vim where you would copy all the functions of a file
in your .h file, select them, hit ":" and type: !mkprotos

"""
import sys
import re

# Number of tabs after the type
ptabs = 3

# Read from stdin or first argument
if len(sys.argv) > 1:
    fp = open(sys.argv[1])
else:
    fp = sys.stdin

# Find all the function definitions
data = re.findall(r"""
    (/\*\*.+?\*/)?          # First group, the comment block
    \s+                     # Newline, crumbs...
    ([^\n\t;\{\}=/\*]+\**)  # Second group, the type
    \s+                     # Newline, crumbs...
    ([\w_]+)                # Third group, function name
    \s?                     # Optional space between function name and params
    \(                      # Start of the params
    ([^\)]*?)               # Fourth group, actual params on multiple lines
    \)$                     # End of the params
    """, fp.read(), re.MULTILINE | re.DOTALL | re.VERBOSE)

for comment, type, name, params in data:
    # Ignore @private and static functions
    if "@private" in comment or "static" in type:
        continue

    # Handle the type
    ptr = ""
    while type.endswith("*"):
        ptr += "*"
        type = type[:-1]
    if not ptr:
        ptr = " "

    # Number of tabs after the type
    tabs = (ptabs - int(len(type) / 8)) * "\t"

    # Parameters, split them with the commas, remove all the actual variable
    # names to keep only the types.
    if not params:
        params = "void"
    else:
        params = re.split("\s*,\s+", params)
        cleaned = []
        width = len(name) + 1
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
        params = ", ".join(cleaned)

    print("%s%s%s%s(%s);" % (type, tabs, ptr, name, params))

