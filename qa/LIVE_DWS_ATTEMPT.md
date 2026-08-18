# Live Nutrient DWS acceptance attempt — 2026-08-18

Status: **BLOCKED**.

The no-fallback live probe was invoked against `https://api.nutrient.io/build` with a transient user-controlled `NUTRIENT_API_KEY` and three generated, non-sensitive synthetic trade PDFs. The execution environment failed DNS resolution for `api.nutrient.io` before an HTTP response was received.

This is an environment/network blocker, not evidence that the credential or DWS request succeeded or failed. No live DWS result is claimed. The credential is intentionally absent from all repository files and retained results.

Local deterministic acceptance remains independently reproducible through the controlled fixtures and unit tests.
