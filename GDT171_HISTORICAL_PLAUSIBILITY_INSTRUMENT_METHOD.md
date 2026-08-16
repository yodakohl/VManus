# GDT171 — historical-plausibility synthetic instrument calibration

## Purpose

GDT171 is a v2 positive-control calibration.  It does not alter or supersede
GDT168/GDT170.  It asks how the frozen VManus surface parser behaves when two
known architectures are rendered with more historically plausible vocabulary,
layout, register and scribal constraints.

No Voynich frequency, operation, threshold or outcome is used to choose any
encoder parameter.  The sole source is the already frozen early-fifteenth-
century Latin medical graphematic control used by GDT168.

## Lexical inventory and literal escape

The 384 most frequent recurring diplomatic source types, ranked by source
frequency with a hash tie-break, receive opaque **lexical IDs**.  They are not
semantic concepts: no lemmatization or meaning normalization is available.
Every other source form uses an explicit reversible literal escape consisting
of one escape marker followed by a base-19 encoding of its UTF-8 bytes.  Rare
forms therefore remain transmissible without creating 5,791 additional
lexical/codebook entries.

## Source order and manuscript layout

Source order within every physical source unit is unchanged.  Deterministic
source-independent hashes set record lengths from 9 to 27 groups, line lengths
from 4 to 9 groups, and folio record counts from 3 to 7.  Final short fragments
are merged into the preceding record/line.  Compiler fields are optional:
record/line operators, local frames, positional right fields, line closure and
record closure occur only under the frozen physical-position rules.

## Registers and hands

Four registers are source partitions, not copies.  Primary register assignment
is by source manuscript family; a hash-frozen minority of complete source units
also appears in one adjacent register, providing controlled partial overlap.
This creates real register-specific frequency/content distributions.  Each
register-unit witness is written by exactly one of two hands.

Both hands use the same symbol identities.  There is no alphabet permutation.
Hand S2 applies one small deterministic host-spelling variant to 1/17 of the
frequent lexical IDs; all other symbols and compiler marks are shared.

## Frozen worlds

### SYSTEM_A_V2 — bounded lexical-address codebook

Each of the 384 frequent lexical IDs has a fixed injective two- or
three-character host.  Compiler fields depend only on visible record/line
position.  Rare source forms use the literal escape.

### SYSTEM_B_V2 — explicit distributed record table

The same 384 lexical IDs are listed in a published, hand-auditable lookup
table.  Each row specifies a small host bucket plus optional lexical-left,
lexical-right and field-marker values.  The tuple is unique.  There is no
modulo-6,175 cipher, slot rotation, hidden arithmetic decoder, or separately
mapped rare-type inventory.  Rare forms use the same literal escape.

## Observation and oracle layers

The strict observation layer contains only visible surface groups, source
separators, physical folio/line/group order, register/hand metadata, visible
paragraph/layout roles and neutral generated annotations.  The sealed oracle
contains source forms, lexical IDs, literal status, source units, record slots,
codebook/table fields and every true encoder component.

The normal frozen GDT170 parser is then run at three reported levels:

1. `SURFACE_ONLY`;
2. `VMANUS_ANNOTATION_ASSISTED`;
3. `ORACLE_CEILING`, opened only after blind outputs are committed.

The fixed GDT113/160/162--167 analogue diagnostics are rerun.  Recovery is
reported separately on frequent lexical-ID rows, literal-escape rows and the
combined corpus.

## Claim ceiling

This is synthetic instrument calibration only.  It may identify sensitivity
or failure modes of the VManus parser under a historically more plausible
control.  It establishes no Voynich word, code value, language, semantic role,
meaning, plaintext or translation.  No Voynich source or image, including
f84r, is an input.
