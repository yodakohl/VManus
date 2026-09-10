# GDT901

Complete operational source network under a joint root/affix lexicon and unknown
whole-paragraph assignments. [Registered contract](METHOD.md).

Run src/run.py for all ten models' necessary count-capacity domains. Empty
required domains exclude the complete model; surviving cases require the full
registered inference. Validate source, role compiler and target projection with
the independent source checks and src/validate.py. No semantic result at registration.
# Full-model execution

Install `ortools==9.14.6206` in an isolated Python environment and run
`python3 experiments/yolo/gdt901_solmization_joint_relational_lexicon/src/run_fits.py`.
The runner launches ten cases, two solver workers each, with a shared per-case
1800-second construction/fit/projection limit and 20-second cleanup allowance.
`src/selftest_fit.py` checks complete synthetic witnesses, impossible order and
shared-root cases, independent alternative queries, and an exhaustive tiny oracle.

Result validation: `python3 experiments/yolo/gdt901_solmization_joint_relational_lexicon/src/validate_results.py`.
`artifacts/FULL_RESULT.json` aggregates both independent fixed-case executions;
`artifacts/RESULT.json` retains the earlier necessary-domain outcome unchanged.
