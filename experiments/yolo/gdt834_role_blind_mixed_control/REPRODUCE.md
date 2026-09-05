# Reproduce GDT834

Python 3, NumPy, Git and a C++17 compiler are needed. No GPU, external LLM
service or API key is used. The largest reference model is built once; the
fit runner uses at most 24 CPU workers. Runtime files are ignored by Git.

The pinned UDante source commit is
`e02420457780c6fbb503ba39a7d8798ab6a8645c`. Its upstream repository is
`https://github.com/UniversalDependencies/UD_Latin-UDante.git`; attribution,
license and file commitments are in `sources/`. Put a checkout at that commit
under `experiments/yolo/gdt834_role_blind_mixed_control/runtime/udante_source`.
Keep source acquisition separate from fit evaluation.

From the repository root:

```sh
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/prepare.py --phase all
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/role_audit.py --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/role_audit.py --fresh --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/test_roles.py
```

Run the independent source-only audit before fitting:

```sh
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/validate.py --capacity-only --check
```

Source generation is deterministic and checks its commitments. It never
changes a failed split or support threshold. `CAPACITY.json` is preserved as
the pre-key snapshot; `GENERATION.json` records subsequent key generation.

To verify an existing result checkout without running any new fit, prepare the
ignored reference model and discovery projections, then replay:

```sh
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/prepare_verification.py
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/run.py --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/evaluate.py --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/validate.py --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/post_result_audit.py --check
```

`prepare_verification.py` is a post-result convenience, outside the registered
fitter; it rebuilds runtime resources only and never fits or changes results.

For a fresh fit reproduction, use public preregistration commit
`1daf02ee1bf5bc74db9b1dbb5f86ec208bafa0a7`, with the source checkout above. The runner rejects an
existing FIT_LOCK.json, so a result checkout is for verification, not silent
overwriting. The exact frozen fit is:

```sh
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/run.py --fit
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/run.py --check
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/evaluate.py
python3 experiments/yolo/gdt834_role_blind_mixed_control/src/validate.py --check
```

Evaluation is permitted only after all 48 restarts and six selections have
been locked. Comparing fresh fit hashes should disregard no scientific field;
there are no timing fields in fit artifacts. Three encryption keys share one
historical text split, and exact original normalized spelling is always gold.
