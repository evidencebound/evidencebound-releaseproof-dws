from fastapi.testclient import TestClient

from releaseproof.public_app import CANONICAL_LIVE_EVIDENCE, V2_HOSTED_EVIDENCE, app


def test_public_health_exposes_accepted_live_truth_without_overclaiming():
    client = TestClient(app)
    data = client.get('/health').json()
    assert data['status'] == 'READY'
    assert data['controlled_kernel'] == 'PASS'
    assert data['public_ci'] == 'PASS'
    assert data['live_dws_core'] == 'PASS'
    assert data['dws_native_v2_core_hosted'] == 'PASS'
    assert data['live_differential_reverification'] == 'PASS_HOSTED'
    assert data['dws_native_v2_signing'] == 'FAIL_HTTP_400'
    assert data['dws_native_v2_viewer'] == 'UNRUN'
    assert data['canonical_live_run'] == 32215337912
    assert data['dws_native_v2_run'] == 33296171708
    assert data['runtime_live_calls'] == 'DISABLED_AFTER_ACCEPTANCE'


def test_public_live_evidence_preserves_historical_static_receipt_contract():
    client = TestClient(app)
    data = client.get('/api/live-evidence').json()
    assert data == CANONICAL_LIVE_EVIDENCE
    assert data['status'] == 'PASS'
    assert data['document_count'] == 3
    assert data['release_state'] == 'REVIEW_REQUIRED'
    assert data['review_trigger'] == 'CROSS_DOCUMENT_MISMATCH'
    assert data['hosted_differential_reverification'] == 'BLOCKED_QUOTA_402'
    assert set(data['dws_receipts']) == {'invoice', 'shipping', 'certificate'}


def test_public_v2_evidence_is_static_sanitized_receipt_not_provider_call():
    client = TestClient(app)
    data = client.get('/api/v2-evidence').json()
    assert data == V2_HOSTED_EVIDENCE
    assert data['status'] == 'PASS'
    assert data['run_id'] == 33296171708
    assert data['processor_canonicalization'] == 'PASS'
    assert data['data_extraction'] == 'PASS'
    assert data['canonical_page_hashes'] == 'PASS'
    assert data['nonmaterial_review_preservation'] == 'PASS'
    assert data['material_review_invalidation'] == 'PASS'
    assert data['signing'] == 'FAIL_HTTP_400'
    assert data['viewer_review_flow'] == 'UNRUN'


def test_public_judge_surface_matches_claims_ledger_truth():
    client = TestClient(app)
    html = client.get('/').text
    assert 'HOSTED NUTRIENT DWS · PASS' in html
    assert 'DWS-NATIVE V2 CORE · HOSTED PASS' in html
    assert 'SIGNING · HTTP 400' in html
    assert 'Run controlled mechanism' in html
    assert '33296171708' in html
    assert 'LIVE NUTRIENT DWS UNVERIFIED' not in html
    assert 'HOSTED DIFFERENTIAL · QUOTA BLOCKED' not in html


def test_public_surface_describes_semantic_identity_not_confidence_binding():
    client = TestClient(app)
    html = client.get('/').text
    assert 'page + field path + normalized value + bounding box tolerance' in html
    assert 'bounds and confidence' not in html
    assert '>27<' not in html
    assert 'Python 3.11-3.13' in html


def test_public_surface_explains_frozen_authority_policy_without_compliance_overclaim():
    client = TestClient(app)
    html = client.get('/').text
    assert 'Frozen Authority Policy' in html
    assert 'evidence-equivalence/1' in html
    assert 'runtime defaults cannot silently reinterpret it' in html
    assert 'SOC 2 compliant' not in html
    assert 'FDA 21 CFR Part 11 compliant' not in html


def test_public_controlled_endpoints_remain_functional():
    client = TestClient(app)
    demo = client.get('/api/demo')
    evaluation = client.get('/api/evaluation')
    assert demo.status_code == 200
    assert demo.json()['after_source_change'] == 'INVALIDATED'
    assert evaluation.status_code == 200
    assert evaluation.json()['differential_review_reuse_after_nonmaterial_file_change'] == 1
