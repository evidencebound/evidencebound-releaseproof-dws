from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi.testclient import TestClient


def _client() -> TestClient:
    path = Path(__file__).resolve().parents[1] / "deploy" / "vercel_evidence_surface.py"
    spec = spec_from_file_location("vercel_evidence_surface", path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


def test_vercel_evidence_surface_truth_boundary():
    client = _client()
    health = client.get("/health")
    assert health.status_code == 200
    payload = health.json()
    assert payload["status"] == "READY"
    assert payload["surface_class"] == "EVIDENCE_SURFACE"
    assert payload["live_dws_core"] == "PASS"
    assert payload["live_differential_reverification"] == "BLOCKED_QUOTA_402"
    assert payload["runtime_live_calls"] == "DISABLED"


def test_vercel_evidence_surface_has_no_live_dws_execution_endpoint():
    client = _client()
    paths = {route.path for route in client.app.routes}
    assert "/api/live-evidence" in paths
    assert "/api/evaluation" in paths
    assert "/api/demo" in paths
    assert not any("run-live" in path or "dws-call" in path for path in paths)


def test_vercel_evidence_surface_favicons_are_quiet():
    client = _client()
    assert client.get("/favicon.ico").status_code == 204
    assert client.get("/favicon.png").status_code == 204
