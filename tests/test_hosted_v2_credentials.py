from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


def _load_acceptance_module(monkeypatch):
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    path = scripts_dir / "run_live_dws_v2_acceptance.py"
    spec = importlib.util.spec_from_file_location("releaseproof_hosted_v2_acceptance", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_hosted_v2_requires_distinct_data_extraction_product_key(monkeypatch, tmp_path):
    module = _load_acceptance_module(monkeypatch)
    monkeypatch.setenv("NUTRIENT_API_KEY", "processor-key-for-contract-test")
    monkeypatch.delenv("NUTRIENT_DATA_EXTRACTION_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="NUTRIENT_DATA_EXTRACTION_API_KEY"):
        module.run(tmp_path, tmp_path / "signed.pdf")


def test_live_workflow_preflights_both_product_keys():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "live-dws-v2.yml").read_text()
    assert "NUTRIENT_API_KEY: ${{ secrets.NUTRIENT_API_KEY }}" in workflow
    assert (
        "NUTRIENT_DATA_EXTRACTION_API_KEY: ${{ secrets.NUTRIENT_DATA_EXTRACTION_API_KEY }}"
        in workflow
    )
