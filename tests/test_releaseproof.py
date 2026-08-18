from dataclasses import replace
from fastapi.testclient import TestClient
from releaseproof.api import app
from releaseproof.demo import load_demo_documents, run_demo
from releaseproof.engine import build_manifest, review_finding, verify_manifest
from releaseproof.model import ReleaseState

def test_review_then_verified():
    docs=load_demo_documents(); m=build_manifest(docs)
    assert m.release_state == ReleaseState.REVIEW_REQUIRED
    f=next(x for x in m.findings if x.rule_id=='LOW_CONFIDENCE')
    a=review_finding(m,f.finding_id,'reviewer','APPROVE_EXCEPTION','checked source')
    assert a.release_state == ReleaseState.VERIFIED
    assert verify_manifest(a,docs) == ReleaseState.VERIFIED

def test_source_change_invalidates():
    docs=load_demo_documents(); m=build_manifest(docs)
    f=next(x for x in m.findings if x.state == ReleaseState.REVIEW_REQUIRED)
    a=review_finding(m,f.finding_id,'reviewer','APPROVE_EXCEPTION','checked source')
    assert verify_manifest(a,load_demo_documents(True)) == ReleaseState.INVALIDATED

def test_manifest_tamper_blocks():
    docs=load_demo_documents(); m=build_manifest(docs)
    assert verify_manifest(replace(m,policy_version='tampered'),docs) == ReleaseState.BLOCKED

def test_mismatch_visible():
    m=build_manifest(load_demo_documents(True))
    assert any(f.rule_id=='CROSS_DOCUMENT_MISMATCH' and f.field=='quantity' for f in m.findings)
    assert m.release_state == ReleaseState.REVIEW_REQUIRED

def test_demo_contract():
    result=run_demo()
    assert result['initial_state']=='REVIEW_REQUIRED'
    assert result['reviewed_state']=='VERIFIED'
    assert result['verification']=='VERIFIED'
    assert result['after_source_change']=='INVALIDATED'

def test_api():
    c=TestClient(app)
    assert c.get('/health').json()['status']=='READY'
    assert c.get('/api/demo').json()['after_source_change']=='INVALIDATED'


def test_spatial_json_normalizer_preserves_grounding():
    from releaseproof.dws import normalize_spatial_json
    payload={"status":"processed","pages":[{"index":0,"elements":[{
        "type":"key_value_pair","label":"Shipment ID","value":"S-42",
        "confidence":0.97,"page":1,"bounds":[82,128,284,152]
    }]}]}
    doc=normalize_spatial_json('shipping',b'pdf-bytes',payload,field_aliases={'shipment id':'shipment_id'})
    field=doc.by_field()['shipment_id']
    assert field.value == 'S-42'
    assert field.citation.page == 1
    assert field.citation.bounds == (82.0,128.0,284.0,152.0)
    assert field.citation.confidence == 0.97
    assert field.citation.document_sha256 == doc.document_sha256


def test_spatial_json_missing_grounding_fails_closed():
    import pytest
    from releaseproof.dws import DwsError, normalize_spatial_json
    payload={"pages":[{"elements":[{"type":"key_value_pair","label":"Shipment ID","value":"S-42"}]}]}
    with pytest.raises(DwsError,match='grounding metadata'):
        normalize_spatial_json('shipping',b'pdf-bytes',payload)


def test_dws_build_request_matches_official_processor_shape(monkeypatch,tmp_path):
    from releaseproof.dws import NutrientDwsTransport
    captured={}
    class Response:
        status_code=200
        def json(self): return {"pages":[{"elements":[]}]}
    def fake_post(endpoint,headers,files,data,timeout):
        import json
        captured['endpoint']=endpoint
        captured['headers']=headers
        captured['instructions']=json.loads(data['instructions'])
        return Response()
    monkeypatch.setattr('releaseproof.dws.requests.post',fake_post)
    path=tmp_path/'packet.pdf'; path.write_bytes(b'%PDF-controlled')
    NutrientDwsTransport('test-only-key').build_json_content(path)
    assert captured['endpoint']=='https://api.nutrient.io/build'
    assert captured['headers']['Authorization']=='Bearer test-only-key'
    instructions=captured['instructions']
    assert instructions=={
        'parts':[{'file':'document'}],
        'output':{'type':'json-content','keyValuePairs':True},
    }


def test_review_is_bound_to_exact_finding_evidence():
    docs=load_demo_documents(); original=build_manifest(docs)
    f=next(x for x in original.findings if x.state == ReleaseState.REVIEW_REQUIRED)
    approved=review_finding(original,f.finding_id,'reviewer','APPROVE_EXCEPTION','checked exact source')
    changed=load_demo_documents(True)
    rebuilt=build_manifest(changed, approved.reviews)
    assert rebuilt.release_state != ReleaseState.VERIFIED
    assert verify_manifest(approved, changed) == ReleaseState.INVALIDATED


def test_differential_reverification_preserves_review_for_unchanged_evidence_slice():
 from releaseproof.engine import differential_reverify
 docs=load_demo_documents(); m=build_manifest(docs)
 f=next(x for x in m.findings if x.state == ReleaseState.REVIEW_REQUIRED)
 approved=review_finding(m,f.finding_id,'reviewer','APPROVE_EXCEPTION','checked exact slice')
 current=load_demo_documents(False,True)
 result=differential_reverify(approved,current)
 assert result.changed_documents==('invoice',)
 assert f.finding_id in result.preserved_review_ids
 assert result.invalidated_review_ids==()
 assert result.current_manifest.release_state==ReleaseState.VERIFIED
 assert result.current_manifest.manifest_sha256 != approved.manifest_sha256


