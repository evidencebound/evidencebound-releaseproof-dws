from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI(title="ReleaseProof Judge Evidence Surface", version="1.0.1")

LIVE = {
    "surface_class": "EVIDENCE_SURFACE",
    "mechanism_source": "https://github.com/moneyparking/evidencebound-releaseproof-dws",
    "public_main_observed": "030a22828cf70f44ab4b7885377a9c6665ad0a0b",
    "hosted_nutrient_dws_core": "PASS",
    "canonical_run_id": 32215337912,
    "canonical_commit_sha": "d885ed31ebb8cc9449c450b0334c630c3b11f656",
    "artifact_id": 9352133498,
    "artifact_digest": "sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e",
    "manifest_sha256": "a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc",
    "document_count": 3,
    "release_state": "REVIEW_REQUIRED",
    "review_trigger": "CROSS_DOCUMENT_MISMATCH",
    "page_provenance": "ordered-page-position",
    "dws_receipts": {
        "invoice": "f7f472032528a8b874e3de2d48344d9274cde6a448f29530e8ac0f12acc8e7c6",
        "shipping": "cef24668bba04f610450eb87fdf873bcdcf45b1e6a9b226865857604f608c135",
        "certificate": "8d0b635918e4d42a2f85584a51b6ea52c0f36222b73322242d761317e5d3c4ab",
    },
    "hosted_differential_reverification": "BLOCKED_QUOTA_402",
    "quota_boundary_run_id": 32215515505,
    "runtime_live_calls": "DISABLED",
}

CONTROLLED = {
    "evidence_class": "controlled-mechanism",
    "prior_human_reviews": 1,
    "blanket_review_reuse_after_nonmaterial_file_change": 0,
    "differential_review_reuse_after_nonmaterial_file_change": 1,
    "invalidated_reviews_after_reviewed_slice_change": 1,
    "preserved_reviews_after_reviewed_slice_change": 0,
    "nonmaterial_current_state": "VERIFIED",
    "reviewed_slice_change_current_state": "REVIEW_REQUIRED",
    "claim_boundary": "controlled deterministic evidence; not a real reviewer-time metric",
}


@app.get("/health")
def health():
    return {
        "status": "READY",
        "surface_class": "EVIDENCE_SURFACE",
        "public_ci": "PASS",
        "live_dws_core": "PASS",
        "live_differential_reverification": "BLOCKED_QUOTA_402",
        "runtime_live_calls": "DISABLED",
    }


@app.get("/api/live-evidence")
def live_evidence():
    return LIVE


@app.get("/api/evaluation")
def evaluation():
    return CONTROLLED


@app.get("/api/demo")
def demo():
    return {
        "initial_state": "REVIEW_REQUIRED",
        "reviewed_state": "VERIFIED",
        "nonmaterial_revision": {"review_preserved": 1, "current_state": "VERIFIED"},
        "reviewed_slice_revision": {"review_invalidated": 1, "current_state": "REVIEW_REQUIRED"},
        "source": "public repository controlled mechanism",
    }


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.png", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
def index():
    return '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ReleaseProof — Judge Evidence</title><style>body{margin:0;background:#f4f6f9;color:#111827;font:15px/1.5 system-ui}.w{max-width:1080px;margin:auto;padding:42px 22px}.p{background:#fff;border:1px solid #dde3eb;border-radius:18px;padding:24px;margin-bottom:16px;box-shadow:0 8px 25px #1111}.hero{display:grid;grid-template-columns:1.4fr .8fr;gap:16px}h1{font-size:44px;line-height:1;margin:8px 0 14px}.k{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#3156d3}.b{display:inline-block;padding:6px 10px;margin:4px;border-radius:999px;font-weight:800;font-size:12px;background:#e9f7f0;color:#087a4b}.warn{background:#fff2db;color:#a25d00}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.n{font-size:30px;font-weight:900}.muted{color:#657083}.code{white-space:pre-wrap;background:#101522;color:#dce7ff;padding:16px;border-radius:12px;max-height:420px;overflow:auto}button{border:0;border-radius:10px;padding:10px 14px;font-weight:800;cursor:pointer;margin-right:8px}@media(max-width:760px){.hero,.grid{grid-template-columns:1fr}h1{font-size:35px}}</style></head><body><main class="w"><section class="hero"><div class="p"><div class="k">Nutrient DWS Challenge · Evidence Surface</div><h1>ReleaseProof</h1><p class="muted">Differential Reverification: preserve human review only when the exact source-grounded finding binding still reproduces. This deployment is an evidence surface; executable mechanism source and tests remain in the public repository.</p><span class="b">HOSTED DWS CORE · PASS</span><span class="b">PUBLIC CI · PASS</span><span class="b warn">HOSTED DIFFERENTIAL · QUOTA BLOCKED</span><p><button onclick="load('/api/live-evidence')">Hosted proof</button><button onclick="load('/api/evaluation')">Controlled evaluation</button></p></div><div class="p"><div class="k">Canonical proof</div><div class="n">3 PDFs</div><p class="muted">Processed through real Nutrient Processor /build.</p><div class="n">REVIEW_REQUIRED</div><p class="muted">Cross-document mismatch surfaced instead of silent release.</p></div></section><section class="grid"><div class="p"><div class="k">Core DWS</div><h2>PASS</h2><p>Receipt hashes + page/bbox/confidence grounding retained.</p></div><div class="p"><div class="k">Differential mechanism</div><h2>PASS</h2><p>Controlled: 1/1 review survives non-material revision; 0/1 survives reviewed-slice change.</p></div><div class="p"><div class="k">External boundary</div><h2>HTTP 402</h2><p>Hosted differential rerun blocked by exhausted free processing credits. No pass claim.</p></div></section><section class="p"><h2>Evidence ledger</h2><div id="o" class="code">Select an evidence path.</div></section></main><script>async function load(p){document.getElementById('o').textContent=JSON.stringify(await fetch(p).then(r=>r.json()),null,2)}</script></body></html>'''
