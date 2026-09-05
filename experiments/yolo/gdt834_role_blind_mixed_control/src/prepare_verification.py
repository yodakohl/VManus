#!/usr/bin/env python3
"""Rebuild ignored verification resources from a result checkout; no fits.

Post-result reproduction convenience, outside the preregistered fitter. Uses
only reference and discovery data and leaves every published artifact intact.
"""
import json
import subprocess
import sys
from pathlib import Path
import run

E=Path(__file__).resolve().parents[1]
def main():
    run.verify_registration()
    runtime=E/'runtime';runtime.mkdir(exist_ok=True)
    base=E.parent/'gdt832_joint_family_context_control/src/reference_model.py'
    subprocess.run([sys.executable,str(base),'--reference',str(E/'prepared/reference.jsonl'),'--families',str(E/'prepared/families.json'),'--out',str(runtime/'reference')],check=True)
    candidates=json.loads((E/'prepared/candidates.json').read_text())
    spec=json.loads((E/'src/SPEC.json').read_text())
    for world in spec['world_ids']:
        for arm in spec['arms']:
            run.projection(E/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}discovery.json',candidates,runtime/f'world_{world}_{arm}.txt',arm)
    print('VERIFICATION_RESOURCES_READY; no fits, held data or truth read')
if __name__=='__main__':main()
