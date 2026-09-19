"""Bind unchanged registration plus explicit post-result gate/review sources."""
import hashlib,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
subprocess.run([sys.executable,str(E/'src/bind.py')],check=True)
m=json.loads((E/'experiment.json').read_text())
for n in ['tools/relation_edge_intake.py','tools/vmanus_experiment.py',
          'experiments/yolo/gdt751_q_base_carrier_shell_audit/REPORT.md',
          'experiments/yolo/gdt820_grouped_predicate_repetition_context/REPORT.md',
          'experiments/yolo/gdt822_qokeey_physical_fire_context/WORKING_THEORY.md',
          'research_registry/proposals/translation_programs_20260912/work/W70/REPORT.md']:
    assert n not in {i['path'] for i in m['inputs']}
    m['inputs'].append(dict(path=n,role='post_result_gate_or_next_route_review',sha256=hashlib.sha256((R/n).read_bytes()).hexdigest()))
(E/'experiment.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
