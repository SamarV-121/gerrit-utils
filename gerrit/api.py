import requests
import json


def get_change_info(gerrit_url, change_num):
    ret = requests.get(f"https://{gerrit_url}/changes/{change_num}?o=CURRENT_REVISION")
    return json.loads(ret.text.split("\n")[1])


def get_chained_changes(gerrit_url, change_num):
    change_info = get_change_info(gerrit_url, change_num)
    id = change_info["id"]
    commit = change_info["current_revision"]
    ret = requests.get(f"https://{gerrit_url}/changes/{id}/revisions/{commit}/related")
    return json.loads(ret.text.split("\n")[1])["changes"]


def get_trimmed_changes(gerrit_url, change_num1, change_num2):
    startIdx, endIdx = None, None
    changes = get_chained_changes(gerrit_url, change_num1)

    for i, change in enumerate(changes):
        if change["_change_number"] == change_num1:
            startIdx = i
        if change["_change_number"] == change_num2:
            endIdx = i
        if startIdx is not None and endIdx is not None:
            return changes[endIdx : startIdx + 1]

    return []


def get_changes_list(ssh, args):
    if args.change:
        return args.change
    elif args.changes:
        return [
            change["_change_number"]
            for change in get_trimmed_changes(
                args.gerrit, args.changes[0], args.changes[1]
            )
        ]
    elif args.query:
        changes = []
        command = f"gerrit query {args.query} --current-patch-set --format=JSON"
        stdin, stdout, stderr = ssh.exec_command(command)

        for change_json in stdout:
            change = json.loads(change_json)

            if change.get("number"):
                changes.append(change["number"])

        return changes
