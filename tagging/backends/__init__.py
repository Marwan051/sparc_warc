"""Lazy backend selection; importing this package loads no models."""


def create_backend(name, model):
    if name == "groq":
        from tagging.backends.groq import GroqBackend
        return GroqBackend(model)
    if ":" in name:
        from importlib import import_module
        module, attribute = name.split(":", 1)
        return getattr(import_module(module), attribute)(model)
    raise ValueError(f"unknown tagging backend: {name}")
