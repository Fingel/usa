#!/usr/bin/env python3

import argparse
import base64
import datetime
import json
import logging
import re
import subprocess
import sys
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError

import tomllib

"""
CONFIG
Settings file, logging setup, etc.
"""
logging.basicConfig(level=logging.INFO)
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
HTTP
JIRA REST, api client
"""


class JiraClientError(Exception):
    pass


class JiraAPIClient:
    def __init__(self) -> None:
        try:
            self.base_url = config["jira_url"]
        except IndexError:
            raise JiraClientError("jira_url missing from config.")

        try:
            self.username = config["email"]
            self.token = config["api_token"]
        except IndexError:
            raise JiraClientError("email and/or api_token missing from config.")

    def auth_header(self) -> str:
        auth_str = f"{self.username}:{self.token}"
        b64_auth_str = base64.b64encode(auth_str.encode("utf-8"))
        decoded = b64_auth_str.decode("utf-8")
        return f"Basic {decoded}"

    def post_json(self, endpoint: str, data: dict) -> dict:
        logger.debug("Making call to %s", self.base_url + endpoint)
        req = urllib.request.Request(self.base_url + endpoint)
        req.add_header("Content-Type", "application/json; charset=utf-8")
        req.add_header("Authorization", self.auth_header())
        json_data = json.dumps(data)
        bytes_data = json_data.encode("utf-8")
        try:
            response = urllib.request.urlopen(req, bytes_data)
            body = response.read()
            if len(body.decode()) > 1:
                return json.loads(body.decode())
            else:
                return {}
        except HTTPError as e:
            logger.exception("Got HTTPError from Jira.")
            raise JiraClientError(e.read().decode())

    def get_json(self, endpoint: str) -> dict:
        logger.debug("Making call to %s", self.base_url + endpoint)
        req = urllib.request.Request(self.base_url + endpoint)
        req.add_header("Authorization", self.auth_header())
        try:
            response = urllib.request.urlopen(req)
            body = response.read()
            return json.loads(body.decode())
        except HTTPError as e:
            logger.exception("Got HTTPError from Jira.")
            raise JiraClientError(e.read().decode())


"""
COMMENTS
"""


@dataclass
class Comment:
    email: str
    date: str
    body: str

    def __str__(self) -> str:
        date = datetime.datetime.fromisoformat(self.date)
        formatted_d = date.strftime("%B %-d, %Y at %-I:%M %p")
        return f"{self.email:<30}{formatted_d}\n{self.body}\n\n"


def parse_comments_response(resp: dict) -> list[Comment]:
    return [
        Comment(email=c["author"]["emailAddress"], date=c["created"], body=c["body"])
        for c in resp["comments"]
    ]


def add_comment(issue_id: str, body: str) -> dict:
    client = JiraAPIClient()
    endpoint = f"/rest/api/latest/issue/{issue_id}/comment"
    data = {"body": body}
    return client.post_json(endpoint, data)


def get_comments(issue_id: str) -> list[Comment]:
    client = JiraAPIClient()
    endpoint = f"/rest/api/latest/issue/{issue_id}/comment"
    all_comments = client.get_json(endpoint)
    return parse_comments_response(all_comments)


"""
TRANSITIONS
"""


@dataclass
class Transition:
    id: int
    name: str

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"


def parse_transitions_response(resp: dict) -> list[Transition]:
    return [Transition(id=t["id"], name=t["name"]) for t in resp["transitions"]]


def get_available_transitions(issue_id: str) -> list[Transition]:
    client = JiraAPIClient()
    endpoint = f"/rest/api/latest/issue/{issue_id}/transitions"
    all_transitions = client.get_json(endpoint)
    return parse_transitions_response(all_transitions)


def do_transition(issue_id: str, transition: int):
    client = JiraAPIClient()
    endpoint = f"/rest/api/latest/issue/{issue_id}/transitions"
    data = {"transition": {"id": transition}}
    client.post_json(endpoint, data)


"""
MAIN
Main entrypoint, argument parsing.
"""

parser = argparse.ArgumentParser(description="Scripts for working with Atlassian JIRA.")
parser.add_argument(
    "-i", "--issue", help="Issue id. Defaults to parsing from active Git branch."
)
parser.add_argument("-c", "--comment", help="Add a comment to the issue.")
parser.add_argument(
    "--list-comments", action="store_true", help="Display comments for an issue."
)
parser.add_argument(
    "-o", "--open", action="store_true", help="Open the issue in a web browser."
)
parser.add_argument(
    "-t",
    "--transition",
    action="store_true",
    help="Transition the issue's state (e.g Backlog -> In Progress)",
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

    if args.comment:
        add_comment(issue_id, args.comment)
        comments = get_comments(issue_id)
        for comment in comments:
            sys.stdout.write(str(comment))

    if args.list_comments:
        comments = get_comments(issue_id)
        for comment in comments:
            sys.stdout.write(str(comment))

    if args.transition:
        transitions = get_available_transitions(issue_id)
        for transition in transitions:
            sys.stdout.write(str(transition) + "\n")
        transition_id = int(input("Enter id: "))
        do_transition(issue_id, transition_id)
        sys.stdout.write("Success.")

    if args.open:
        open_issue(issue_id)


if __name__ == "__main__":
    main()
