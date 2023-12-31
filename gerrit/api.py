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
    gerrit_url = args.gerrit
    if args.change:
        if args.topic:
            return args.change
        elif args.review:
            changes = []
            # review needs a patchset number as well
            for change in args.change:
                change_info = get_change_info(gerrit_url, change)

                for rev_id, rev_data in change_info["revisions"].items():
                    current_patchset = rev_data["_number"]

                changes.append(f"{change},{current_patchset}")

            return changes
    elif args.changes:
        change_num1, change_num2 = args.changes

        if args.topic:
            return [
                change["_change_number"]
                for change in get_trimmed_changes(gerrit_url, change_num1, change_num2)
            ]
        elif args.review:
            return [
                f'{change["_change_number"]},{change["_current_revision_number"]}'
                for change in get_trimmed_changes(gerrit_url, change_num1, change_num2)
            ]
    elif args.query:
        changes = []
        command = f"gerrit query {args.query} --current-patch-set --format=JSON"
        stdin, stdout, stderr = ssh.exec_command(command)

        for change_json in stdout:
            change = json.loads(change_json)

            if change.get("number"):
                if args.review:
                    changes.append(
                        f'{change["number"]},{change["currentPatchSet"]["number"]}'
                    )
                else:
                    changes.append(change["number"])

        return changes
