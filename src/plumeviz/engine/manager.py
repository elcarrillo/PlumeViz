from __future__ import annotations

import shutil
from pathlib import Path


DEFAULT_EXECUTABLE_NAMES = (
    "plumeria_wd",
    "plumeria",
)


def find_plumeria_executable(
    executable: str | Path | None = None,
) -> Path | None:
    """
    Locate a usable Plumeria executable.

    Search order:
      1. Explicit path supplied by the caller.
      2. Known executable names available on PATH.

    Returns None when no executable can be found.
    """

    if executable is not None:
        path = Path(executable).expanduser()

        if path.is_file():
            return path.resolve()

        return None

    for name in DEFAULT_EXECUTABLE_NAMES:
        found = shutil.which(name)

        if found:
            return Path(found).resolve()

    return None
