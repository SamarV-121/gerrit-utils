#!/usr/bin/env python3
import argparse
import paramiko
import sys
from gerrit import actions

GERRIT = "review.leafos.org"
PORT = "29418"
USER = "SamarV-121"


def add_common_args(parser):
    parser.add_argument("-c", "--change", type=int, nargs="+", help="Change number(s)")
    parser.add_argument(
        "-cc",
        "--changes",
        type=int,
        nargs=2,
        metavar=("CHANGE1", "CHANGE2"),
        help="Specify range of changes",
    )
    parser.add_argument("-q", "--query", help="Pass a gerrit query")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gerrit", default=GERRIT, help="Gerrit server URL")
    parser.add_argument(
        "-p", "--port", default=PORT, type=int, help="Gerrit server port number"
    )
    parser.add_argument("-u", "--user", default=USER, help="Gerrit user")

    subparsers = parser.add_subparsers(title="abilities", dest="subcommand")

    # Review
    review_parser = subparsers.add_parser("review", help="Review gerrit changes")
    review_parser.add_argument(
        "-a", "--abandon", action="store_true", help="Abandon the change"
    )
    review_parser.add_argument(
        "-cr",
        "--code-review",
        choices={"-2", "-1", "0", "+1", "+2"},
        help="Code review",
    )
    review_parser.add_argument(
        "-v",
        "--verified",
        choices={"-1", "0", "+1"},
        help="Verify the change",
    )
    add_common_args(review_parser)

    # Topic
    topic_parser = subparsers.add_parser("topic", help="Set topic")
    topic_parser.add_argument("-t", "--topic", help="Set topic")
    add_common_args(topic_parser)

    return parser.parse_args(args=None if sys.argv[1:] else ["-h"])


def main():
    args = parse_args()

    # SSH connect
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(args.gerrit, port=args.port, username=args.user)

    match args.subcommand:
        case "review":
            actions.review(ssh, args)
        case "topic":
            actions.set_topic(ssh, args)

    ssh.close()


if __name__ == "__main__":
    main()
