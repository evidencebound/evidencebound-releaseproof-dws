from __future__ import annotations
from dataclasses import asdict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .demo import run_demo
from .evaluate import run_evaluation

app = FastAPI(title="ReleaseProof", version="0.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "READY", "live_dws": "UNVERIFIED"}


@app.get("/api/demo")
def demo() -> dict:
    return run_demo()


@app.get('/api/evaluation')
def evaluation() -> dict:
    return asdict(run_evaluation())


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ReleaseProof — Differential Reverification</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#14171f;--muted:#606879;--line:#dfe3ea;--ok:#136f46;--warn:#9b5d00;--bad:#a72b2b;--accent:#3156d3;--soft:#eef2ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}.wrap{max-width:1180px;margin:auto;padding:42px 24px 72px}.hero{display:grid;grid-template-columns:1.45fr .8fr;gap:28px;align-items:stretch}.panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;box-shadow:0 8px 28px rgba(20,23,31,.05)}.kicker{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}h1{font-size:42px;line-height:1.05;margin:10px 0 14px;letter-spacing:-.04em}.lead{font-size:18px;color:var(--muted);max-width:760px}.truth{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}.badge{padding:6px 10px;border-radius:999px;font-size:12px;font-weight:800;background:#edf8f2;color:var(--ok)}.badge.unverified{background:#fff4df;color:var(--warn)}.metric{font-size:34px;font-weight:850;letter-spacing:-.04em}.metric-label{color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:18px}.section{margin-top:24px}.section h2{font-size:20px;margin:0 0 12px}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.step{padding:16px;border:1px solid var(--line);border-radius:14px;background:#fff}.step b{display:block;margin-bottom:5px}.state{font-weight:800}.VERIFIED{color:var(--ok)}.REVIEW_REQUIRED{color:var(--warn)}.INVALIDATED,.BLOCKED{color:var(--bad)}button{border:0;border-radius:12px;background:var(--ink);color:white;padding:12px 16px;font-weight:750;cursor:pointer}button.secondary{background:var(--soft);color:var(--accent)}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.evidence{display:grid;grid-template-columns:1fr 1fr;gap:16px}.code{background:#11151d;color:#dfe8ff;border-radius:14px;padding:18px;overflow:auto;max-height:430px;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace}.callout{border-left:4px solid var(--accent);padding:14px 16px;background:var(--soft);border-radius:0 12px 12px 0;color:#34405c}.small{font-size:13px;color:var(--muted)}@media(max-width:850px){.hero,.evidence{grid-template-columns:1fr}.grid,.steps{grid-template-columns:1fr 1fr}h1{font-size:34px}}@media(max-width:560px){.grid,.steps{grid-template-columns:1fr}}
</style></head><body><main class="wrap">
<section class="hero"><div class="panel"><div class="kicker">Nutrient DWS Challenge · Controlled Judge Surface</div><h1>ReleaseProof</h1><p class="lead">Differential reverification for document-driven autonomous work: preserve a human review only when the exact source-grounded evidence slice still reproduces; invalidate it when the reviewed evidence changes.</p><div class="truth"><span class="badge">CONTROLLED KERNEL READY</span><span class="badge unverified">LIVE NUTRIENT DWS UNVERIFIED</span><span class="badge">FAIL-CLOSED</span></div><div class="section row"><button onclick="runDemo()">Run controlled evidence path</button><button class="secondary" onclick="loadEval()">Load evaluation</button></div></div>
<div class="panel"><div class="kicker">Controlled result</div><div class="grid"><div><div id="reuse" class="metric">—</div><div class="metric-label">review reuse after non-material revision</div></div><div><div id="invalidate" class="metric">—</div><div class="metric-label">review invalidated after reviewed slice changes</div></div><div><div class="metric">0</div><div class="metric-label">live DWS claims made by this page</div></div></div><p class="small">Fixture evidence is labeled controlled and never promoted to observed DWS output.</p></div></section>

<section class="section panel"><h2>One packet, four trust states</h2><div class="steps"><div class="step"><b>1 · Extract & reconcile</b><span id="s1" class="state">NOT RUN</span><div class="small">Source-grounded fields + confidence</div></div><div class="step"><b>2 · Human review</b><span id="s2" class="state">NOT RUN</span><div class="small">Review binds exact evidence slice</div></div><div class="step"><b>3 · Non-material revision</b><span id="s3" class="state">NOT RUN</span><div class="small">New manifest; valid review may survive</div></div><div class="step"><b>4 · Reviewed slice changes</b><span id="s4" class="state">NOT RUN</span><div class="small">Old review cannot release current packet</div></div></div></section>

<section class="section evidence"><div class="panel"><h2>Why this is not a version hash demo</h2><div class="callout">A whole-document hash always changes when the file changes. ReleaseProof reprocesses the current packet and preserves human work only when the current finding reproduces the same normalized evidence binding: logical document, field, label, value, page, bounds, and confidence. The whole-file hash still binds the new manifest, not the reusable review token.</div><p class="small">The old manifest itself never becomes current after any document revision. Differential Reverification mints a new manifest.</p></div><div class="panel"><h2>Current mechanism evidence</h2><div id="summary" class="small">Run the controlled path. Live `/build` remains blocked until a user-controlled Nutrient API key is provisioned and the exact response is externally verified.</div></div></section>

<section class="section panel"><h2>Evidence ledger</h2><pre id="out" class="code">No controlled run yet.</pre></section>
</main><script>
function state(id,v){const e=document.getElementById(id);e.textContent=v;e.className='state '+v}
async function runDemo(){const r=await fetch('/api/demo').then(x=>x.json());state('s1',r.initial_state);state('s2',r.reviewed_state);state('s3',r.nonmaterial_revision.current_state);state('s4',r.reviewed_slice_revision.current_state);document.getElementById('summary').textContent=`Non-material revision changed ${r.nonmaterial_revision.changed_documents.join(', ')} but preserved ${r.nonmaterial_revision.preserved_review_ids.length} scoped review(s). Reviewed-slice revision invalidated ${r.reviewed_slice_revision.invalidated_review_ids.length} scoped review(s). Historical manifest verification after a material source change: ${r.after_source_change}.`;document.getElementById('out').textContent=JSON.stringify(r,null,2);await loadEval()}
async function loadEval(){const r=await fetch('/api/evaluation').then(x=>x.json());document.getElementById('reuse').textContent=`${r.differential_review_reuse_after_nonmaterial_file_change}/${r.prior_human_reviews}`;document.getElementById('invalidate').textContent=`${r.invalidated_reviews_after_reviewed_slice_change}/${r.prior_human_reviews}`}
</script></body></html>'''
