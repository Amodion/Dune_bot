from __future__ import annotations

from pathlib import Path


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def static_path(filename: str) -> Path:
    return package_root() / "static" / filename


def read_static_text(filename: str) -> str:
    return static_path(filename).read_text(encoding="utf-8")

