# ReleaseProof — Differential Reverification with Nutrient DWS

**One-line pitch:** After a document packet changes, ReleaseProof reprocesses the current evidence and preserves a prior human exception only when the exact document-scoped source-grounded finding binding still reproduces; otherwise the old review cannot release the new packet.

## Controlled judge path

```bash
python -m pip install -e '.[dev]' --no-build-isolation
PYTHONPATH=src pytest
PYTHONPATH=src uvicorn releaseproof.api:app --host 127.0.0.1 --port 8080
```

The controlled path demonstrates:

- initial reconciliation -> `REVIEW_REQUIRED`;
- scoped human review -> `VERIFIED`;
- non-material file revision -> new manifest while an unchanged scoped review is preserved;
- change to the reviewed evidence slice -> review invalidated and current packet returns to `REVIEW_REQUIRED`.

Controlled fixtures are explicitly labelled `controlled-fixture:nutrient-shaped` and are never claimed as live DWS execution.

## Nutrient DWS core operation

`NutrientDwsTransport` implements the hosted Processor `/build` path using multipart PDF input and `json-content` with `keyValuePairs: true`. `normalize_processor_json()` accepts only source-grounded key/value results with page index, confidence, value content and bounding box; missing grounding fails closed.

The API key is read only from server-side `NUTRIENT_API_KEY`. `scripts/run_live_dws_probe.py` has no fixture fallback and must process all three real packet documents before live DWS can be marked PASS.

Current live DWS status: **BLOCKED by execution environment network**. A user-controlled key was provisioned transiently for an acceptance attempt on 2026-08-18, but this sandbox could not resolve `api.nutrient.io`; the key was not persisted to source, fixtures, logs, or GitHub. Therefore live DWS remains unverified rather than being converted to PASS.

## Controlled evaluation

In the retained fixture evaluation, a whole-file non-material revision causes a blanket-version baseline to preserve `0/1` prior reviews while Differential Reverification preserves `1/1`; when the reviewed evidence slice changes, it preserves `0/1` and requires review again. These are fixture-level mechanism results, not measured staff-time savings.

See `results/evaluation.json` and `docs/claims-ledger.md`.
