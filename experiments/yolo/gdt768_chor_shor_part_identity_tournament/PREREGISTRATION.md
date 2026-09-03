# GDT768 preregistration

## Objective

Compare five fixed complete-word explanations for `chor` and `shor`, then
decide whether either concrete dictionary default may be replaced. The
experiment must also output a complete, concrete working reading for twelve
already admitted lines, including a default for every token.

## Admitted scope

- Use the current guarded cache only.
- Open no new page, image, or transcription.
- Keep `f84` and `f84r` forbidden.
- Target exactly `chor`, `shor`, `cthy`, `dair`, `kooiin`, and `koaiin` as
  complete reader-exact forms.
- Remove every one of the 172 GDT754 source-composed surfaces before context
  classification.
- Treat edit distance as a donor-contamination control only.
- Assign no letter, sound, Latin initial, stem, or productive component value
  to an EVA substring.

The fixed source decks are `src/ANCHOR_6_DEFAULT_SPECS.tsv`,
`src/MODEL_5_SPECS.tsv`, `src/COMPARISON_FEATURE_SPECS.tsv`,
`src/HISTORICAL_PART_SIGNATURES.tsv`, and
`src/LINE_12_TOKEN_DEFAULT_SPECS.tsv`.

## Fixed models

| ID | relation | concrete direction under test |
|---|---|---|
| M01 | two state forms of one reproductive part | `chor` dry, `shor` moist |
| M02 | two distinct reproductive parts | `chor` flower, `shor` seed/fruit |
| M03 | two distinct reproductive parts | `chor` seed/fruit, `shor` flower |
| M04 | hierarchical general-to-specific pair | `chor` general herb, `shor` reproductive part |
| M05 | two opaque learned record wholes | identities remain different and open |

No sixth fallback model may be introduced after seeing scores. M05 receives no
benefit merely because identity is unknown.

## Fixed observations

For every target occurrence, compute target-excluding environments at D1, R3,
and full-line scope under ED0, ED1, and ED2 complete-form donor ablation. Retain
the following channels:

1. direct and line DRY/MOIST polarity;
2. exact named state-whole contacts;
3. exact pair rates with the other five anchors;
4. line, paragraph, and section geometry;
5. target-excluding 12-dimensional cofield similarity;
6. a broad VALUE/AMOUNT proxy;
7. declared cached visual and historical architecture priors.

The VALUE/AMOUNT channel is named `BROAD_VALUE_AMOUNT_PROXY`. It is not a
bound amount formula and gives no organ-identity credit.

## CF04 rule

The exact complete-form comparison deck is fixed as:

```text
dry-side:   chol, qokchol, cheor
moist-side: shol, sheol, sheor
```

M01 receives the weaker of the two ED2/ED0 expected-family retention ratios:

```text
min(chor dry-side retention, shor moist-side retention)
```

This makes the same-part state claim conjunctive. M02 and M03 instead receive
the ED2 weighted Jaccard of the target-normalised six-form donor profiles. That
metric can recognize common form conditioning but must be identical for both
directions. M04 receives only measured `chor` named-state surface coverage;
matching `shor` breadth remains counterevidence.

## Scoring

Each model's applicable CF01–CF13 weights are fixed in
`src/MODEL_5_SPECS.tsv`. Each feature returns a bounded match `m_i` and both an
evidence and counterevidence statement. The score is:

```text
sum(w_i * m_i) / sum(w_i)
```

All scores must lie in `[0,1]`. Missing evidence scores zero where relevant.
Historical architecture and cached visual priors remain explicit; neither can
identify `chor` or `shor`.

## Minimum support and replacement rules

- **M01:** opposite direct polarity must survive at least two radii, the
  `shor` moist-persistence match must be at least 0.6, and one independent
  channel must agree. Otherwise the dry/moist model remains only a live rival.
- **M02/M03:** a direction requires at least two independent target-specific
  contrasts over the reverse, at least one nonhistorical, plus a score lead of
  at least 0.10. If the scores tie, both directional minimum-support flags are
  false; only their shared two-part relation is supported.
- **M04:** `chor` must show exposure-controlled breadth on both part and
  register axes and lead the part models by at least 0.10.
- **M05:** at least two independent divergence channels are required,
  including stable role divergence and low target-excluding cofield
  similarity. Ignorance is not divergence.

If M02 and M03 differ by less than 0.10, publish the direction as unresolved
and keep both concrete readings visible. No tied model may silently replace
the dictionary.

## Concrete-reader rule

Every one of the 94 tokens in the twelve fixed lines must receive a concrete
default. Each row must preserve:

- exact EVA surface and complete written line;
- portable role;
- concrete German default;
- confidence, positive evidence, counterevidence, and strongest rival;
- `confirmed_plaintext=0`, `confirmed_lexeme=0`, and
  `component_export_credit=0`.

The reader may use `chor=Blütenstand` and `shor=Fruchtstand` as its displayed
C0 direction. This display is replaceable and does not break an M02/M03 tie.

## Historical expectation

Circa-1400 comparison material may support two architectures: parallel
plant-part rubrics and learned materia names combined with part, quality,
state, degree, amount, or recipe fields. Attested Latin words document those
register slots only. Similar initials or spellings between Latin and EVA are
inadmissible evidence.

## Output and claim ceiling

Publish the occurrence, pair, ablation, role, metric, feature-evidence,
scoreboard, six-word dictionary, and twelve-line reader artifacts. The result
may rank complete-word models and retain a shared nominal-part relation. It may
not confirm a lexeme, plaintext clause, plant, substance, language, cipher,
phonetic value, glyph value, or component meaning.
