from gerrit.api import get_changes_list


def review(ssh, args):
    # Stub
    pass


def set_topic(ssh, args):
    changes = get_changes_list(ssh, args)

    for change in changes:
        print(f"Setting topic for change: {change}")
        command = f"gerrit set-topic {change} --topic {args.topic}"
        ssh.exec_command(command)
