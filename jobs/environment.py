"""Load project dotenv defaults, then replace this process with the launcher."""

import os
import json
from pathlib import Path
import sys


def load_environment(path):
    if path.is_file():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=path, override=False)


def main():
    # Preserve source information for resume checks: dotenv values are defaults,
    # while variables present before loading the file are explicit overrides.
    os.environ["SPARK_WARC_EXPORTED_ENV_KEYS"] = json.dumps(sorted(os.environ))
    load_environment(Path(__file__).resolve().parents[1] / '.env')
    command = sys.argv[1:]
    if not command:
        raise SystemExit('expected a command to launch')
    os.execvpe(command[0], command, os.environ)


if __name__ == '__main__':
    main()
