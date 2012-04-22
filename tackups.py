#!/usr/bin/env python

"""
Simplistic backup system wrapping gnupg, gzip, cpio, find and Amazon S3.

The whole point of this tool is to simplify the storage format and avoid the
need for extra tools to restore from backups. All you need to restore an
archive is::

    gpg -d $file | gzip | cpio -id

"Incremental" backups are handled manually, in most cases, this can be done by
simply specifying partial backups based on find rules, for example, backing up
a folder of Maildir folders:

- hourly saving only the last 24H of inbox/ and sent/
- daily saving everything except archived folders
- weekly saving everything.

This script assumes the AWS keys are stored in the configuration file, the
reason for this choice is simple, you should setup a user for each machine (or
class of machine) and only give "PutObject" rights to this user, the global
AWS_ variables are typically user specific, not task specific.

Here is an example configuration file (YAML)::

    aws_access_key_id:      "AK.................."
    aws_secret_access_key:  "........................................"

    gpg_recipient:          "6453194A"

    target_bucket_name:     "backups.hostname.tamentis.com"

    periods:
        hourly:
            include:
                - "mail/inbox"
                - "mail/sent"
                - "mail/work/inbox"
                - "mail/work/sent"
            include_options:
                ctime: 1

        daily:
            include:
                - "projects"
                - "mail"
            exclude:
                - "^mail/archives"

        weekly:
            include:
                - "projects"
                - "mail"

Here is an example of the usage in a crontab(5)::

    @hourly tackups.py /etc/tackups.conf hourly
    @daily tackups.py /etc/tackups.conf daily
    @weekly tackups.py /etc/tackups.conf weekly
"""

import os
import sys
import argparse
from datetime import datetime

import yaml
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def cmd_find(paths, options):
    """Return a find shell command for all the given paths."""
    options = ["-{} {}".format(opt,  value) for opt, value in options.items()]
    return "find {} {}".format(" ".join(paths), " ".join(options))


def cmd_greps(paths):
    """Return a bunch of grep exclusion commands for all the given paths."""
    return ["grep -v {}".format(p) for p in paths]


def cmd_gpg_encode(recipient):
    return "gpg -e -r {}".format(recipient)


def create_file(period_name):
    """Create a backup file using the given period configuration.

    This function assumes a ``config`` dictionary was previously loaded.

    :param period_name: Key in the configuration to a period configuration.

    """
    filename = "backup_{}.cpio.gz.gpg".format(period_name)
    periods = config["periods"]
    period = periods[period_name]

    if verbose:
        print("creating backup file '{}'".format(filename))

    include_options = period.get("include_options", {})

    cmds = [cmd_find(period["include"], include_options)]

    if "exclude" in period:
        cmds += cmd_greps(period["exclude"])

    cmds += [
        "cpio -o",
        "gzip",
        cmd_gpg_encode(config["gpg_recipient"]),
    ]

    cmd = "{} > {}".format(" | ".join(cmds), filename)

    if os.system(cmd) != 0:
        print("error running '{}'".format(cmd))
        sys.exit(3)

    return filename


def upload(filename, bucket_name):
    """Upload a file to a bucket.

    The key will be the name of the file by default (stripping the whole path).

    :param filename: Path to the file to be uploaded.
    :param bucket_name: Name of the bucket.

    """
    if verbose:
        print("saving file to S3 ({})".format(bucket_name))

    conn = S3Connection(config["aws_access_key_id"],
                        config["aws_secret_access_key"])

    bucket = conn.get_bucket(bucket_name, validate=False)

    k = Key(bucket)
    k.key = os.path.basename(filename)
    k.set_contents_from_filename(filename)


def parse_options():
    """Extract options from the command-line.

    Print usage and exists if anything is wrong.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=argparse.FileType("r"),
                        help="where to find the config and period definitions")
    parser.add_argument("period", help="period definition in the config file")
    parser.add_argument("-v", dest="verbose", action="store_true",
                        default=False, help="verbose")
    args = parser.parse_args()

    config = yaml.safe_load(args.config_file)

    if args.period not in config["periods"]:
        print("error: unknown period '{}'".format(args.period))
        sys.exit(2)

    return args.verbose, args.period, config


# Extract options from the command line.
verbose, period, config = parse_options()

# Run GnuPG, Gzip, etc. and create a backup file.
filename = create_file(period)

# Save the file to an S3 key.
upload(filename, config["target_bucket_name"])

