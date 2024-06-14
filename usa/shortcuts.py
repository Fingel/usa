import subprocess
import re
import logging
import webbrowser

from .settings import config

logger = logging.getLogger(__name__)


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
    try:
        branch = git_branch()
    except GitException:
        return False, "Could not determine git branch. Are you in a repo?"
    issue_id = extract_issue_id(branch)
    if issue_id is None:
        return False, "Could not determine issue from branch name: {branch}"
    open_issue(issue_id)
    return True, "success"
