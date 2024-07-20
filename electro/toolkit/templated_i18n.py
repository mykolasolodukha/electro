"""A subclass of `I18nMiddleware` that allows for string templating."""

from string import Template
from typing import Callable


class TemplatedString(str, Template):
    """A string that can be used both as a string and as a template."""

    def __repr__(self) -> str:
        """Return a representation of the string."""
        return f"TemplatedString({super().__repr__()})"


def make_templated_gettext(gettext_function: Callable[..., str]) -> Callable[..., TemplatedString]:
    """Return a function that returns `TemplatedString` instead of strings."""

    def templated_gettext(*args, **kwargs) -> TemplatedString:
        """Return a `TemplatedString(str)()` instead of a string."""
        return TemplatedString(gettext_function(*args, **kwargs))

    return templated_gettext
