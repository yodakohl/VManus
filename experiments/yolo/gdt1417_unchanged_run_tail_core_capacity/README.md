# GDT1417 joint unchanged-core capacity

One pre-decoder gate on the raw words unaffected by both long e/i-run changes and dy-end changes. No full writer/decoder, meanings unassigned. Python3 and z3-solver required.

    python3 experiments/yolo/gdt1417_unchanged_run_tail_core_capacity/src/run.py --gate
    python3 experiments/yolo/gdt1417_unchanged_run_tail_core_capacity/src/validate.py --gate
    python3 experiments/yolo/gdt1417_unchanged_run_tail_core_capacity/src/run.py --native
    python3 experiments/yolo/gdt1417_unchanged_run_tail_core_capacity/src/validate.py --native

Native requires independent gate PASS. See METHOD.md and PREREGISTRATION.md.
