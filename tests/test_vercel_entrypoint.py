from __future__ import annotations

import importlib
from pathlib import Path
import tomllib

from fastapi import FastAPI


ROOT = Path(__file__).resolve().parents[1]


def test_vercel_entrypoint_maps_to_real_root_module_file():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    entrypoint = config["tool"]["vercel"]["entrypoint"]
    module_name, object_name = entrypoint.split(":", 1)

    module_file = ROOT.joinpath(*module_name.split(".")).with_suffix(".py")
    assert module_file.is_file(), (
        f"Vercel entrypoint {entrypoint!r} does not map to a module file at {module_file}"
    )

    module = importlib.import_module(module_name)
    assert object_name == "app"
    assert isinstance(getattr(module, object_name), FastAPI)
