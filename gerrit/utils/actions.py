#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
import time
from git import Repo
from gerrit.utils.api import get_changes_list


def ssh_exec(ssh, args, action, query):
    changes = get_changes_list(ssh, args, action)

    for idx, change in enumerate(changes):
        command = f"gerrit {action} {query} {change}"
        if not args.quiet:
            print(command)
        _, _, stderr = ssh.exec_command(command)
        if err := stderr.read().decode("utf-8"):
            print(err)
        if idx < len(changes) - 1:
            time.sleep(args.timeout)


def push(args):
    repo = Repo(args.path)
    refspec = []

    remote = args.remote or repo.remote().name
    branch = args.branch or repo.active_branch.name
    ref = args.ref or "for"
    commit = args.commit or "HEAD"
    commit = repo.git.rev_parse(commit)

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
        add_refspec(base_args)

    command = [remote, f'{commit}:refs/{ref}/{branch}{"".join(refspec)}']

    if args.thin:
        command.append("--no-thin")

    if args.force:
        command.append("-f")

    if ref == "heads":
        command.append("-o skip-validation")

    last_commit = None

    if args.multiple_merge:
        base_commit = args.multiple_merge
        commits = repo.git.log(
            "--reverse",
            "--first-parent",
            "--format=%H",
            f"{base_commit}..{commit}",
        ).split("\n")

        merge_commits = repo.git.log(
            "--reverse",
            "--merges",
            "--first-parent",
            "--format=%H",
            f"{base_commit}..{commit}",
        ).split("\n")

        last_commit = repo.git.rev_parse(commits[-1])
        normal_commits = []

        refspec_copy = refspec.copy()
        command_copy = command.copy()
        for commit in commits:
            current_command = command_copy
            if commit in merge_commits:
                # Push normal commits before merges
                if normal_commits:
                    latest_normal_commit = normal_commits[-1]
                    current_command[1] = f"{latest_normal_commit}:refs/{ref}/{branch}"

                    if not args.quiet:
                        print(f"Running git push {current_command}")

                    repo.git.push(current_command)
                    normal_commits = []

                # Push merges
                if not args.quiet:
                    print("Merge commit detected")
                commit_info = repo.git.show(commit, "--pretty=%P").split()
                base_args = f"base={commit_info[0]},base={commit_info[1]}"
                refspec = refspec_copy.copy()
                add_refspec(base_args)

                current_command[1] = f'{commit}:refs/{ref}/{branch}{"".join(refspec)}'

                if not args.quiet:
                    print(f"Running git push {current_command}")

                repo.git.push(current_command)
            else:
                normal_commits.append(commit)

    if last_commit == commit:
        return

    if not args.quiet:
        print(f"Running git push {command}")

    repo.git.push(command)


def review(ssh, args):
    review_query = []

    if args.abandon:
        review_query.append("--abandon")

    if args.restore:
        review_query.append("--restore")

    if args.submit:
        review_query.append("--submit")

    if args.message:
        review_query.append(f'--message "{args.message}"')

    if args.code_review:
        review_query.append(f"--code-review {args.code_review}")

    if args.verified:
        review_query.append(f"--verified {args.verified}")

    final_query = " ".join(review_query)
    ssh_exec(ssh, args, action="review", query=final_query)


def set_reviewers(ssh, args):
    reviewers = []

    if args.add:
        reviewers.append(f"--add {args.add}")

    if args.remove:
        reviewers.append(f"--remove {args.remove}")

    final_query = " ".join(reviewers)
    ssh_exec(ssh, args, action="set-reviewers", query=final_query)


def set_topic(ssh, args):
    final_query = f"--topic {args.topic_name}"
    ssh_exec(ssh, args, action="set-topic", query=final_query)
