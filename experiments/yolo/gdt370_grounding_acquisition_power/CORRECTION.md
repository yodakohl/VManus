# GDT370 serialization correction

After the frozen simulation ran, repository `diff --check` identified CRLF
line endings in the two generated TSV files as trailing whitespace. The TSV
writer was changed to emit LF explicitly and the deterministic simulation was
rerun with the same method, grid, seed, and 256 trials. Numerical values and
the scientific outcome did not change. This is a serialization correction,
not a design or outcome change.
