from gerrit.api import get_changes_list


def review(ssh, args):
    changes = get_changes_list(ssh, args, action="review")
    review_query = []

    if args.abandon:
        review_query.append("--abandon")

    if args.code_review:
        review_query.append(f"--code-review {args.code_review}")

    if args.verified:
        review_query.append(f"--verified {args.verified}")

    for change in changes:
        command = f"gerrit review {' '.join(review_query)} {change}"
        print(command)
        ssh.exec_command(command)


def set_topic(ssh, args):
    changes = get_changes_list(ssh, args, action="set_topic")

    for change in changes:
        print(f"Setting topic for change: {change}")
        command = f"gerrit set-topic {change} --topic {args.topic}"
        ssh.exec_command(command)
