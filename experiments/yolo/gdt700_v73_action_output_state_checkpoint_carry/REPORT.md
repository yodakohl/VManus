# GDT700 — one material survives one state checkpoint

Status: `PASS_V73_10_ANA_WINDOWS__1_EXACT_STATE_ONLY_2_WORKING_STATE_LIKE_2_DEICTIC__1_UNIQUE_CANDIDATE_1_NEW_B_EDGE__C011_OCCURRENCE_BOUND__ZERO_WORD_DELTA`

## Result

The full 175-clause current scope contains exactly ten occurrences of the
shape `ACTION → one-token NOMINAL_BLOCK → ACTION`.  One middle block is
independently evidenced as state-only, two others are merely state-like in the
working gloss, and seven are material-bearing.  Two target actions are deictic
and objectless.  Only `f26r.2#4–6` combines a written material patient in the
source action with the exact state-only checkpoint and a deictic target.  This
uniqueness selects a B-tier hypothesis; it does not verify participant identity.

The resulting practical microrecord is:

> Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von
> „hiervon“ offen]. **[Zustandsvermerk ohne eigenen Materialträger: Mittlere
> Trockenstufe erreicht.]** Die erhitzte Krautdroge bis zur Mittelstufe
> abkühlen und abschließen [C011-Arbeitshypothese].

This is not generic “take material, work it, continue” filler.  The local
proposed participant is specifically the already written *Krautdroge*; the two actions
are specifically the inherited heating and cooling operations; and the
intervening statement is specifically the inherited middle dry-state
checkpoint.

## Exact local graph

| position | inherited working content | V73 relation decision |
|---:|---|---|
| #3 `adeeody` | same measured part of the finished preparation | H002 stays held; no input edge into #4 |
| #4 `ykecthey` | heat Krautdroge to the middle stage and finish | C011 source hypothesis: result of the action with written Krautdroge patient |
| #5 `chedy` | middle dry stage reached | hull-only state checkpoint; not a donor or node |
| #6 `ytedy` | from this, cool to the middle stage and finish | C011 deictic target action |
| #7 `dy` | clause stop | structural only |
| #8 `checthedy` | dry Krautdroge in two moderate drying passes | writes its own object; C011 stops before it |

Thus C011 is exactly:

```text
#4 ykecthey [INFERRED ACTION OUTPUT: die erhitzte Krautdroge]
    └── C011, B_WORKING_LOCAL ──> #6 ytedy [REFERENCE + TARGET_ACTION]

#5 chedy lies inside the 4–6 hull but is not an edge node.
```

No separate output label occurs at #4: “die erhitzte Krautdroge” is exactly
the C011 B-hypothesis.  The opening *hiervon* inside #4 remains unresolved.  GDT700 does not silently
import #3 as its source.  It also does not turn #5 into a drying action and does
not rewrite #8 as “continue drying the cooled Krautdroge”.

## Why the second deictic case does not pass

At `f77v.7`, the broad geometry is similar:

```text
#3 qy       hiervon nehmen
#4 rr       getrocknete Wurzel
#5 ycheedy  hiervon bis zur Endstufe trocknen
```

But #4 is a written material, not a pure state checkpoint.  It competes with a
hypothetical output of #3 for the target reference.  H004/H005 and
R016/R017 therefore remain held; neither *Wurzel* nor “the thing taken” is
selected.

## Scope and ceiling

- 10 complete A--N--A windows: 1 exact-state B nomination and 9 exclusions.
- 11 cumulative relation edges: C001--C010 unchanged, C011 new.
- 479 token glosses, 51 line translations and 3 bound spans unchanged.
- 0 new word meanings, pages or f84/f84r access.
- GDT388 intake remains invalid/not score-ready.

The gain is one concrete local participant link, not a portable grammar
default or historical plaintext proof.  The next useful pass is to compile all
eleven relation edges into exact connected components and practical
microrecords, keeping #5 hull-only and every held rival visible.
