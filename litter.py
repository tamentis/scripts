#!/usr/bin/python

"""Monitor the cat litter changes.

This little script reads a ~/.litterrc JSON file and returns the last time
you changed your cat's litter.

usage: litter [-c] [-h] [now]

All arguments are short. The final keyword 'now' is to be added only when
actually resetting the counter.

  -c        cron mode, returns 1 and a message when the litter is overdue.
  -h        help
"""

from __future__ import with_statement
import os.path
import datetime
import math
import simplejson as json
import sys
import re


max_days = 5
now = datetime.datetime.now()
date_format = "%Y-%m-%d %H:%M:%S"
config_file = os.path.expanduser("~/.litterrc")


def get_since_datetime(dt):
    """Return a string expressing the time passed since a given datetime."""
    output = ""
    delta = now - dt
    seconds = delta.seconds
    if delta.days > 0:
        seconds += delta.days * 24 * 3600

    delta = seconds

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


def reset_counter(last_change):
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

    return (now + datetime.timedelta(max_days)).strftime("%A %B %d")


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

    # Check for cron-mode.
    if "-c" in sys.argv:
        date = datetime.datetime.strptime(last_change["date"], date_format)
        if (now - date).days >= max_days:
            print("Litter is overdue (done %sago)" % get_since_datetime(date))
            sys.exit(-1)
        else:
            sys.exit(0)

    # Explicit reset
    if sys.argv[-1] == "now":
        next_date = reset_counter(last_change)
        print("Next change on " + next_date)
        sys.exit(0)
    
    # No parameters left, show the last reset
    if len(sys.argv) == 1:
        date = datetime.datetime.strptime(last_change["date"], date_format)
        print("Last changed %sago" % get_since_datetime(date))
        sys.exit(0)

    # We've exhausted the possibilities, help!
    print(__doc__)
    sys.exit(-1)
