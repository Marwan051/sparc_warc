"""Errors that map cleanly onto launcher exit codes."""


class LaunchError(Exception):
    def __init__(self, message="", exit_code=1):
        super().__init__(message)
        self.message = message
        self.exit_code = 128 - exit_code if exit_code < 0 else exit_code