def test_differential_reverification_invalidates_review_when_evidence_slice_changes():
 from releaseproof.engine import differential_reverify
 docs=load_demo_documents(); m=build_manifest(docs)
 for f in m.findings:
  if f.state == ReleaseState.REVIEW_REQUIRED:
   m=review_finding(m,f.finding_id,'reviewer','APPROVE_EXCEPTION','checked exact slice')
 result=differential_reverify(m,load_demo_documents(reviewed_invoice_changed=True))
 assert 'invoice' in result.changed_documents
 assert result.invalidated_review_ids
 assert result.current_manifest.release_state==ReleaseState.REVIEW_REQUIRED
 assert result.current_manifest.manifest_sha256 != m.manifest_sha256


def test_differential_reverification_controlled_attention_evaluation():
 from releaseproof.evaluate import run_evaluation
 r=run_evaluation()
 assert r.prior_human_reviews==1
 assert r.blanket_review_reuse_after_nonmaterial_file_change==0
 assert r.differential_review_reuse_after_nonmaterial_file_change==1
 assert r.differential_review_reuse_fraction_after_nonmaterial_file_change==1.0
 assert r.invalidated_reviews_after_reviewed_slice_change==1
 assert r.preserved_reviews_after_reviewed_slice_change==0
 assert r.nonmaterial_current_state=='VERIFIED'
 assert r.reviewed_slice_change_current_state=='REVIEW_REQUIRED'


def test_processor_json_normalizer_matches_documented_key_value_contract():
 import pytest
 from releaseproof.dws import normalize_processor_json
 payload={'pages':[{'pageIndex':0,'keyValuePairs':[{'confidence':95.4,'key':{
  'bbox':{'left':10,'top':20,'width':80,'height':10},'content':'Shipment ID'},
  'value':{'bbox':{'left':100,'top':20,'width':60,'height':10},'content':'S-42'}
 }]}]}
 doc=normalize_processor_json('shipping',b'%PDF-controlled',payload,field_aliases={'shipment id':'shipment_id'})
 field=doc.by_field()['shipment_id']
 assert field.value=='S-42'
 assert field.citation.page==1
 assert field.citation.bounds==(100.0,20.0,160.0,30.0)
 assert field.citation.confidence==pytest.approx(0.954)
 assert doc.dws_operation=='nutrient-dws:processor-json-content:keyValuePairs'


def test_processor_json_missing_value_bbox_fails_closed():
 import pytest
 from releaseproof.dws import DwsError, normalize_processor_json
 payload={'pages':[{'pageIndex':0,'keyValuePairs':[{'confidence':98,'key':{'content':'Quantity'},'value':{'content':'42'}}]}]}
 with pytest.raises(DwsError,match='bbox'):
  normalize_processor_json('invoice',b'pdf',payload)


def test_controlled_fixture_never_claims_live_dws_operation():
 doc=load_demo_documents()[0]
 assert doc.dws_operation.startswith('controlled-fixture:')
 assert 'processor-json-content' not in doc.dws_operation


def test_judge_surface_is_truthful_and_exposes_evaluation():
 c=TestClient(app)
 html=c.get('/').text
 assert 'Differential reverification' in html
 assert 'LIVE NUTRIENT DWS UNVERIFIED' in html
 assert 'Run controlled evidence path' in html
 r=c.get('/api/evaluation')
 assert r.status_code==200
 assert r.json()['differential_review_reuse_after_nonmaterial_file_change']==1


def test_evidence_slice_binding_is_scoped_to_logical_document_identity():
    from releaseproof.dws import normalize_fixture
    payload={
        'fields':[{
            'field':'quantity','value':'100','label':'Quantity','confidence':0.99,
            'page':1,'bounds':[10,20,30,40],
        }]
    }
    a=normalize_fixture('invoice',b'bytes-a',payload).fields[0].citation
    b=normalize_fixture('shipping',b'bytes-b',payload).fields[0].citation
    assert a.evidence_slice_sha256 != b.evidence_slice_sha256


def test_evidence_slice_binding_can_survive_nonmaterial_revision_within_same_logical_document():
    from releaseproof.dws import normalize_fixture
    payload={
        'fields':[{
            'field':'quantity','value':'100','label':'Quantity','confidence':0.99,
            'page':1,'bounds':[10,20,30,40],
        }]
    }
    a=normalize_fixture('invoice',b'original file bytes',payload).fields[0].citation
    b=normalize_fixture('invoice',b'revised file bytes with unrelated footer',payload).fields[0].citation
    assert a.document_sha256 != b.document_sha256
    assert a.evidence_slice_sha256 == b.evidence_slice_sha256


def test_fixture_texts_are_free_of_generation_script_artifacts():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "fixtures"
    forbidden = ('cat > "$ROOT', '/mnt/data/evidencebound-human-control-plane', "python - <<")
    for path in root.glob("*.txt"):
        text = path.read_text()
        assert not any(marker in text for marker in forbidden), path.name
