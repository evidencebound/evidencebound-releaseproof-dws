from fastapi.testclient import TestClient

from releaseproof.public_app import CANONICAL_LIVE_EVIDENCE, app


def test_public_health_exposes_accepted_live_truth_without_overclaiming():
    client = TestClient(app)
    data = client.get('/health').json()
    assert data['status'] == 'READY'
    assert data['controlled_kernel'] == 'PASS'
    assert data['public_ci'] == 'PASS'
    assert data['live_dws_core'] == 'PASS'
    assert data['live_differential_reverification'] == 'BLOCKED_QUOTA_402'
    assert data['canonical_live_run'] == 32215337912
    assert data['runtime_live_calls'] == 'DISABLED_TO_PRESERVE_EXHAUSTED_QUOTA'


def test_public_live_evidence_is_static_sanitized_receipt_not_provider_call():
    client = TestClient(app)
    data = client.get('/api/live-evidence').json()
    assert data == CANONICAL_LIVE_EVIDENCE
    assert data['status'] == 'PASS'
    assert data['document_count'] == 3
    assert data['release_state'] == 'REVIEW_REQUIRED'
    assert data['review_trigger'] == 'CROSS_DOCUMENT_MISMATCH'
    assert data['hosted_differential_reverification'] == 'BLOCKED_QUOTA_402'
    assert set(data['dws_receipts']) == {'invoice', 'shipping', 'certificate'}


def test_public_judge_surface_matches_claims_ledger_truth():
    client = TestClient(app)
    html = client.get('/').text
    assert 'HOSTED NUTRIENT DWS · PASS' in html
    assert 'HOSTED DIFFERENTIAL · QUOTA BLOCKED' in html
    assert 'Run controlled mechanism' in html
    assert '32215337912' in html
    assert 'HTTP 402' in html
    assert 'LIVE NUTRIENT DWS UNVERIFIED' not in html


def test_public_surface_describes_semantic_identity_not_confidence_binding():
    client = TestClient(app)
    html = client.get('/').text
    assert 'page + field path + normalized value + bounding box tolerance' in html
    assert 'bounds and confidence' not in html
    assert '>27<' not in html
    assert 'Python 3.11-3.13' in html


def test_public_controlled_endpoints_remain_functional():
    client = TestClient(app)
    demo = client.get('/api/demo')
    evaluation = client.get('/api/evaluation')
    assert demo.status_code == 200
    assert demo.json()['after_source_change'] == 'INVALIDATED'
    assert evaluation.status_code == 200
    assert evaluation.json()['differential_review_reuse_after_nonmaterial_file_change'] == 1
