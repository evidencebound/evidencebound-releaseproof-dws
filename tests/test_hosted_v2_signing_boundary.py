from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

from releaseproof.dws import DwsError


def _load_acceptance_module(monkeypatch):
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    path = scripts_dir / "run_live_dws_v2_acceptance.py"
    spec = importlib.util.spec_from_file_location("releaseproof_hosted_v2_signing_boundary", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FailingSigner:
    def sign_pdf(self, pdf_bytes: bytes, *, filename: str = "release.pdf") -> bytes:
        raise DwsError("DWS signing returned HTTP 400")


def test_optional_signing_failure_does_not_erase_core_acceptance(monkeypatch, tmp_path):
    module = _load_acceptance_module(monkeypatch)
    result = module._attempt_optional_sign(
        FailingSigner(),
        b"%PDF-1.4\n%%EOF\n",
        tmp_path / "signed.pdf",
    )

    assert result["status"] == "FAIL_HTTP_400"
    assert result["required_for_core_acceptance"] is False
    assert not (tmp_path / "signed.pdf").exists()


def test_script_records_core_pass_before_optional_signing(monkeypatch):
    module = _load_acceptance_module(monkeypatch)
    source = Path(module.__file__).read_text(encoding="utf-8")
    core_marker = '"core_status": "PASS"'
    sign_call = "_attempt_optional_sign("
    assert core_marker in source
    assert sign_call in source
    assert source.index(core_marker) < source.rindex(sign_call)
