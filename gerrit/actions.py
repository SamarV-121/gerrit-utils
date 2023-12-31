from gerrit.api import get_changes_list


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
        print(command)
        ssh.exec_command(command)


def set_topic(ssh, args):
    changes = get_changes_list(ssh, args, action="set_topic")

    for change in changes:
        command = f"gerrit set-topic {change} --topic {args.topic}"
        print(command)
        ssh.exec_command(command)
