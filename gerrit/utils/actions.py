#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
from git import Repo
from gerrit.utils.api import get_changes_list


def push(args):
    repo = Repo(args.path)
    refspec = []

    remote = args.remote or repo.remote().name
    branch = args.branch or repo.active_branch.name
    ref = args.ref or "for"
    commit = args.commit or "HEAD"

    def add_refspec(spec):
        sep = "%" if len(refspec) == 0 else ","
        refspec.append(f"{sep}{spec}")

    if args.code_review:
        add_refspec(f"l=Code-Review{args.code_review}")

    if args.verified:
        add_refspec(f"l=Verified{args.verified}")

    if args.topic:
        add_refspec(f"topic={args.topic}")

    if args.reviewer:
        add_refspec(f"r={args.reviewer}")

    if args.cc:
        add_refspec(f"cc={args.cc}")

    if args.private:
        add_refspec("private")

    if args.remove_private:
        add_refspec("remove-private")

    if args.wip:
        add_refspec("wip")

    if args.ready:
        add_refspec("ready")

    if args.merge:
        commit_info = repo.git.show(args.merge, "--pretty=%P").split()
        base_args = f"base={commit_info[0]},base={commit_info[1]}"
        add_refspec("".join(base_args))

    command = [remote, f'{commit}:refs/{ref}/{branch}{"".join(refspec)}']

    if args.thin:
        command.append("--no-thin")

    if ref == "heads":
        command.append("-o skip-validation")

    if not args.quiet:
        print(f"Running git push {command}")

    repo.git.push(command)


def review(ssh, args):
    changes = get_changes_list(ssh, args, action="review")
    review_query = []

    if args.abandon:
        review_query.append("--abandon")

    if args.restore:
        review_query.append("--restore")

    if args.submit:
        review_query.append("--submit")

    if args.message:
        review_query.append(f"--message {args.message}")

    if args.code_review:
        review_query.append(f"--code-review {args.code_review}")

    if args.verified:
        review_query.append(f"--verified {args.verified}")

    for change in changes:
        command = f"gerrit review {' '.join(review_query)} {change}"
        if not args.quiet:
            print(command)
        ssh.exec_command(command)


def set_reviewers(ssh, args):
    changes = get_changes_list(ssh, args, action="set_reviewers")
    reviewers = []

    if args.add:
        reviewers.append(f"--add {args.add}")

    if args.remove:
        reviewers.append(f"--remove {args.remove}")

    for change in changes:
        command = f"gerrit set-reviewers {' '.join(reviewers)} {change}"
        if not args.quiet:
            print(command)
        ssh.exec_command(command)


def set_topic(ssh, args):
    changes = get_changes_list(ssh, args, action="set_topic")

    for change in changes:
        command = f"gerrit set-topic {change} --topic {args.topic_name}"
        if not args.quiet:
            print(command)
        ssh.exec_command(command)
