# 🇺🇸 USA 🇺🇸
Un-Suckify Atlassian

JIRA is slow, confusing and extremely bloated. Did I mention it's slow?

`usa` is a script with several functions that make it easier to quickly find
the issues you are looking for and even perform some common tasks without leaving
the terminal.

Some features include:

* Open the current JIRA issue in a webrowser determined by the current Git branch.
* Comment on issues.
* Transition issues (change their state).
* List and open issues associated with a project.

`usa` is a single file Python script that only depends on the standard library.
Simply drop in somewhere in your $PATH and go.

## Installation

Copy or link usa.py to somewhere in your $PATH e.g:

    ln -s usa.py ~/bin/usa

and make sure the file is executable:

    chmod a+x ~/bin/usa

## Configuration

Copy `config.sample.toml` to `~/.config/usa.toml`:

    cp config.sample.toml ~/.config/usa.toml

and make sure to fill in the appropriate values.
