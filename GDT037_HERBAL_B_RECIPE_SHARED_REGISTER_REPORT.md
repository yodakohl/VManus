# GDT037 — Herbal-B / Stars-Recipe shared formal register

## Outcome

**B_S_SHARED_REGISTER_CANDIDATES_ISOLATED_CURRIER_HAND_CONFOUNDED**

This pass does not re-test whether Herbal-B and Stars/Recipe are globally similar. It isolates exact features that recur in both targets, subtracts Herbal-A prevalence, and then asks whether they are also more specific than **other Currier-B sections**. The primary inventories contain 1,323 Herbal-B groups on 16 folios, 4,855 Currier-B S groups on 13 folios, 3,911 Herbal-A groups on 47 folios, and 4,519 other Currier-B groups.

The scan retains **346** cross-folio recurring formal features; **24** meet the stricter exploratory B↔S-register classification after requiring positive leave-one-target-folio enrichment over both Herbal-A and other Currier-B. These are candidate register markers, not meanings.

## Highest-ranked overall patterns

| Rank | Family | Pattern | HB/S/A/other-B counts | min log2 enrichment vs A | min log2 specificity vs other-B | target folios | hand-3 overlap | Classification |
|---:|---|---|---|---:|---:|---:|---|---|
| 1 | WRAPPER_CORE | `NONE|ain` | 4/16/0/5 | 4.733 | 1.482 | 4 | NO | B_S_ENRICHED_HAND_CONFOUNDED |
| 2 | WRAPPER_CORE | `ch|daiin` | 4/7/0/0 | 3.595 | 3.803 | 2 | YES | B_S_REGISTER_CANDIDATE |
| 3 | WRAPPER_CORE | `NONE|ar` | 22/59/7/20 | 2.676 | 1.434 | 11 | YES | B_S_REGISTER_CANDIDATE |
| 4 | WRAPPER_TRANSITION | `che>che` | 12/42/3/20 | 3.176 | 0.928 | 9 | YES | B_S_REGISTER_CANDIDATE |
| 5 | RECORD_STATE | `ED_MEDIUM` | 16/123/2/46 | 4.285 | 0.277 | 11 | YES | A_RARE_BS_SHARED_WEAK_SPECIFICITY |
| 6 | CORE | `daiin` | 6/17/1/4 | 3.232 | 1.856 | 4 | YES | B_S_REGISTER_CANDIDATE |
| 7 | STATE_TRANSITION | `ED_MEDIUM>CARRIER_STATE` | 4/25/0/5 | 4.628 | 1.471 | 3 | YES | B_S_REGISTER_CANDIDATE |
| 8 | WRAPPER_CORE | `che|dy` | 25/99/0/130 | 7.235 | -0.584 | 12 | YES | GENERIC_CURRIER_B_NOT_BS_SPECIFIC |
| 9 | CORE | `opch` | 3/9/0/3 | 3.936 | 1.337 | 3 | YES | B_S_REGISTER_CANDIDATE |
| 10 | CLOSED_FIELD_CLOSER | `opch` | 3/9/0/3 | 3.503 | 1.612 | 3 | YES | B_S_REGISTER_CANDIDATE |
| 11 | WRAPPER_CORE | `NONE|olaiin` | 5/9/0/4 | 3.936 | 0.975 | 5 | YES | B_S_REGISTER_CANDIDATE |
| 12 | FIELD_SHAPE | `CLOSED|LEN_3|AR_REFERENCE>DY_RESOLUTION` | 7/14/2/2 | 1.791 | 2.707 | 6 | NO | B_S_ENRICHED_HAND_CONFOUNDED |
| 13 | CORE | `dy` | 65/127/3/158 | 4.875 | -0.417 | 12 | YES | GENERIC_CURRIER_B_NOT_BS_SPECIFIC |
| 14 | STATE_TRANSITION | `DY_RESOLUTION>AR_REFERENCE` | 25/51/2/52 | 3.938 | -0.152 | 10 | YES | GENERIC_CURRIER_B_NOT_BS_SPECIFIC |
| 15 | FIELD_SHAPE | `OPEN|LEN_1|ED_MEDIUM>ED_MEDIUM` | 3/11/0/6 | 3.779 | 0.994 | 3 | NO | B_S_ENRICHED_HAND_CONFOUNDED |
| 16 | FIELD_TEMPLATE | `ED_MEDIUM>OPEN` | 3/11/0/6 | 3.779 | 0.994 | 3 | NO | B_S_ENRICHED_HAND_CONFOUNDED |
| 17 | CORE | `otch` | 7/10/0/6 | 4.080 | 0.588 | 6 | YES | B_S_REGISTER_CANDIDATE |
| 18 | CLOSED_FIELD_CLOSER | `otch` | 7/10/0/6 | 3.647 | 0.863 | 6 | YES | B_S_REGISTER_CANDIDATE |
| 19 | CORE | `okair` | 3/7/0/2 | 3.595 | 1.482 | 3 | NO | B_S_ENRICHED_HAND_CONFOUNDED |
| 20 | STATE_TRANSITION | `AR_REFERENCE>DY_RESOLUTION` | 15/54/3/45 | 3.535 | 0.137 | 7 | YES | A_RARE_BS_SHARED_WEAK_SPECIFICITY |

