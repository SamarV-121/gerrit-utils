# Gerrit Utils

## Requirements

* Python 3.10 (or newer)

## Installation

```bash
pip3 install --upgrade git+https://github.com/SamarV-121/gerrit-utils
```

## Usage

```bash
usage: gerrit-utils [-h] {push,review,set-reviewers,topic} ...

options:
  -h, --help                         show this help message and exit

abilities:
  {push,review,set-reviewers,topic}
    push                             Push changes to Gerrit
    review                           Review gerrit changes
    set-reviewers                    Assign reviewers
    topic                            Set topic
```

### Push

```bash
usage: gerrit-utils push [-h] [--path PATH] [-b BRANCH] [-c COMMIT] [-r REMOTE] [--ref REF] [-cr {+2,0,+1,-1,-2}] [-v {-1,0,+1}] [-t TOPIC] [-m MERGE] [-n]
                    [--reviewer REVIEWER] [--cc CC] [--private | --remove-private] [--wip | --ready]

options:
  -h, --help                                          show this help message and exit
  --path PATH                                         Specify the local path of repo
  -b BRANCH, --branch BRANCH                          Specify the branch name
  -c COMMIT, --commit COMMIT                          Specify the commit hash id
  -r REMOTE, --remote REMOTE                          Specify the remote
  --ref REF                                           Specify the ref type
  -t TOPIC, --topic TOPIC                             Specify a topic
  -cr {+2,0,+1,-1,-2}, --code-review {+2,0,+1,-1,-2}  Code review
  -v {-1,0,+1}, --verified {-1,0,+1}                  Verify the change
  -m MERGE_COMMIT, --merge MERGE_COMMIT               Push a merge on Gerrit
  -n, --no-thin                                       Disable thin optimizations while pushing
  --reviewer REVIEWER                                 Assign a reviewer
  --cc CC                                             CC additional recipients
  --private                                           Set the change visibility to private
  --remove-private                                    Set the change visibility to public
  --wip                                               Mark the change as work in progress
  --ready                                             Mark the change as ready for reviewing
```

### Review

```bash
usage: gerrit-utils review [-h] [-g GERRIT] [-p PORT] [-u USER] (-c CHANGE [CHANGE ...] | --range CHANGE1 CHANGE2 | -q QUERY | -t TOPIC) [-a | -r | -s] [-m MESSAGE]
                      [-cr {0,+2,-2,-1,+1}] [-v {-1,0,+1}]

options:
  -h, --help                                            show this help message and exit
  -g GERRIT, --gerrit GERRIT                            Specify the Gerrit server URL (default: None)
  -p PORT, --port PORT                                  Specify the Gerrit server port number (default: 29418)
  -u USER, --user USER                                  Specify the Gerrit user (default: None)
  -c CHANGE [CHANGE ...], --change CHANGE [CHANGE ...]  Specify the change number(s)
  --range CHANGE1 CHANGE2                               Specify a range of changes
  -q QUERY, --query QUERY                               Specify a Gerrit query
  -t TOPIC, --topic TOPIC                               Specify a topic name
  -a, --abandon                                         Abandon the change
  -r, --restore                                         Restore the change
  -s, --submit                                          Submit the change
  -m MESSAGE, --message MESSAGE                         Post a message on the change
  -cr {0,+2,-2,-1,+1}, --code-review {0,+2,-2,-1,+1}    Code review
  -v {-1,0,+1}, --verified {-1,0,+1}                    Verify the change
```

### Set reviewers

```bash
usage: gerrit-utils set-reviewers [-h] -g GERRIT [-p PORT] -u USER (-c CHANGE [CHANGE ...] | --range CHANGE1 CHANGE2 | -q QUERY | -t TOPIC) [-a ADD] [-r REMOVE]

options:
  -h, --help                                            show this help message and exit
  -g GERRIT, --gerrit GERRIT                            Specify the Gerrit server URL (default: None)
  -p PORT, --port PORT                                  Specify the Gerrit server port number (default: 29418)
  -u USER, --user USER                                  Specify the Gerrit user (default: None)
  -c CHANGE [CHANGE ...], --change CHANGE [CHANGE ...]  Specify the change number(s)
  --range CHANGE1 CHANGE2                               Specify a range of changes
  -q QUERY, --query QUERY                               Specify a Gerrit query
  -t TOPIC, --topic TOPIC                               Specify a topic name
  -a ADD, --add ADD                                     Add reviewer to the change
  -r REMOVE, --remove REMOVE                            Remove reviewer from the change
```

### Topic

```bash
usage: gerrit-utils topic [-h] -g GERRIT [-p PORT] -u USER (-c CHANGE [CHANGE ...] | --range CHANGE1 CHANGE2 | -q QUERY) [-t TOPIC]

options:
  -h, --help                                            show this help message and exit
  -g GERRIT, --gerrit GERRIT                            Specify the Gerrit server URL (default: None)
  -p PORT, --port PORT                                  Specify the Gerrit server port number (default: 29418)
  -u USER, --user USER                                  Specify the Gerrit user (default: None)
  -c CHANGE [CHANGE ...], --change CHANGE [CHANGE ...]  Specify the change number(s)
  --range CHANGE1 CHANGE2                               Specify a range of changes
  -q QUERY, --query QUERY                               Specify a Gerrit query
  -t TOPIC, --topic TOPIC                               Set topic
```

## License

```bash
#
# Copyright (C) 2023-2024, Samar Vispute "SamarV-121" <samar@samarv121.dev>
#
# SPDX-License-Identifier: MIT
#
```
