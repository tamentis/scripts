#!/usr/bin/env python

"""
Scan authlog for abusers and add them to the <bruteforce> table.

This script only bothers with the latest authlog which is empty after log
rotation.  Because of that you should set the expiration of your <bruteforce>
table to 24 hours.  The following will do nicely in your /etc/daily::

    pfctl -t bruteforce -T expire 84600

And the following can go at the top of your pf.conf::

    table <bruteforce> persist
    block quick from <bruteforce>

And that will keep it running in the root crontab::

    */10 * * * * brute.py | xargs pfctl -t bruteforce -T add


"""

max_connections = 50

brutes = {}

with open("/var/log/authlog") as fp:
    for line in fp:
        tokens = line.strip().split()

        process = tokens[4]
        if not process.startswith("sshd"):
            continue

        if "Received disconnect from" not in line:
            continue

        # Legit users disconnecting are not abusing anything.
        if "disconnected by user" in line:
            continue

        ip = tokens[8].strip(":")
        brutes.setdefault(ip, 0)
        brutes[ip] += 1

brutes = sorted(brutes.items(), key=lambda b: b[1])

for ip, count in brutes:
    if count > max_connections:
        print("{}".format(ip, count))
