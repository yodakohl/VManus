# GDT520 method

## Question

Can the remaining GDT519 over-splits be reduced by learning where the old
surfaces normally expose a renderer boundary, while retaining the same finite
candidate compiler, atom anchors and short whole renderers?

## Inputs

- GDT407's 4,576 old running events / 1,558 invariant surface types;
- GDT516's 159 new-to-old-base surface families and their already selected
  contextual recipes;
- GDT519's finite candidates, visible atom anchors and two-/three-atom
  renderers.

No additional page is admitted. `f84` and `f84r` remain forbidden.

## Boundary construction

For each old invariant surface, GDT519's minimum-cost monotone alignment is
replayed against its known working recipe. Every internal character position
is then recorded as either:

- **open**: a renderer segment ends and another begins at that position; or
- **closed**: the position lies inside one renderer segment.

The full old deck supplies 7,433 positions, 199 visible character-pair cells
and 2,037 four-character-window cells. A new position first receives a
smoothed pair probability and then a window refinement:

```text
p_pair   = (open_pair + 8 * p_all) / (pair_contacts + 8)
p_window = (open_window + 4 * p_pair) / (window_contacts + 4)
```

Probabilities are bounded to `[0.02, 0.98]`. The boundary cost of a candidate
is the summed negative log probability of its complete open/closed pattern.

## Composition economy

GDT519 charges visible edit and renderer-alias costs but does not care whether
the same surface is expressed by three licensed renderer segments or five
atomic pieces. GDT520 adds `0.10` per selected renderer segment. This is a
small preference for an already learned whole renderer, not a ban on atomic
composition.

The selected unknown-form score is:

```text
GDT519 score + 0.10 * renderer segment count + 0.10 * boundary NLL
```

Exact event cards and unambiguous known surface/role cards retain precedence.

## Rehearsal and model ladder

The same SHA-256 four-way surface rotation as GDT519 is used. In every fold,
the compiler, anchors, renderer deck and boundary counts are rebuilt from the
other three groups. Eight segment/boundary weight combinations are emitted for
both that old-form rehearsal and the 159 current forms.

The selected light weights trade two old top-five placements for seven old
rank-one gains, lower old rank sum, and a one-card net current rank-one gain.
They are retained as a useful working default rather than intensified to force
the remaining ambiguities.

## Claim ceiling

The open/closed cells are visible renderer licenses. They are not spaces,
morpheme boundaries, phonetic boundaries or word boundaries. Structural atoms
and their German workshop values remain exploratory working tags; no confirmed
lexeme or plaintext follows.
