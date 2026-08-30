from releaseproof.public_app import health, index


def test_health_exposes_hosted_v2_core_and_optional_signing_truth():
    payload = health()
    assert payload["dws_native_v2_core_hosted"] == "PASS"
    assert payload["dws_native_v2_signing"] == "FAIL_HTTP_400"
    assert payload["dws_native_v2_viewer"] == "UNRUN"
    assert payload["dws_native_v2_run"] == 33296171708


def test_judge_surface_no_longer_calls_v2_hosted_unrun():
    html = index()
    assert "DWS-NATIVE V2 CORE · HOSTED PASS" in html
    assert "SIGNING · HTTP 400" in html
    assert "CONTRACT TESTED / HOSTED UNRUN" not in html
    assert "quota was exhausted before" not in html.lower()
