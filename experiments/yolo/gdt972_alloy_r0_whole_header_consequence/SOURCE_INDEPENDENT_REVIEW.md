# GDT972 independent contract review

**Bounded pre-target review, 15 September 2026.** This validator checks the necessary R0 whole-account header conditions only. It does not decode, score, parse the body, fit the 38-atom code, assign numerical values, or make a semantic claim.

## Frozen bindings

- Protocol: `PREREGISTRATION.md` in this directory.
- Source grammar: `research_registry/work_batches/ten_hours_20260915/ALLOY_FINITE_GRAMMAR.json`.
- Bound complete-paragraph cache (read only after public registration): `experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json`.
- The bound cache is expected to contain all 1,349 complete rows, including 561 literal eligible rows and 788 nonliteral rows. These denominators are protocol expectations, not hardcoded positive outcomes.
- No private absolute path is required. Registration records repository-relative bindings and hashes of the public protocol/grammar files.

## Independent header reconstruction

For each complete paragraph, the first 12 groups are inspected at the fixed positions:

`0 GRADES, 1 A, 2 NUM(a), 3 B, 4 NUM(b), 5 C, 6 NUM(c), 7 TARGET, 8 NUM(t), 9 TOTAL, 10 NUM(m), 11 FIRST`.

The validator records every condition, even when an earlier one fails:

1. at least 14 complete groups;
2. seven atomic words at positions 0,1,3,5,7,9,11, each length 1–8;
3. those seven words pairwise distinct;
4. those seven words pairwise prefix-incomparable;
5. five numeric words at positions 2,4,6,8,10, each length 2–32;
6. the four grade/target words at 2,4,6,8 pairwise distinct;
7. every candidate common `NUM` prefix of length 1–8 that is shorter than all five numeric words and prefix-incomparable with all seven atomic words. The registered R0 header screen does not choose or test a suffix segmentation here.

All valid NUM-prefix candidates are retained. Nonliteral rows are retained with their recorded defects; they are not repaired into lowercase groups.

The first-failure order is `group_count`, `atomic_length`, `atomic_distinct`, `atomic_prefix_free`, `numeric_length`, `grade_target_distinct`, `num_prefix`; all criterion values remain present. Full mode independently constructs all row records before opening the public RESULT, then requires an exact row-list comparison and nonzero failure on mismatch.

## Scope ceiling

A positive row or summary can establish only compatibility with these necessary header conditions for the unchanged R0 representation. It cannot establish a complete grammar parse, a shared code, arithmetic, a source copy, a language, a word, or a Voynich meaning. A zero survivor result would reject the fixed R0 header within the declared literal cache, while leaving other grammars and semantic architectures open.

Default execution is registration-only while RESULT is absent; after execution it validates the full result. Explicit --registration-only never opens the target cache. Full execution is intended only after public registration and primary enumeration. No source/key/prefix, header deletion, or target-driven rule adjustment is allowed after the outcome.

## Pre-publication implementation corrections

Before any target header enumeration, root corrected the independently drafted validator's guessed input/output schemas, summary survivor type and status, independent-condition handling, exact TSV comparison, binding/scope checks and failure exit. An extra suffix segmentation restriction was removed because it was outside the registered necessary screen. No primary predicate or frozen protocol changed. The independently drafted header evaluator remains separate from the primary runner; validation is not a blinded semantic replication.

## First full-run validator intake correction

After the frozen primary census, the first full validator run stopped before comparison because its `full_text.split(" ")` reconstruction split internal spaces inside nonliteral cached groups. The primary correctly preserves cached line word lists and checks `" ".join(words) == full_text`. The validator was corrected to check that same textual identity while retaining the cached group boundaries. No eligibility, header predicate, primary result or preregistration changed. The initial validator failure is an intake implementation error, not a manuscript contradiction or independent confirmation.
