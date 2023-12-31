from gerrit.api import get_changes_list


def review(ssh, args):
    changes = get_changes_list(ssh, args, action="review")

    if args.abandon:
        review_query = "--abandon"
    elif args.code_review:
        review_query = f"--code-review {args.code_review}"
    elif args.verified:
        review_query = f"--verified {args.verified}"

    for change in changes:
        print(f"{args.review}: {change}")
        command = f"gerrit review {review_query} {change}"
        ssh.exec_command(command)


def set_topic(ssh, args):
    changes = get_changes_list(ssh, args, action="set_topic")

    for change in changes:
        print(f"Setting topic for change: {change}")
        command = f"gerrit set-topic {change} --topic {args.topic}"
        ssh.exec_command(command)
