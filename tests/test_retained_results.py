from dataclasses import asdict
import json
from pathlib import Path

from releaseproof.demo import run_demo
from releaseproof.evaluate import run_evaluation


ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: str):
    return json.loads((ROOT / path).read_text())


def test_retained_controlled_demo_matches_current_mechanism():
    assert _read_json("results/controlled-demo.json") == run_demo()


def test_retained_evaluation_matches_current_mechanism():
    assert _read_json("results/evaluation.json") == asdict(run_evaluation())
