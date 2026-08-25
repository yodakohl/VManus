#!/usr/bin/env python3
import csv, hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

def rows(name):
    with (HERE/name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

m = rows("PASS926_354_PROCESS_MAPS.tsv")
a = rows("PASS926_1435_PHASE_ASSIGNMENTS.tsv")
checks = [
    ("clauses_354", len(m)==354, len(m)),
    ("instructions_1435", len(a)==1435, len(a)),
    ("clause_ids_unique", len({r['clause_id'] for r in m})==354, len({r['clause_id'] for r in m})),
    ("instruction_ids_unique", len({r['instruction_id'] for r in a})==1435, len({r['instruction_id'] for r in a})),
    ("pages_12", len({r['physical_page'] for r in m})==12, len({r['physical_page'] for r in m})),
    ("all_natural", all(r['natural_process_summary_de'].endswith('.') for r in m), 'summary'),
    ("all_phase_sequence", all(r['phase_run_sequence'] for r in m), 'phases'),
    ("sealed_absent", not any(x in p.read_text(encoding='utf-8',errors='ignore') for p in HERE.glob('PASS926_*') if p.suffix in ('.tsv','.md') for x in ('f84r','f84')), 'sealed'),
]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('PASS926_*') if p.is_file() and p.name not in ('PASS926_VALIDATION.json','PASS926_BUILD_SUMMARY.json')}
subprocess.run([sys.executable,str(HERE/'build_nine_hundred_twenty_sixth.py')],check=True)
after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('PASS926_*') if p.is_file() and p.name not in ('PASS926_VALIDATION.json','PASS926_BUILD_SUMMARY.json')}
checks.append(("deterministic",before==after,len(before)))
out={"status":"PASS" if all(x[1] for x in checks) else "FAIL","checks":[{"name":n,"pass":p,"detail":d} for n,p,d in checks]}
(HERE/'PASS926_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if out['status']=='PASS' else 1)
