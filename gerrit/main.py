#!/usr/bin/env python3
#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
import argparse
import os
import sys
import paramiko
from gerrit.utils import actions

GERRIT = os.environ.get("GERRIT_SERVER")
USER = os.environ.get("GERRIT_USERNAME")
PORT = "29418"


def ssh_connection_required(exclude):
    def decorator(func):
        def wrapper(parsed_args, ssh):
            if parsed_args.subcommand in exclude:
                func(parsed_args, None)
            else:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(parsed_args.gerrit, parsed_args.port, parsed_args.user)
                func(parsed_args, ssh)
                ssh.close()

        return wrapper

    return decorator


def formatter(prog):
    return argparse.HelpFormatter(prog, max_help_position=52)


def add_common_args(parser, ops=None):
    parser.add_argument(
        "--quiet", action="store_true", default=False, help="Silence the output"
    )
    parser.add_argument(
        "-g",
        "--gerrit",
        default=GERRIT,
        help="Specify the Gerrit server URL (default: %(default)s)",
        required=GERRIT is None,
    )
    parser.add_argument(
        "-p",
        "--port",
        default=PORT,
        type=int,
        help="Specify the Gerrit server port number (default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--user",
        default=USER,
        help="Specify the Gerrit user (default: %(default)s)",
        required=USER is None,
    )
    common_group = parser.add_mutually_exclusive_group(required=True)
    common_group.add_argument(
        "-c", "--change", type=int, nargs="+", help="Specify the change number(s)"
    )
    common_group.add_argument(
        "--range",
        type=int,
        nargs=2,
        metavar=("CHANGE1", "CHANGE2"),
        help="Specify a range of changes",
    )
    common_group.add_argument(
        "-q",
        "--query",
        help='Specify a Gerrit query (Initialize with "-" to exclude changes eg. -topic:foo -420)',
    )
    if ops != "topic":
        common_group.add_argument("-t", "--topic", help="Specify a topic name")
    parser.add_argument(
        "--timeout",
        default=0,
        type=int,
        help="Specify the time interval (in seconds) between SSH commands (default: %(default)s)",
    )


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=formatter)
    subparsers = parser.add_subparsers(title="abilities", dest="subcommand")

    # Push
    push_parser = subparsers.add_parser(
        "push", help="Push changes to Gerrit", formatter_class=formatter
    )
    push_parser.add_argument(
        "--quiet", action="store_true", default=False, help="Silence the output"
    )
    push_parser.add_argument(
        "--path",
        default=".",
        help="Specify the local path of repo",
    )
    push_parser.add_argument("-b", "--branch", help="Specify the branch name")
    push_parser.add_argument("-c", "--commit", help="Specify the commit hash id")
    push_parser.add_argument(
        "-r",
        "--remote",
        default="gerrit",
        help="Specify the remote (default: %(default)s)",
    )
    push_parser.add_argument("--ref", help="Specify the ref type")
    push_parser.add_argument("-t", "--topic", help="Specify a topic")
    push_parser.add_argument(
        "-cr",
        "--code-review",
        choices={"-2", "-1", "0", "+1", "+2"},
        help="Code review",
    )
    push_parser.add_argument(
        "-v",
        "--verified",
        choices={"-1", "0", "+1"},
        help="Verify the change",
    )
    push_parser.add_argument(
        "-m", "--merge", help="Push a merge on Gerrit", metavar="MERGE_COMMIT"
    )
    push_parser.add_argument(
        "-n",
        "--no-thin",
        dest="thin",
        action="store_true",
        help="Disable thin optimizations while pushing",
    )
    push_parser.add_argument("--reviewer", help="Assign a reviewer")
    push_parser.add_argument("--cc", help="CC additional recipients")
    private_group = push_parser.add_mutually_exclusive_group()
    private_group.add_argument(
        "--private",
        action="store_true",
        help="Set the change visibility to private",
    )
    private_group.add_argument(
        "--remove-private",
        action="store_true",
        help="Set the change visibility to public",
    )
    wip_group = push_parser.add_mutually_exclusive_group()
    wip_group.add_argument(
        "--wip", action="store_true", help="Mark the change as work in progress"
    )
    wip_group.add_argument(
        "--ready", action="store_true", help="Mark the change as ready for reviewing"
    )

    # Review
    review_parser = subparsers.add_parser(
        "review", help="Review gerrit changes", formatter_class=formatter
    )
    add_common_args(review_parser)
    review_group = review_parser.add_mutually_exclusive_group()
    review_group.add_argument(
        "-a", "--abandon", action="store_true", help="Abandon the change"
    )
    review_group.add_argument(
        "-r", "--restore", action="store_true", help="Restore the change"
    )
    review_group.add_argument(
        "-s", "--submit", action="store_true", help="Submit the change"
    )
    review_parser.add_argument("-m", "--message", help="Post a message on the change")
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

    # Reviewers
    reviewer_parser = subparsers.add_parser(
        "set-reviewers", help="Assign reviewers", formatter_class=formatter
    )
    add_common_args(reviewer_parser)
    reviewer_parser.add_argument("-a", "--add", help="Add reviewer to the change")
    reviewer_parser.add_argument(
        "-r", "--remove", help="Remove reviewer from the change"
    )

    # Topic
    topic_parser = subparsers.add_parser(
        "topic", help="Set topic", formatter_class=formatter
    )
    add_common_args(topic_parser, ops="topic")
    topic_parser.add_argument("-t", "--topic", dest="topic_name", help="Set topic")

    return parser.parse_args(args=None if sys.argv[1:] else ["-h"])


@ssh_connection_required(exclude="push")
def main(parsed_args, ssh):
    if parsed_args.subcommand == "push":
        actions.push(parsed_args)
    elif parsed_args.subcommand == "review":
        actions.review(ssh, parsed_args)
    elif parsed_args.subcommand == "set-reviewers":
        actions.set_reviewers(ssh, parsed_args)
    elif parsed_args.subcommand == "topic":
        actions.set_topic(ssh, parsed_args)


if __name__ == "__main__":
    args = parse_args()
    main(args, None)
