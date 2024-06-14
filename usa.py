#!/usr/bin/env python

import logging
import re
import subprocess
import sys
import webbrowser
from pathlib import Path

import tomllib

"""
CONFIG
Settings file, logging setup, etc.
"""
logger = logging.getLogger(__name__)

with open(Path.home() / ".config/usa.toml") as f:
    config = tomllib.loads(f.read())


"""
ISSUES
Branch parsing, regex, webbrowser.
"""


class GitException(Exception):
    pass


def git_branch() -> str:
    try:
        p = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise GitException(e.stderr)
    else:
        branch_name = p.stdout
        return branch_name.strip()


def extract_issue_id(branch: str) -> str | None:
    result = re.search(r"^(\D+-\d+)", branch)
    if not result:
        return None
    else:
        return result.group(1)


def open_issue(issue_id: str):
    webbrowser.open_new_tab(f"{config["jira_url"]}/browse/{issue_id}")


def open_current_issue() -> tuple[bool, str]:
    """
    Attempts to use the currently checked out branch name
    to open a web browser to the appropriate JIRA issue
    """
    try:
        branch = git_branch()
    except GitException:
        return False, "Could not determine git branch. Are you in a repo?"
    issue_id = extract_issue_id(branch)
    if issue_id is None:
        return False, f"Could not determine issue from branch name: {branch}"
    open_issue(issue_id)
    return True, "success"


"""
MAIN
Main entrypoint, argument parsing.
"""


def main():
    success, msg = open_current_issue()
    if not success:
        sys.stdout.write(msg)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
