# 🇺🇸 USA 🇺🇸
Un-Stickify Atlassian

JIRA is slow, confusing and extremely bloated. Did I mention it's slow?

`usa` is a script with several functions that make it easier to quickly find
the issues you are looking for and even perform some common tasks without leaving
the terminal.

Some features include:

* Open the current JIRA issue in a webrowser determined by the current Git branch.
* Comment on issues.
* Transition issues (change their state).
* List and open issues associated with a project.
* General search of issues (and being able to view the context of the matched search terms).

**Most of these interactions assume you prefix your git branches with the JIRA issue ID.**
For example: `ISSUE-123-implement-widget` It's possible to use the `-i` flag to manually
specify issue ID's but you will be missing most of the convenience of the script.

`usa` is a single file Python script that only depends on the standard library.
Simply drop in somewhere in your $PATH and execute. 

Requires Python >= 3.11

## Usage examples

Open the current issue in the default web browser:

`> usa -o`

Add a comment (also displays previous comments) to the current issue and then open it in the default browser:

```
> usa -c"Found some tech debt, working on it now" -o

example@example.com         June 18, 2024 at 08:03 AM
Please someone fix this

joe@example.com             June 18, 2024 at 12:52 PM
Found some tech debt, working on it now.
```

Transition the current issue (change state), add a comment, and open it:

```
> usa -c"Finished this!" -t -o
joe@example.com                June 18, 2024 at 12:50 PM
Finished this!

Available states to transition to:
11 - To Do
21 - In Progress
31 - Code Review
41 - Testing
51 - Done
61 - Won't Do
71 - Blocked
Enter state id:
```

List sibling issues:

```
> usa -l
 1 Issue-3180   Backlog     joe@example.com      🏎️ PERF: Suspense - Async load components
 2 Issue-3182   Backlog     joe@example.com      ⚙️ CHORE: npm audit

Found 2 issues for parent issue(s): Issue-2297, Issue-2885
Open issue:
```

## Installation

Copy or link usa.py to somewhere in your $PATH e.g:

    ln -s usa.py ~/bin/usa

and make sure the file is executable:

    chmod a+x ~/bin/usa

## Configuration

Copy `config.sample.toml` to `~/.config/usa.toml`:

    cp config.sample.toml ~/.config/usa.toml

and make sure to fill in the appropriate values.
