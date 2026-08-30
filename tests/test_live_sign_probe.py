from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

from releaseproof.dws import DwsError


def _load_probe(monkeypatch):
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    path = scripts_dir / "run_live_sign_probe.py"
    spec = importlib.util.spec_from_file_location("releaseproof_live_sign_probe", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sign_probe_classifies_http_400(monkeypatch):
    module = _load_probe(monkeypatch)
    assert module._status_from_error(DwsError("DWS signing returned HTTP 400")) == "FAIL_HTTP_400"


def test_sign_probe_workflow_isolated_from_normal_pushes():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "live-sign-probe.yml").read_text()
    assert "run/live-sign-probe" in workflow
    assert "acceptance/run-sign-probe.txt" in workflow
    assert "NUTRIENT_DATA_EXTRACTION_API_KEY" not in workflow
