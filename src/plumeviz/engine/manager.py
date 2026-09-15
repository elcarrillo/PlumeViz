from __future__ import annotations

import os
import shutil
import subprocess

from pathlib import Path


PLUMERIA_VERSION = "3.0.0"

PLUMERIA_REPOSITORY_URL = (
    "https://code.usgs.gov/vsc/Ash_hazards/plumeria_wd.git"
)


DEFAULT_EXECUTABLE_NAMES = (
    "plumeria_wd",
    "plumeria",
)

_BAD_FORMAT_FRAGMENT = "e12.4', kg/s'"
_FIXED_FORMAT_FRAGMENT = "e12.4,' kg/s'"


COMPATIBILITY_PATCHES = {
    "3.0.0": (
        (
            _BAD_FORMAT_FRAGMENT,
            _FIXED_FORMAT_FRAGMENT,
            2,
        ),
    ),
}

BUILD_RECIPES = {
    "3.0.0": {
        "command": ("make",),
        "required_tools": ("make", "gfortran"),
        "executable": "plumeria_wd",
    },
}


def find_plumeria_executable(
    executable: str | Path | None = None,
    version: str = PLUMERIA_VERSION,
) -> Path | None:
    """
    Locate a usable Plumeria executable.

    Search order:
      1 Explicit path supplied by the caller.
      2 PlumeViz-managed executable for the requested version.
      3 Known executable names available on PATH.

    returns none when no executable can be found.
    """

    if executable is not None:
        path = Path(executable).expanduser()

        if path.is_file():
            return path.resolve()

        return None

    recipe = BUILD_RECIPES.get(version)

    if recipe is not None:
        managed = (
            managed_binary_directory(version)
            / recipe["executable"]
        )

        if managed.is_file():
            return managed.resolve()

    for name in DEFAULT_EXECUTABLE_NAMES:
        found = shutil.which(name)

        if found:
            return Path(found).resolve()

    return None


def plumeviz_home() -> Path:
    """
    Return the directory used for PlumeViz-managed data.

    PLUMEVIZ_HOME can override the default location.
    """

    configured = os.environ.get("PLUMEVIZ_HOME")

    if configured:
        return Path(configured).expanduser()

    return Path.home() / ".plumeviz"


def managed_source_directory(
    version: str = PLUMERIA_VERSION,
) -> Path:
    """Return the managed source directory for a Plumeria version."""

    return (
        plumeviz_home()
        / "engines"
        / "plumeria_wd"
        / version
        / "source"
    )


def _find_main_f90(source_dir: Path) -> Path:
    matches = list(source_dir.rglob("main.f90"))

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one main.f90 in {source_dir}, "
            f"found {len(matches)}."
        )

    return matches[0]


def fetch_plumeria_source(
    version: str = PLUMERIA_VERSION,
    *,
    force: bool = False,
) -> Path:
    """
    Fetch the official USGS Plumeria source into PlumeViz-managed storage.

    Existing valid source is reused unless force=True.
    """

    destination = managed_source_directory(version)

    if destination.exists():
        try:
            _find_main_f90(destination)
        except RuntimeError:
            if not force:
                raise RuntimeError(
                    f"Existing Plumeria source directory is incomplete: "
                    f"{destination}"
                )
        else:
            if not force:
                return destination

        shutil.rmtree(destination)

    git = shutil.which("git")

    if git is None:
        raise RuntimeError(
            "Git is required to fetch the official USGS Plumeria source."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    command = [
        git,
        "clone",
        "--branch",
        version,
        "--depth",
        "1",
        "--single-branch",
        PLUMERIA_REPOSITORY_URL,
        str(destination),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        if destination.exists():
            shutil.rmtree(destination)

        detail = exc.stderr.strip() or exc.stdout.strip()

        raise RuntimeError(
            f"Failed to fetch official USGS Plumeria {version} source. "
            f"{detail}"
        ) from exc

    _find_main_f90(destination)

    return destination

def patch_plumeria_source(
    source_dir: str | Path,
    version: str = PLUMERIA_VERSION,
) -> Path:
    """
    Apply compatibility patches validated for a specific Plumeria version.

    Versions without registered patches are left untouched.
    """

    source_dir = Path(source_dir).expanduser()
    main_f90 = _find_main_f90(source_dir)

    patches = COMPATIBILITY_PATCHES.get(version, ())

    if not patches:
        return main_f90

    text = main_f90.read_text()
    changed = False

    for bad_fragment, fixed_fragment, expected_count in patches:
        bad_count = text.count(bad_fragment)
        fixed_count = text.count(fixed_fragment)

        if bad_count == expected_count:
            text = text.replace(
                bad_fragment,
                fixed_fragment,
            )
            changed = True
            continue

        if bad_count == 0 and fixed_count >= expected_count:
            continue

        raise RuntimeError(
            f"Unexpected source structure for Plumeria {version}. "
            f"Expected {expected_count} occurrence(s) of "
            f"{bad_fragment!r}, found {bad_count}. "
            "Refusing to modify the source."
        )

    if changed:
        main_f90.write_text(text)

    return main_f90


def prepare_plumeria_source(
    version: str = PLUMERIA_VERSION,
    *,
    force: bool = False,
) -> Path:
    """
    Fetch official USGS Plumeria source and apply any validated
    compatibility patches for that version.
    """

    source_dir = fetch_plumeria_source(
        version,
        force=force,
    )

    patch_plumeria_source(
        source_dir,
        version=version,
    )

    return source_dir


def managed_binary_directory(
    version: str = PLUMERIA_VERSION,
) -> Path:
    """Return the managed binary directory for a Plumeria version."""

    return (
        plumeviz_home()
        / "engines"
        / "plumeria_wd"
        / version
        / "bin"
    )


def build_plumeria(
    version: str = PLUMERIA_VERSION,
    *,
    force: bool = False,
) -> Path:
    """
    Build a validated Plumeria version and install its executable
    into PlumeViz-managed storage.
    """

    recipe = BUILD_RECIPES.get(version)

    if recipe is None:
        raise RuntimeError(
            f"No validated PlumeViz build recipe exists for "
            f"Plumeria {version}."
        )

    destination_dir = managed_binary_directory(version)
    destination = destination_dir / recipe["executable"]

    if destination.is_file() and not force:
        return destination.resolve()

    for tool in recipe["required_tools"]:
        if shutil.which(tool) is None:
            raise RuntimeError(
                f"Required build tool is not available: {tool}"
            )

    source_dir = prepare_plumeria_source(
        version,
        force=force,
    )

    try:
        subprocess.run(
            list(recipe["command"]),
            cwd=source_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip()

        raise RuntimeError(
            f"Failed to build Plumeria {version}. {detail}"
        ) from exc

    built_executable = source_dir / recipe["executable"]

    if not built_executable.is_file():
        raise RuntimeError(
            f"Build completed but expected executable was not found: "
            f"{built_executable}"
        )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        built_executable,
        destination,
    )

    destination.chmod(
        destination.stat().st_mode | 0o111
    )

    return destination.resolve()
