"""Resolve writable data paths and bundled assets for dev and frozen builds."""
import sys
from pathlib import Path

APP_NAME = "GFA Admin Panel"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_dir() -> Path:
    """Directory beside the executable (or project root in development)."""
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    """Read-only bundled assets extracted by PyInstaller."""
    if is_frozen():
        base = Path(getattr(sys, "_MEIPASS", app_dir()))
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)


def find_asset(candidates: tuple[str, ...] | list[str]) -> Path | None:
    for name in candidates:
        bundled = resource_path(name)
        if bundled.exists():
            return bundled
    for name in candidates:
        local = app_dir() / name
        if local.exists():
            return local
    return None
