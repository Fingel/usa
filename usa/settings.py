import tomllib
from pathlib import Path

with open(Path.home() / ".config/usa.toml") as f:
    config = tomllib.loads(f.read())
