# GDT051 — revised hybrid register compiler (HPR-2)

## Purpose

This is an abductive synthesis after GDT008–GDT050. It revises the earlier
HPR-1 generator wherever subsequent tests supplied a stronger attribution or
a counterexample. It does not fit a language, mapping, lexicon, or translation.

The runner binds every material supporting result, verifies selected real
complete-line examples from the frozen GDT016 inventory, and emits:

- a machine-readable layered generator;
- an evidence/status table distinguishing supported, provisional, weak, and
  rejected components;
- representative real line parses; and
- new non-f84 predictions for later tests.

The synthesis may choose a leading theory, but every semantic function remains
explicitly provisional. f84r is skipped before inventory retention and is not
used as an example or prediction target.
