#!/usr/bin/env python3
import argparse
import sys
import paramiko
from gerrit import actions

GERRIT = "review.leafos.org"
PORT = "29418"
USER = "SamarV-121"


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


def add_common_args(parser):
    parser.add_argument("-g", "--gerrit", default=GERRIT, help="Gerrit server URL")
    parser.add_argument(
        "-p", "--port", default=PORT, type=int, help="Gerrit server port number"
    )
    parser.add_argument("-u", "--user", default=USER, help="Gerrit user")
    parser.add_argument("-c", "--change", type=int, nargs="+", help="Change number(s)")
    parser.add_argument(
        "--changes",
        type=int,
        nargs=2,
        metavar=("CHANGE1", "CHANGE2"),
        help="Specify range of changes",
    )
    parser.add_argument("-q", "--query", help="Pass a gerrit query")


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="abilities", dest="subcommand")

    # Push
    push_parser = subparsers.add_parser("push", help="Push changes to gerrit")
    push_parser.add_argument("--path", default=".", help="Push changes")
    push_parser.add_argument("-b", "--branch", help="Specify the branch name")
    push_parser.add_argument("-c", "--commit", help="Commit hash id")
    push_parser.add_argument("-r", "--remote", help="Specify the remote")
    push_parser.add_argument("--ref", help="Specify the ref type")
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
    push_parser.add_argument("-t", "--topic", help="Set a topic")
    push_parser.add_argument("-m", "--merge", help="Push a merge on gerrit")
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
        help="Set private visibility to the change",
    )
    private_group.add_argument(
        "--remove_private",
        action="store_true",
        help="Set public visibility to the change",
    )
    wip_group = push_parser.add_mutually_exclusive_group()
    wip_group.add_argument("--wip", action="store_true", help="Mark change as wip")
    wip_group.add_argument(
        "--ready", action="store_true", help="Mark change ready for reviewing"
    )

    # Review
    review_parser = subparsers.add_parser("review", help="Review gerrit changes")
    add_common_args(review_parser)
    review_parser.add_argument("-t", "--topic", help="Review a whole topic")
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
    reviewer_parser = subparsers.add_parser("set-reviewers", help="Assign reviewers")
    add_common_args(reviewer_parser)
    reviewer_parser.add_argument("-a", "--add", help="Set reviewer to the change")
    reviewer_parser.add_argument(
        "-r", "--remove", help="Remove reviewer from the change"
    )

    # Topic
    topic_parser = subparsers.add_parser("topic", help="Set topic")
    add_common_args(topic_parser)
    topic_parser.add_argument("-t", "--topic", help="Set topic")

    return parser.parse_args(args=None if sys.argv[1:] else ["-h"])


@ssh_connection_required(exclude="push")
def main(parsed_args, ssh):
    match parsed_args.subcommand:
        case "push":
            actions.push(parsed_args)
        case "review":
            actions.review(ssh, parsed_args)
        case "set-reviewers":
            actions.set_reviewers(ssh, parsed_args)
        case "topic":
            actions.set_topic(ssh, parsed_args)


if __name__ == "__main__":
    args = parse_args()
    main(args, None)
