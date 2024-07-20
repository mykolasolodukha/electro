"""All the common stuff that is used in the `electro` Framework."""

from contextvars import ContextVar
from typing import Type, TypeVar

T = TypeVar("T")


class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_instance = ContextVar(f"instance_{cls.__name__}")
        return cls

    @classmethod
    def get_current(cls: Type[T], no_error=True) -> T:
        if no_error:
            return cls.__context_instance.get(None)
        return cls.__context_instance.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}")
        cls.__context_instance.set(value)
