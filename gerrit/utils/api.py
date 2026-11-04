#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
import json


def get_change_info(ssh, change_num):
    command = (
        f"gerrit query {change_num} --current-patch-set --dependencies --format=JSON --no-limit"
    )
    _, stdout, _ = ssh.exec_command(command)

    for change_json in stdout:
        change = json.loads(change_json)
        if str(change.get("number")) == str(change_num):
            return change

    raise ValueError(f"Unable to find change info for change {change_num}")


def get_chained_changes(ssh, change_num):
    changes = []
    current_change_num = str(change_num)
    seen_changes = set()

    while current_change_num and current_change_num not in seen_changes:
        seen_changes.add(current_change_num)
        change_info = get_change_info(ssh, current_change_num)
        current_patchset = change_info.get("currentPatchSet")
        if not current_patchset:
            raise ValueError(
                f"Unable to find current patchset for change {current_change_num}"
            )

        changes.append(
            {
                "_change_number": int(change_info["number"]),
                "_current_revision_number": int(current_patchset["number"]),
            }
        )

        depends_on = change_info.get("dependsOn") or []
        next_change_num = None
        for dependency in depends_on:
            if dependency.get("number"):
                next_change_num = str(dependency["number"])
                break
        current_change_num = next_change_num

    return list(reversed(changes))


def get_trimmed_changes(ssh, change_num1, change_num2):
    start_idx, end_idx = None, None
    changes = get_chained_changes(ssh, change_num1)

    for i, change in enumerate(changes):
        if change["_change_number"] == change_num1:
            start_idx = i
        if change["_change_number"] == change_num2:
            end_idx = i
        if start_idx is not None and end_idx is not None:
            return changes[end_idx : start_idx + 1]

    return []


def get_current_patchset(ssh, change_num):
    change_info = get_change_info(ssh, change_num)
    current_patchset = change_info.get("currentPatchSet")
    if not current_patchset:
        raise ValueError(f"Unable to find current patchset for change {change_num}")
    return current_patchset["number"]


def get_changes_list(ssh, args, action):
    if args.change:
        if action == "review":
            changes = []
            # review needs a patchset number as well
            for change in args.change:
                current_patchset = get_current_patchset(ssh, change)
                changes.append(f"{change},{current_patchset}")

            return changes
        return args.change
    elif args.range:
        change_num1, change_num2 = args.range
        if action == "review":
            return [
                f'{change["_change_number"]},{change["_current_revision_number"]}'
                for change in get_trimmed_changes(ssh, change_num1, change_num2)
            ]
        return [
            change["_change_number"]
            for change in get_trimmed_changes(ssh, change_num1, change_num2)
        ]
    elif args.query or args.topic:
        changes = []
        skip_changes = []
        query = args.query
        final_query = []

        if hasattr(args, "topic") and args.topic:
            query = f"topic:{args.topic}"

        for q in query.split():
            if q.startswith("-"):
                if "topic:" in q:
                    skip_changes.append(q[1:].split(":")[1].strip("'\""))
                else:
                    skip_changes.append(q[1:])
            else:
                final_query.append(q)

        command = f"gerrit query {' '.join(final_query)} --current-patch-set --format=JSON --no-limit"
        if not args.quiet:
            print(command)

        _, stdout, _ = ssh.exec_command(command)

        for change_json in stdout:
            change = json.loads(change_json)
            if (
                change.get("topic") in skip_changes
                or str(change.get("number")) in skip_changes
            ):
                if not args.quiet:
                    print(f"Skipping {change['subject']}")
                continue
            if change.get("number"):
                if action == "review":
                    changes.append(
                        f'{change["number"]},{change["currentPatchSet"]["number"]}'
                    )
                else:
                    changes.append(change["number"])

        return changes
