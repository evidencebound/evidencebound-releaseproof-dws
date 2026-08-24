from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .demo import run_demo
from .evaluate import run_evaluation

CANONICAL_LIVE_EVIDENCE = {
    "evidence_class": "hosted-nutrient-dws-synthetic-packet",
    "status": "PASS",
    "run_id": 32215337912,
    "commit_sha": "d885ed31ebb8cc9449c450b0334c630c3b11f656",
    "artifact_id": 9352133498,
    "artifact_digest": "sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e",
    "manifest_sha256": "a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc",
    "document_count": 3,
    "release_state": "REVIEW_REQUIRED",
    "review_trigger": "CROSS_DOCUMENT_MISMATCH",
    "dws_receipts": {
        "invoice": "f7f472032528a8b874e3de2d48344d9274cde6a448f29530e8ac0f12acc8e7c6",
        "shipping": "cef24668bba04f610450eb87fdf873bcdcf45b1e6a9b226865857604f608c135",
        "certificate": "8d0b635918e4d42a2f85584a51b6ea52c0f36222b73322242d761317e5d3c4ab",
    },
    "page_provenance": "ordered-page-position",
    "hosted_differential_reverification": "BLOCKED_QUOTA_402",
    "quota_boundary_run_id": 32215515505,
}

app = FastAPI(title="ReleaseProof Judge Surface", version="0.5.0")


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "READY",
        "controlled_kernel": "PASS",
        "public_ci": "PASS",
        "live_dws_core": "PASS",
        "dws_native_v2_hosted": "UNRUN",
        "live_differential_reverification": "BLOCKED_QUOTA_402",
        "canonical_live_run": CANONICAL_LIVE_EVIDENCE["run_id"],
        "runtime_live_calls": "DISABLED_TO_PRESERVE_EXHAUSTED_QUOTA",
    }


@app.get("/api/demo")
def demo() -> dict:
    return run_demo()


@app.get("/api/evaluation")
def evaluation() -> dict:
    return asdict(run_evaluation())


