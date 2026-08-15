# GDT038 — local-context transfer of DAIIN, DAM, OKAM, and ODAIN

## Outcome

**DAM_FIELD_ROLE_PROVISIONAL_LOW_CAPACITY; DAIIN_STATE_ONLY; OKAM/ODAIN_SECTION_CONDITIONED**

Every one of the 65 Herbal-B or Currier-B Stars/Recipe occurrences is aligned as preceding field and immediate state → observed wrapper+core → immediate state and following field. Fields are segmented only by the frozen GDT016 `DY_RESOLUTION` state.

| Core | HB/S occurrences | HB/S folios | target-state overlap | local-context median overlap | Worst LOFO state overlap | Decision |
|---|---:|---:|---:|---:|---:|---|
| `daiin` | 6/17 | 4/5 | 1.000 | 0.253 | 1.000 | STATE_PRESERVED_CONTEXT_VARIABLE |
| `dam` | 4/4 | 3/2 | 1.000 | 0.467 | 1.000 | ABSTRACT_ROLE_PRESERVED_LOW_CAPACITY |
| `okam` | 6/10 | 6/8 | 0.304 | 0.334 | 0.176 | CONDITIONALLY_COMPATIBLE_SECTION_SHIFT |
| `odain` | 3/15 | 2/7 | 0.364 | 0.229 | 0.154 | CONDITIONALLY_COMPATIBLE_SECTION_SHIFT |


## Core findings

### DAIIN

All 23 DAIIN occurrences—6 Herbal-B and 17 S, spread across 4 and 5 folios—are `CARRIER_STATE`, despite renderer variation (`ch/che/sh` in Herbal-B and `ch/che` in S). This identity survives every folio deletion. It is **not**, however, independent role evidence: `CARRIER_STATE` is induced from that same renderer family. Independent context is variable: field-position overlap is 0.619, but previous-state overlap is 0.214, next-state overlap is 0.172, and exact micro-context and masked-field-template overlap are both zero. DAIIN is therefore a stable wrapped host/state association, not yet a stable full field role.

### DAM

All eight DAM occurrences are `CARRIER_STATE`: four `ch|dam` in Herbal-B and three `ch|dam` plus one `che|dam` in S. More importantly, every occurrence is in the final open field of its line; five are at the open-field end and three are internal. The target-state overlap is 1.000, field-position and combined field-role overlap are each 0.600, and next-field shape is identically `EOL`. Exact neighbours remain variable, and only 3 Herbal-B versus 2 S physical folios support the pattern. DAM is the best provisional abstract field-role lead, explicitly low-capacity and renderer-dependent.

### OKAM

OKAM does not preserve one state distribution. Herbal-B is dominated by `OTHER` (5/6, plus one `Q_OUTER_STATE`), while S distributes the host across `Q_OUTER_STATE` (5), `OTHER` (3), `CARRIER_STATE` (1), and `DY_RESOLUTION` (1). It remains a reusable host, but its renderer/state role is section-conditioned rather than invariant.

### ODAIN

ODAIN is also section-conditioned. Herbal-B supplies two `OTHER` and one `Q_OUTER_STATE`; S adds seven `CARRIER_STATE` alongside four `OTHER` and four `Q_OUTER_STATE`. The overlap in local/Q roles is real, but the S-only carrier realization prevents a single preserved abstract-role claim.

## Template clusters and tests

`gdt038_context_clusters.tsv` retains every singleton and recurrent template. Cross-section clusters require occurrences on at least one physical folio in each section; no repeated token on one page is treated as transfer. `gdt038_role_comparison.tsv` reports distribution overlap, JS divergence, exact folio-label permutations, per-core maxT over all eleven context views, worst leave-one-folio-out behavior, and hand-3-only sensitivity.

The strongest invariants are renderer-derived target state for DAIIN/DAM and final-open-field placement for DAM. Exact previous/next field templates are much sparser and often section-specific. This is compatible with a core selecting a broad constructional role while neighbouring material supplies record-specific content, but it is equally compatible with a constrained formal generator. No semantic choice between those accounts is made. The exact folio permutations provide diagnostics rather than confirmation: no positive preservation claim is inferred from a small p-value.

No concrete function, word, morpheme, POS, referent, sound, language, plaintext, meaning, or translation is assigned. f84r was not opened, retained, queried, joined, or scored.
