# GDT1092 method

The [preregistration](PREREGISTRATION.md) froze the source signature and strict
four-feature decision before f25v image access. The [scope note](../../../docs/VOYNICH_DATA_SCOPE_20260929_F25V_IMAGE.md)
admitted only Yale canvas 1006123. Official URLs, 1500px download hashes and
sizes are in `src/SOURCE.tsv`; binaries are not copied into this experiment.
`src/OBSERVED.tsv` holds all four fixed judgments and discrepancies. `src/run.py`
checks the complete input and writes the fixed decision; `src/validate.py`
replays it. Code verifies completeness and arithmetic, not visual judgment.
