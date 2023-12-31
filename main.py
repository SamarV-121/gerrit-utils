#!/usr/bin/env python3
import argparse
import paramiko
import sys
from gerrit import actions

GERRIT = "review.leafos.org"
PORT = "29418"
USER = "SamarV-121"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--change", type=int, nargs="+", help="Change number(s)")
    parser.add_argument(
        "-cc",
        "--changes",
        type=int,
        nargs=2,
        metavar=("CHANGE1", "CHANGE2"),
        help="Specify range of changes",
    )
    parser.add_argument("-g", "--gerrit", default=GERRIT, help="Gerrit server URL")
    parser.add_argument(
        "-p", "--port", default=PORT, type=int, help="Gerrit server port number"
    )
    parser.add_argument("-q", "--query", help="Pass a gerrit query")
    parser.add_argument("-r", "--review", help="Review gerrit changes")
    parser.add_argument("-t", "--topic", help="Set topic")
    parser.add_argument("-u", "--user", default=USER, help="Gerrit user")

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(args.gerrit, port=args.port, username=args.user)

    if args.review:
        actions.review(ssh, args)
    elif args.topic:
        actions.set_topic(ssh, args)

    ssh.close()


if __name__ == "__main__":
    main()
