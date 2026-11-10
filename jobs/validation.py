"""Dependency-free integer validation for configuration and command arguments."""

import argparse
import os


def integer(value, *, name, minimum=0):
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer, got {value!r}") from error
    if number < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {number}")
    return number


def env_int(name, default, *, minimum=0):
    return integer(os.environ.get(name, str(default)).strip(), name=name, minimum=minimum)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean, got {value!r}")


def positive_int(value):
    try:
        return integer(value, name="value", minimum=1)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def non_negative_int(value):
    try:
        return integer(value, name="value", minimum=0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
