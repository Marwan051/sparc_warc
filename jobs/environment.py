"""Load project dotenv defaults, then replace this process with the launcher."""

import os
from pathlib import Path
import sys


def load_environment(path):
    if path.is_file():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=path, override=False)


def main():
    load_environment(Path(__file__).resolve().parents[1] / '.env')
    command = sys.argv[1:]
    if not command:
        raise SystemExit('expected a command to launch')
    os.execvpe(command[0], command, os.environ)


if __name__ == '__main__':
    main()
