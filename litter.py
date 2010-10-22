#!/usr/bin/python
"""Monitor the cat litter changes.

This little script reads a ~/.litterrc JSON file and returns the last time
you changed your cat's litter.

"""
from __future__ import with_statement
import os.path
import datetime
import math
import simplejson as json
import sys
import re


now = datetime.datetime.now()
date_format = "%Y-%m-%d %H:%M:%S"
config_file = os.path.expanduser(".litterrc")


def get_since_datetime(dt):
    """Return a string expressing the time passed since a given datetime."""
    output = ""
    delta = now - dt
    seconds = delta.seconds
    if delta.days > 0:
        seconds += delta.days * 24 * 3600

    delta = seconds
    print(delta)

    if delta >= 172800:
        output += "%d days " % math.floor(delta / 86400.0)
        delta = delta % 86400

    if delta >= 3600:
        output += "%d hours " % (delta / 3600.0)
        delta = delta % 3600

    if delta >= 60:
        output += "%d minutes " % (delta / 60.0)
        delta = delta % 60

    if delta > 0:
        output += "%d seconds " % delta

    return output


if __name__ == '__main__':
    # Load the current data
    if os.path.exists(config_file):
        with open(config_file) as fp:
            current = json.load(fp)
    else:
        current = {"litter_changes": []}

    # Obtain the last change
    changes = current["litter_changes"]
    last_change = None
    if changes:
        changes.sort(key=lambda x: x["date"])
        last_change = changes[-1]

    if len(sys.argv) > 1:
        # Change was done
        if sys.argv[1] == "now":
            if last_change:
                name = last_change["person"]
                type = last_change["type"]
            else:
                name = "Anonymous"
                type = "Brand X Litter"

            new_name = raw_input("Who (default: %s): " % name)
            new_type = raw_input("Type (default: %s): " % type)

            if new_name:
                name = new_name
            if new_type:
                type = new_type

            changes.append({
                "date": now.strftime(date_format),
                "person": name,
                "type": type
            })

            current["litter_changes"] = changes

            # Do the save in two steps to avoid saving a corrupted JSON
            dump_data = json.dumps(current, indent=4)
            with open(config_file, "w") as fp:
                fp.write(dump_data)

            next_date = (now + datetime.timedelta(5)).strftime("%A %B %d")
            print("Next change on " + next_date)

        # Help
        else:
            print("usage: litter [-h] [now]")

    # Just show
    else:
        date = datetime.datetime.strptime(last_change["date"], date_format)
        print("Last changed %sago" % get_since_datetime(date))


