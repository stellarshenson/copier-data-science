#!/usr/bin/env python3
"""Docker entrypoint for {{ project_name }}."""

import argparse
import sys
from importlib.metadata import version

import {{ module_name }}
from {{ module_name }}.modeling import predict, train

__version__ = version("{{ module_name }}")


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(
        description="{{ description }}"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "train", "predict"],
        help="Command to execute (default: run)",
    )
    args = parser.parse_args()

    if args.command == "run":
        # ANSI color codes
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        print(f"{GREEN}🐳  Running inside Docker container{RESET}")
        print(f"{CYAN}{{ project_name }}{RESET} {YELLOW}v{__version__}{RESET}")
        print()
        # Add your main execution logic here
    elif args.command == "train":
        train.main()
    elif args.command == "predict":
        predict.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())