## Strongest B↔S-specific candidates

| Rank | Family | Pattern | HB/S/A/other-B | LOFO min vs A / other-B | Formal reading |
|---:|---|---|---|---:|---|
| 2 | WRAPPER_CORE | `ch|daiin` | 4/7/0/0 | 2.137 / 2.346 | FORMAL_PATTERN |
| 3 | WRAPPER_CORE | `NONE|ar` | 22/59/7/20 | 2.537 / 1.295 | FORMAL_PATTERN |
| 4 | WRAPPER_TRANSITION | `che>che` | 12/42/3/20 | 2.988 / 0.740 | FORMAL_PATTERN |
| 6 | CORE | `daiin` | 6/17/1/4 | 2.478 / 1.102 | PREDOMINANT_CARRIER_STATE |
| 7 | STATE_TRANSITION | `ED_MEDIUM>CARRIER_STATE` | 4/25/0/5 | 3.874 / 0.717 | FORMAL_PATTERN |
| 9 | CORE | `opch` | 3/9/0/3 | 3.542 / 0.943 | PREDOMINANT_CLOSURE_HOST |
| 10 | CLOSED_FIELD_CLOSER | `opch` | 3/9/0/3 | 3.132 / 1.240 | FORMAL_PATTERN |
| 11 | WRAPPER_CORE | `NONE|olaiin` | 5/9/0/4 | 3.515 / 0.554 | FORMAL_PATTERN |
| 17 | CORE | `otch` | 7/10/0/6 | 3.710 / 0.218 | PREDOMINANT_CLOSURE_HOST |
| 18 | CLOSED_FIELD_CLOSER | `otch` | 7/10/0/6 | 3.311 / 0.527 | FORMAL_PATTERN |
| 24 | WRAPPER_CORE | `NONE|aiin` | 22/102/15/42 | 1.901 / 0.654 | FORMAL_PATTERN |
| 32 | STATE_TRANSITION | `AR_REFERENCE>OTHER` | 38/92/25/35 | 1.355 / 1.180 | FORMAL_PATTERN |
| 33 | STATE_TRANSITION | `OTHER>DY_RESOLUTION` | 44/153/37/91 | 1.495 / 0.510 | FORMAL_PATTERN |
| 41 | WRAPPER_TRANSITION | `NONE>che` | 52/217/56/109 | 1.205 / 0.553 | FORMAL_PATTERN |
| 42 | WRAPPER_CORE | `ch|dam` | 4/3/0/0 | 1.401 / 1.609 | FORMAL_PATTERN |
| 52 | CORE | `okam` | 6/10/1/6 | 2.301 / 0.394 | MIXED_NONCLOSURE_HOST_CANDIDATE |
| 65 | WRAPPER_CORE | `NONE|okal` | 10/21/6/10 | 0.994 / 0.510 | FORMAL_PATTERN |
| 66 | WRAPPER_CORE | `NONE|otch` | 3/5/0/3 | 2.610 / 0.012 | FORMAL_PATTERN |
| 68 | CORE | `dam` | 4/4/0/1 | 2.137 / 0.760 | PREDOMINANT_CARRIER_STATE |
| 70 | CORE | `odain` | 3/15/4/2 | 0.223 / 1.280 | MIXED_NONCLOSURE_HOST_CANDIDATE |

