# RTA001 transparent operator DSL

Status: frozen before extraction of RTA001 edge programs.

## Purpose and representations

RTA001 describes how one already paired text position differs from another.  It
does not assign a meaning to either position.  The same language is applied
separately to five token streams: manual-transcription characters, STA
families, exact STA members, literal roots, and construction roles plus
boundaries.  A program is always interpreted relative to its source stream.

`BOS`, `EOS`, and `WB` are structural sentinels, not manuscript glyphs.  Program
arguments are JSON strings or lists of strings.  Operators retained by the
experiment are named only `OP01`, `OP02`, and so on.

## Primitive operations and code lengths

All lengths below are in bits.  `U(n) = 2*floor(log2(n+1))+1` is the frozen
universal positive-integer code.  `V` is the vocabulary size of the current
representation in the training fold only.  A literal token costs
`ceil(log2(V+1))` bits.  The operation tag costs 4 bits.

| operation | exact action | argument cost after the 4-bit tag |
|---|---|---:|
| `KEEP` | copy one source token | 0 |
| `DELETE` | consume one source token | `U(1)` |
| `INSERT` | emit one literal token | `U(1) + literal` |
| `SUBSTITUTE` | consume one token and emit one literal token | `U(1) + literal` |
| `ADD_PREFIX` | emit a literal sequence before the retained core | `U(length) + literals` |
| `DROP_PREFIX` | consume a sequence before the retained core | `U(length)` |
| `ADD_SUFFIX` | emit a literal sequence after the retained core | `U(length) + literals` |
| `DROP_SUFFIX` | consume a sequence after the retained core | `U(length)` |
| `REPLACE_PREFIX` | replace a leading source sequence | `U(source length)+U(target length)+target literals` |
| `REPLACE_SUFFIX` | replace a trailing source sequence | `U(source length)+U(target length)+target literals` |
| `MERGE_BOUNDARY` | consume one `WB` | `U(1)` |
| `SPLIT_BOUNDARY` | emit one `WB` | `U(1)` |
| `ADD_CARRIER` | emit a registered carrier token | `U(1) + literal` |
| `DROP_CARRIER` | consume a registered carrier token | `U(1)` |
| `REPLACE_ROOT_CLASS` | substitute one literal-root token | `U(1) + literal` |
| `KEEP_CORE` | copy a maximal nonempty contiguous source subsequence | `U(length)` |
| `REORDER_LOCAL_COMPONENTS` | emit a permutation of a source window of length 2--4 | `U(length) + ceil(log2(length!))` |

There are no learned special-case opcodes.  A retained operator is an explicit
template over these primitives.  Literal parameters are permitted, but their
description length prevents a library of memorized labels from being free.

## Canonical exact program

The CPU extractor first computes all minimum-cost Levenshtein alignments using
integer primitive costs `KEEP=0`, `DELETE=2`, `INSERT=2`, and `SUBSTITUTE=3`.
It stores the exact number of optimal alignments.  Ties are broken only for the
canonical rendering by operation order `KEEP < SUBSTITUTE < DELETE < INSERT`
and then by UTF-8 argument bytes.

The canonical alignment is compressed, without changing its action, in this
order:

1. an unchanged maximal contiguous run becomes `KEEP_CORE`;
2. leading edit runs become the applicable prefix operation;
3. trailing edit runs become the applicable suffix operation;
4. `WB` deletion/insertion becomes `MERGE_BOUNDARY`/`SPLIT_BOUNDARY`;
5. carrier addition/deletion is named only when the representation itself
   supplies a registered carrier token;
6. root substitutions become `REPLACE_ROOT_CLASS` only in the literal-root
   representation;
7. a length 2--4 pure permutation becomes `REORDER_LOCAL_COMPONENTS`;
8. all remaining actions retain their primitive names.

The TSV records both the uncompressed exact alignment and this canonical DSL
rendering, so every macro is mechanically auditable.  Missing source readings
are retained as `MISSING_SOURCE_READING`; they are never silently imputed.

## Operator templates and residuals

An operator template is a sparse vector over `(opcode, relative zone,
argument-class)` atoms plus a human-readable medoid DSL program.  The zones are
`PREFIX`, `CORE`, `SUFFIX`, and `BOUNDARY`; they derive mechanically from source
and target ordinals.  Argument classes are either the explicit literal token,
`ANY_LITERAL`, or `NONE`.  Training-fold MDL pays for each explicit literal and
each nonzero atom.  Applying an operator to an edge leaves a nonnegative sparse
residual vector; its exact CPU description length is the weighted L1 code of
that residual.

The GPU may propose codebooks and assignments.  It cannot change the DSL,
canonical edge programs, atom vocabulary, description lengths, or final CPU
objective.

## Algebraic composition

Programs act on token streams.  Composition is evaluated by applying the two
programs in order to the registered source when both applications are defined,
then comparing the produced stream with the direct-edge target by the same
exact CPU dynamic program.  A failure to apply is assigned the maximum
registered residual for that representation; it is not discarded.  Cycle
closure applies the programs around the complete registered cycle.  Rectangle
commutation is evaluated only for a rectangle present in the text-blind
inventory; RTA001 does not manufacture one from proximity.

## Interpretation ceiling

The DSL names formal edits only.  It does not encode a word, sound, part of
speech, language, cipher value, object, quality, direction, season, element,
plaintext, or translation.
