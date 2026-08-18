# GDT308 — sparse-operation hybrid grammar update

Status: **SPARSE_OPERATION_LEXICALIZED_HYBRID_GRAMMAR**.

This is an abductive, evidence-bound synthesis. It scores no new manuscript row and assigns no meaning.

## Revised executable generator

```text
PAGE / REGISTER
  -> RECORD TEMPLATE + LINE-ENTRY STATE
  -> FIELD OPPORTUNITY / COARSE POSITION
  -> UNKNOWN LATENT PAYLOAD OR FORM ENTRY
  -> JOINT (PAGE_HOST, RENDERER) SURFACE ALTERNANT
  -> OPTIONAL COMPATIBILITY-LICENSED SHARED OPERATION
  -> LOCAL FRAME + RIGHT EDGE + DY/B3 CLOSURE BACKOFF
  -> VISIBLE SOURCE GROUP
```

The revision to GDT298 is narrow but real: rendering is not entirely an exception table. A small shared operation layer exists inside a much larger host-specific alternant lexicon.

## Current shared operations

| operation | formal effect | section/hand direction accuracy | status |
|---|---|---:|---|
| `wrapper:ch>s` | MOVE_MASS_FROM_MIDDLE_TO_PHYSICAL_BOUNDARY | 0.846/0.867 | DOMAIN_STABLE |
| `wrapper:d>s` | SHIFT_MAINLY_TOWARD_PHYSICAL_FIRST | 0.789/0.947 | DOMAIN_STABLE |
| `wrapper:NONE>q` | POST_DY_ENTRY_ECOLOGY_WITH_DOMAIN_MIXED_POSITION_VECTOR | 0.421/0.375 | DOMAIN_MIXED_OR_UNSTABLE |

## Field/line grammar

```text
LINE         := CLOSED_FIELD* OPEN_TAIL?
CLOSED_FIELD := FIELD_PAYLOAD DY
POST_DY      := q-enriched entry ecology (host/register conditioned)
RESET        := physical line start
```

`ch->s` and `d->s` are the first sparse renderer operations to survive unseen-host and held-domain checks. `NONE->q` generalizes as post-DY ecology but not as one invariant domain-wide physical-position vector. This combination explains why the global renderer model fails while a few exact transformations remain reusable.

## Novel predictions

1. New compatible `ch/s` and `d/s` exact-form pairs should preserve the respective boundary/initial delta even when their host was not used to estimate it.
2. A compatibility model that first predicts whether an operation is licensed should beat both a global renderer and a pure exact-form table; applying operations indiscriminately should lose.
3. q enrichment should recur after DY across new forms, but its physical FIRST/MIDDLE/LAST vector should change by register/host ecology.
4. Complete-form identity should retain placement information outside the three supported operation neighborhoods.
5. Any eventual payload decoder must marginalize over joint form alternants plus this sparse operation layer rather than stripping every wrapper uniformly.

## What remains awkward

- The operation family was discovered and selected post hoc before domain stability testing.
- Only three of 29 powered operations transfer; no compact full compiler has emerged.
- The payload carrier remains unidentified and no external referent maps to a form.
- Historical architecture controls do not uniquely distinguish shorthand, language-derived abbreviation, and technical notation.

## Claim ceiling

Formal sparse-operation hybrid grammar only; no word morpheme grammar meaning sound language plaintext or translation. No f84 material was accessed.