## Candidate residual cores, separated by formal behavior

| Core | HB/S/A/other-B | Target wrapper variants | Anonymous-state tendency | Reading |
|---|---:|---|---|---|
| `daiin` | 6/17/1/4 | ch;che;sh | CARRIER_STATE:6 ; CARRIER_STATE:17 | PREDOMINANT_CARRIER_STATE |
| `opch` | 3/9/0/3 | NONE;ch;q | DY_RESOLUTION:3 ; DY_RESOLUTION:9 | PREDOMINANT_CLOSURE_HOST |
| `otch` | 7/10/0/6 | NONE;ch;q;sh | DY_RESOLUTION:7 ; DY_RESOLUTION:10 | PREDOMINANT_CLOSURE_HOST |
| `okam` | 6/10/1/6 | NONE;ch;q | OTHER:5;Q_OUTER_STATE:1 ; Q_OUTER_STATE:5;OTHER:3;CARRIER_STATE:1;DY_RESOLUTION:1 | MIXED_NONCLOSURE_HOST_CANDIDATE |
| `dam` | 4/4/0/1 | ch;che | CARRIER_STATE:4 ; CARRIER_STATE:4 | PREDOMINANT_CARRIER_STATE |
| `odain` | 3/15/4/2 | NONE;ch;che;q;sh | OTHER:2;Q_OUTER_STATE:1 ; CARRIER_STATE:7;OTHER:4;Q_OUTER_STATE:4 | MIXED_NONCLOSURE_HOST_CANDIDATE |


`DAIIN` is the cleanest carrier-associated residual host: it recurs under `ch`, `che`, and `sh`, with 6/17 target occurrences versus 1 Herbal-A and 4 other-B. `OKAM` and `ODAIN` are the clearest mixed nonclosure candidates, but are weaker. `OPCH` and `OTCH` are not content leads: every target occurrence is a DY-resolution closer, making them candidate shared **field-closing templates**. Bare `AR` and bare `AIIN` are constructional selection effects; their underlying cores are much broader than the bare forms.

The earlier CKHY lead is an important counterexample to a simple practical-register vocabulary: CKHY occurs 23 times in Herbal-B and 33 in S, but also 17 in Herbal-A and 52 in other Currier-B; its target-versus-other-B specificity is negative. It is not a B↔S register marker here.

## Interpretation

The leading vocabulary candidates must be read through `gdt037_core_wrapper_atlas.tsv`, which keeps every observed wrapper distribution and anonymous-state distribution separate. A core recurrent under several wrappers is evidence for a stable residual host, not for a lexeme. `MIXED_NONCLOSURE_HOST_CANDIDATE` means only that the core is not normally the DY-resolution closer in this formal parser; it is the appropriate pool for later independent grounding.

The structural atlas separately ranks anonymous states, exact state-field templates, compact field shapes, closer hosts, state transitions, and wrapper transitions. This prevents a frequent closure renderer from being mistaken for content vocabulary. Generic Currier-B patterns are retained as counterexamples rather than promoted as B↔S-specific.

## Hand and Currier limits

The primary target comparison fixes Currier B. Other Currier-B sections are the strongest available control against simply rediscovering the B renderer. Hand 3 occurs in both Herbal-B and S, and every candidate records whether it recurs there. But Herbal-B also uses hands 2 and 5, S is overwhelmingly hand 3, and Herbal-A is hand 1/Currier A. Consequently A-rarity can never be fully separated from Currier/hand with this manuscript. The single Currier-A S folio is reported only as sensitivity.

No candidate receives a semantic function, object, medical operation, ingredient, word, morpheme, POS, sound, language, plaintext, or translation. f84r was not opened, retained, queried, joined, or scored.
