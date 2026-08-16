# GDT173 — B2 human-grown distributed notation calibration

Status at registration: **FROZEN_B2_TABLE_RENDERER_AND_LAYOUT_BEFORE_BLIND_SCORE**.

## Purpose

GDT173 adds B2 only.  GDT172 lexical System A is never regenerated or changed,
and GDT172's factorial System B remains a frozen artificial contrast.  B2 asks
what the unchanged VManus instrument recovers from an irregular distributed
technical notation that a historical scribe could operate from a finite lookup
table plus a few simple rendering rules.

This is a synthetic instrument calibration.  It uses no Voynich source,
statistic, result, image, or f84 material.

## Frozen source and layout

B2 reuses, row for row, the GDT172 lexical-ID universe and observation schedule:

- the same 384 frequent lexical IDs and source forms;
- the same real medieval medical source order;
- the same 176 content folios, variable 9--27 group records, 4--9 group lines,
  register partitions, partial register overlap, hands, separators and neutral
  layout annotations; and
- the same literal channel, escape `w` followed by the unchanged source
  graphematic form.

Only the frequent-ID encoding is new.

## B2 lookup architecture

The committed `gdt173_b2_lookup.tsv` is the decoding authority.  It has one
explicit row per lexical ID.  A row records a family, host, optional lexical
left, optional lexical right, optional field mark, optional lexical closure,
and an explicitly listed S2 host spelling.  Exact source recovery is stored in
the sealed oracle and the complete rendered lexical tuple is injective within
each hand.

The table is authored from:

- 32 named host families with unequal sizes from 7 to 18;
- 24 hand-declared local construction variants;
- partial host-family reuse and two locally analogical host extensions;
- empty/optional left, right, field and lexical-closure cells;
- eleven explicit lexicalized exceptions; and
- six explicitly named families with a small S2 final-glyph variant.

The authoring program walks the already frozen lexical-ID order through these
literal family/variant declarations.  It contains no random generator,
hash-based assignment, modulo operation, complete Cartesian enumeration,
optimizer, or Voynich-derived parameter.  The production renderer does not
execute the authoring declarations; it reads the materialized 384-row table.

For a frequent row the visible order is:

```text
record operator + line frame + B2 lexical left + rendered host
+ B2 lexical right + B2 field + B2 lexical closure
+ positional right + physical line/record closure
```

For a rare row it is the unchanged GDT172 literal construction.  The physical
record/line closure remains distinct from B2's optional lexical closure.

System B2 is a **human-grown distributed synthetic control**, not a
reconstruction of a historical notation and not a Voynich model.  GDT172
factorial B remains explicitly artificial.  No B2 parameter may be changed
after this source freeze.

## Blind instrument and comparison

The exact GDT170/GDT172 blind surface parser, annotation-assisted ranking,
operation thresholds/caps, diagnostics, smoothing and null size are inherited
unchanged.  The blind runner sees only anonymous CONTROL_R observations.
The B2 table and oracle are forbidden until blind outputs are committed.

After unblinding, report:

- frequent-ID host/full-tuple information, held accuracy and coverage;
- exact host, left/right, full-span and component-boundary recovery;
- compatibility density and its unchanged null;
- held NEXT_HOST and WHOLE_LINE gains;
- closure, short-host, substitution and register-alignment diagnostics; and
- a side-by-side fingerprint with frozen GDT172 lexical A and factorial B.

## Claim ceiling

The result can calibrate sensitivity to a human-authored irregular distributed
notation only.  It cannot establish Voynich architecture, a word, code value,
language, role, meaning, plaintext or translation.
