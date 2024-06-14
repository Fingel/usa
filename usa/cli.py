import logging
import sys

from .shortcuts import open_current_issue

logger = logging.getLogger(__name__)


def main():
    success, msg = open_current_issue()
    if not success:
        sys.stdout.write(msg)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
