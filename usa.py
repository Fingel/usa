#!/usr/bin/env python3

import argparse
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


"""
MAIN
Main entrypoint, argument parsing.
"""

parser = argparse.ArgumentParser(description="Scripts for working with Atlassian JIRA.")
parser.add_argument(
    "-i", "--issue", help="Issue id. Defaults to parsing from active Git branch."
)
parser.add_argument(
    "-o", "--open", action="store_true", help="Open the issue in a web browser."
)
args = parser.parse_args()


def main():
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    if args.issue is None:
        try:
            branch = git_branch()
        except GitException:
            sys.stdout.write("Could not determine git branch. Are you in a repo?")
            sys.exit(1)
        issue_id = extract_issue_id(branch)
        if issue_id is None:
            sys.stdout.write(f"Could not determine issue from branch name: {branch}")
            sys.exit(1)
    else:
        issue_id = args.issue

    if args.open:
        open_issue(issue_id)


if __name__ == "__main__":
    main()
