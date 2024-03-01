#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
import json
import requests

TIMEOUT = 10


def get_change_info(gerrit_url, change_num):
    ret = requests.get(
        f"https://{gerrit_url}/changes/{change_num}?o=CURRENT_REVISION",
        timeout=TIMEOUT,
    )
    return json.loads(ret.text.split("\n")[1])


def get_chained_changes(gerrit_url, change_num):
    change_info = get_change_info(gerrit_url, change_num)
    change_id = change_info["id"]
    commit = change_info["current_revision"]
    ret = requests.get(
        f"https://{gerrit_url}/changes/{change_id}/revisions/{commit}/related",
        timeout=TIMEOUT,
    )
    return json.loads(ret.text.split("\n")[1])["changes"]


def get_trimmed_changes(gerrit_url, change_num1, change_num2):
    start_idx, end_idx = None, None
    changes = get_chained_changes(gerrit_url, change_num1)

    for i, change in enumerate(changes):
        if change["_change_number"] == change_num1:
            start_idx = i
        if change["_change_number"] == change_num2:
            end_idx = i
        if start_idx is not None and end_idx is not None:
            return changes[end_idx : start_idx + 1]

    return []


def get_changes_list(ssh, args, action):
    gerrit_url = args.gerrit
    if args.change:
        if action == "review":
            changes = []
            # review needs a patchset number as well
            for change in args.change:
                change_info = get_change_info(gerrit_url, change)

                for _, rev_data in change_info["revisions"].items():
                    current_patchset = rev_data["_number"]

                changes.append(f"{change},{current_patchset}")

            return changes
        return args.change
    elif args.range:
        change_num1, change_num2 = args.range
        if action == "review":
            return [
                f'{change["_change_number"]},{change["_current_revision_number"]}'
                for change in get_trimmed_changes(gerrit_url, change_num1, change_num2)
            ]
        return [
            change["_change_number"]
            for change in get_trimmed_changes(gerrit_url, change_num1, change_num2)
        ]
    elif args.query or args.topic:
        changes = []
        query = args.query

        if args.topic:
            query = f"topic:{args.topic}"

        command = f"gerrit query {query} --current-patch-set --format=JSON"
        _, stdout, _ = ssh.exec_command(command)

        for change_json in stdout:
            change = json.loads(change_json)

            if change.get("number"):
                if action == "review":
                    changes.append(
                        f'{change["number"]},{change["currentPatchSet"]["number"]}'
                    )
                else:
                    changes.append(change["number"])

        return changes
