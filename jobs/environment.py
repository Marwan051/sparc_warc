"""Load project dotenv defaults, optionally reporting only the added values."""

import json
import os
import sys
from pathlib import Path


def load_environment(path):
    if path.is_file():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=path, override=False)


def read_environment(path):
    """Load ``path`` and return only the names it added to the environment.

    Existing variables always win; that is what ``override=False`` means and it
    is the contract the resume checks rely on.
    """
    before = set(os.environ)
    load_environment(path)
    return {key: os.environ[key] for key in os.environ if key not in before}


def main():
    arguments = sys.argv[1:]
    if arguments and arguments[0] == "--json":
        path = Path(arguments[1]) if len(arguments) > 1 else (
            Path(__file__).resolve().parents[1] / ".env"
        )
        print(json.dumps(read_environment(path), sort_keys=True))
        return

    # Compatibility path for the old shell launcher: record explicit overrides,
    # load defaults, then replace the process with the requested command.
    os.environ["SPARK_WARC_EXPORTED_ENV_KEYS"] = json.dumps(sorted(os.environ))
    load_environment(Path(__file__).resolve().parents[1] / ".env")
    command = sys.argv[1:]
    if not command:
        raise SystemExit("expected a command to launch")
    os.execvpe(command[0], command, os.environ)


if __name__ == "__main__":
    main()
