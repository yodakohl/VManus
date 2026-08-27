# GDT520 compact working book

## Current intake stack

1. exact event card;
2. unique known surface/role card;
3. GDT517 finite candidate recipes;
4. GDT518 visible form plus weak neighbouring-card context;
5. GDT519 canonical atom anchors plus learned two-/three-atom renderers;
6. GDT520 segment economy plus visible open/closed boundary licenses.

No new page was used.

## Selected score

```text
GDT519_score + 0.10 * renderer_segments + 0.10 * visible_boundary_NLL
```

Boundary evidence: 1,558 old surface types, 7,433 internal character
positions, 199 character-pair cells and 2,037 four-character windows.

## Current performance

- old four-fold generated targets: GDT519 1,082 rank one / rank sum 2,152;
  GDT520 1,089 / 2,139;
- current 159: GDT519 138 rank one / rank sum 192; GDT520 139 / 190;
- current changes: two corrections, one loss, twenty remaining top-one errors.

## Concrete interpretation

- `chekeey`: prefer `chek~CH+K | ee~EE | y~Y` over atomizing the visible `e`;
- `shckheody`: prefer the terminal whole `dy~DY`;
- `psheody`: the same visible tail needs `d~D_ADDR | y~Y`, so surface boundary
  evidence alone cannot decide the whole `...eody` family.

## Next working move

Learn short recipe-tail licenses around the recurrent ambiguity families:

- `O+DY` versus `O+D_ADDR+Y` (and occasionally `O+Y`);
- `OL` versus `O+L`;
- `AIIN`/`IIN` versus address/local-character expansions;
- visible swallowed or inserted `a`, `d`, `q`, `ch` and local characters.

Use atom bigrams/trigrams and their visible tail, not full-form exceptions.
Retain both alternatives when the old deck genuinely uses both. Exact known
cards always keep precedence.