@app.get("/api/live-evidence")
def live_evidence() -> dict:
    return CANONICAL_LIVE_EVIDENCE


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ReleaseProof - Proof-Carrying Document Decisions</title>
<style>
:root{--bg:#f4f6f9;--panel:#fff;--ink:#101522;--muted:#5e687b;--line:#dce2ea;--blue:#244bd8;--green:#087a4b;--amber:#a25d00;--red:#b32836;--soft:#eef2ff}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#f8f9fb 0,#f2f5f8 100%);color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}.wrap{max-width:1180px;margin:auto;padding:40px 22px 70px}.panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;box-shadow:0 9px 30px rgba(16,21,34,.05)}.hero{display:grid;grid-template-columns:1.5fr .8fr;gap:18px}.kicker{font-size:12px;font-weight:850;letter-spacing:.13em;text-transform:uppercase;color:var(--blue)}h1{font-size:44px;line-height:1.02;letter-spacing:-.045em;margin:10px 0 14px}.lead{font-size:18px;color:var(--muted);max-width:780px}.badges{display:flex;gap:8px;flex-wrap:wrap;margin:19px 0}.badge{font-size:12px;font-weight:850;padding:7px 10px;border-radius:999px;background:#e9f7f0;color:var(--green)}.badge.warn{background:#fff2db;color:var(--amber)}.badge.blue{background:var(--soft);color:var(--blue)}button{border:0;border-radius:11px;background:var(--ink);color:#fff;padding:11px 15px;font-weight:800;cursor:pointer}button.alt{background:var(--soft);color:var(--blue)}.row{display:flex;gap:9px;flex-wrap:wrap}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:12px}.metric{border:1px solid var(--line);border-radius:14px;padding:16px}.num{font-size:30px;font-weight:900;letter-spacing:-.04em}.small{color:var(--muted);font-size:13px}.section{margin-top:18px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.state{font-weight:900}.ok{color:var(--green)}.warntext{color:var(--amber)}.code{background:#101522;color:#dce7ff;padding:18px;border-radius:14px;overflow:auto;max-height:470px;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace}.callout{border-left:4px solid var(--blue);background:var(--soft);border-radius:0 12px 12px 0;padding:14px 16px}.proof{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:800px){.hero,.proof{grid-template-columns:1fr}.grid3,.metrics{grid-template-columns:1fr}h1{font-size:35px}}
</style></head><body><main class="wrap">
<section class="hero"><div class="panel"><div class="kicker">Nutrient DWS Challenge · Judge Surface</div><h1>ReleaseProof</h1><p class="lead">A proof-carrying release lifecycle for document-driven autonomous work. Human review survives only when the same logical finding still reproduces from equivalent source-grounded evidence under the rules frozen when that authority was granted.</p><div class="badges"><span class="badge">HOSTED NUTRIENT DWS · PASS</span><span class="badge">PUBLIC CI · PASS</span><span class="badge blue">DWS-NATIVE V2 · CONTRACT TESTED / HOSTED UNRUN</span><span class="badge warn">HOSTED DIFFERENTIAL · QUOTA BLOCKED</span></div><div class="row"><button onclick="runControlled()">Run controlled mechanism</button><button class="alt" onclick="loadLive()">Show hosted DWS evidence</button></div></div>
<div class="panel"><div class="kicker">Evidence summary</div><div class="metrics"><div class="metric"><div class="num">3</div><div class="small">PDFs processed by hosted DWS</div></div><div class="metric"><div class="num">3</div><div class="small">Python 3.11-3.13 CI lanes</div></div><div class="metric"><div class="num">1/1</div><div class="small">controlled review preserved after non-material revision</div></div><div class="metric"><div class="num">0/1</div><div class="small">review preserved after reviewed evidence changed</div></div></div></div></section>
<section class="section grid3"><div class="panel"><div class="kicker">Live document operation</div><h2 class="state ok">PASS</h2><p>Historical hosted Processor <code>/build</code>, JSON key-value extraction, response receipt hashes, page/bbox/confidence grounding.</p></div><div class="panel"><div class="kicker">Live trust decision</div><h2 class="state warntext">REVIEW_REQUIRED</h2><p>Hosted extraction produced a cross-document Shipment ID disagreement. ReleaseProof surfaced it instead of silently releasing.</p></div><div class="panel"><div class="kicker">Current external blocker</div><h2 class="state warntext">HTTP 402</h2><p>The account quota was exhausted before the hosted Differential Reverification rerun. No success claim is made for that experiment.</p></div></section>
<section class="section proof"><div class="panel"><h2>Differential Reverification</h2><div class="callout">A file hash changing is not enough reason to discard human work. ReleaseProof separates integrity from semantic review identity. The review key is page + field path + normalized value + bounding box tolerance. Confidence still routes uncertain evidence to review, but it does not define whether the business evidence itself is the same.</div><p class="small">Controlled evidence: semantically unchanged reviewed evidence preserves 1/1 prior review; material value or out-of-tolerance location change preserves 0/1. The current packet always receives a new manifest.</p></div><div class="panel"><h2>DWS-native v2 boundary</h2><p class="small">Processor owns canonical OCR/flatten/page operations. Data Extraction owns source grounding. Viewer annotations/layers/comments are the target review surface. Processor <code>/sign</code> is the target signed artifact path. These v2 contracts are tested in public CI but remain hosted UNRUN.</p><button class="alt" onclick="loadLive()">Load historical hosted receipt</button></div></section>
<section class="section panel"><div class="kicker">Frozen Authority Policy</div><h2>The human decision carries its own rules of continued validity</h2><div class="callout">Each new semantic review stores <code>evidence-equivalence/1</code>, its bbox tolerance, value-normalization version and bbox metric. Differential Reverification evaluates that review under its historical policy, so runtime defaults cannot silently reinterpret it.</div><p class="small">Controlled CI proves that a review granted at tolerance 2.0 is still invalidated after a 4px evidence move even if a later runtime passes tolerance 10.0. Unknown policy versions fail closed to review. This is an auditability and deterministic replay mechanism, not a regulatory certification claim.</p></section>
<section class="section panel"><h2>Canonical hosted proof</h2><p class="small">Run <b>32215337912</b> · 3 documents · source grounding PASS · historical manifest generated · DWS receipts retained. Live calls are disabled on this public surface so judge traffic cannot consume provider quota.</p></section>
<section class="section panel"><h2>Evidence ledger</h2><pre id="out" class="code">Choose a proof path above.</pre></section>
</main><script>
const out=document.getElementById('out');
async function runControlled(){const [d,e]=await Promise.all([fetch('/api/demo').then(r=>r.json()),fetch('/api/evaluation').then(r=>r.json())]);out.textContent=JSON.stringify({evidence_class:'controlled-mechanism',demo:d,evaluation:e},null,2)}
async function loadLive(){const e=await fetch('/api/live-evidence').then(r=>r.json());out.textContent=JSON.stringify(e,null,2)}
</script></body></html>'''
