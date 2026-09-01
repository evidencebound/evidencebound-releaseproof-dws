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
    assert "--canonical-output live-sign-probe-canonical.pdf" in workflow
    assert "live-sign-probe-canonical.pdf" in workflow


def test_sign_probe_sanitizes_provider_error_body(monkeypatch):
    module = _load_probe(monkeypatch)

    class Response:
        def json(self):
            return {
                "details": "invalid file",
                "requestId": "req-123",
                "failingPaths": ["file"],
                "authorization": "Bearer should-not-leak",
                "extra": {"secret": "nope"},
            }

    assert module._sanitize_provider_error(Response()) == {
        "details": "invalid file",
        "requestId": "req-123",
        "failingPaths": ["file"],
    }


def test_sign_probe_non_json_provider_error_fails_closed(monkeypatch):
    module = _load_probe(monkeypatch)

    class Response:
        def json(self):
            raise ValueError("not json")

    assert module._sanitize_provider_error(Response()) == {}


def test_sign_probe_posts_file_only_and_captures_http_400(monkeypatch):
    module = _load_probe(monkeypatch)
    captured = {}

    class Transport:
        sign_endpoint = "https://api.nutrient.io/sign"
        api_key = "processor-key"
        timeout_seconds = 60

    class Response:
        status_code = 400
        content = b'{"details":"invalid file","requestId":"req-live","failingPaths":["file"]}'

        def json(self):
            return {
                "details": "invalid file",
                "requestId": "req-live",
                "failingPaths": ["file"],
            }

    def fake_post(endpoint, headers, files, timeout):
        captured["endpoint"] = endpoint
        captured["headers"] = headers
        captured["files"] = files
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(module.requests, "post", fake_post)
    signed, status, diagnostics = module._sign_with_diagnostics(
        Transport(), b"%PDF-canonical\n%%EOF", filename="canonical.pdf"
    )

    assert signed is None
    assert status == 400
    assert diagnostics == {
        "details": "invalid file",
        "requestId": "req-live",
        "failingPaths": ["file"],
    }
    assert captured["endpoint"] == "https://api.nutrient.io/sign"
    assert captured["headers"] == {"Authorization": "Bearer processor-key"}
    assert list(captured["files"]) == ["file"]
    assert captured["files"]["file"] == (
        "canonical.pdf",
        b"%PDF-canonical\n%%EOF",
        "application/pdf",
    )
    assert captured["timeout"] == 60


def test_sign_probe_retains_canonical_pdf_and_provider_diagnostics(monkeypatch, tmp_path):
    module = _load_probe(monkeypatch)
    monkeypatch.setenv("NUTRIENT_API_KEY", "test-key")

    class FakeTransport:
        def __init__(self, key):
            assert key == "test-key"

        def canonicalize_pdf(self, source):
            return b"%PDF-canonical\n%%EOF"

    monkeypatch.setattr(module, "NutrientDwsTransport", FakeTransport)
    monkeypatch.setattr(
        module,
        "_sign_with_diagnostics",
        lambda transport, pdf_bytes, filename: (
            None,
            400,
            {
                "details": "invalid file",
                "requestId": "req-123",
                "failingPaths": ["file"],
            },
        ),
    )

    signed_output = tmp_path / "signed.pdf"
    canonical_output = tmp_path / "canonical.pdf"
    receipt = module.run(signed_output, canonical_output)

    assert canonical_output.read_bytes() == b"%PDF-canonical\n%%EOF"
    assert receipt["signing"] == "FAIL_HTTP_400"
    assert receipt["provider_error"] == {
        "details": "invalid file",
        "requestId": "req-123",
        "failingPaths": ["file"],
    }
    assert "test-key" not in str(receipt)
    assert not signed_output.exists()


def test_sign_probe_returns_signed_pdf_on_success(monkeypatch):
    module = _load_probe(monkeypatch)

    class Transport:
        sign_endpoint = "https://api.nutrient.io/sign"
        api_key = "processor-key"
        timeout_seconds = 60

    class Response:
        status_code = 200
        content = b"%PDF-signed\n%%EOF"

    monkeypatch.setattr(module.requests, "post", lambda *args, **kwargs: Response())
    signed, status, diagnostics = module._sign_with_diagnostics(
        Transport(), b"%PDF-canonical\n%%EOF", filename="canonical.pdf"
    )

    assert signed == b"%PDF-signed\n%%EOF"
    assert status == 200
    assert diagnostics == {}
