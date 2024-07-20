"""
The `__version__` module.

Separated from the `__init__` one because some tools use `__init__` internally
(e.g. Pycharm Interactive console: `pycharm_matplotlib_backend`) and that creates problems.
"""

import tomllib
from pathlib import Path

# Get the version
with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as file:
    __version__ = tomllib.load(file)["tool"]["poetry"]["version"]


__all__ = ["__version__"]
