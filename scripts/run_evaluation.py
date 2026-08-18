from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
from releaseproof.evaluate import run_evaluation

if __name__=='__main__':
    result=asdict(run_evaluation())
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    Path('results').mkdir(exist_ok=True)
    Path('results/evaluation.json').write_text(text)
    print(text,end='')
