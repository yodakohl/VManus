# GDT001 current exploratory summary

Runs retained: **4,185**; converged: **4,181**.

## Current leaders

| rank | run | class | system | bits/source symbol | total bits |
|---:|---|---|---|---:|---:|
| 1 | `contextmixer_s0_015625` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.960465 | 575,289.5 |
| 2 | `contextmixer_s0_00390625` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.960914 | 575,376.6 |
| 3 | `contextmixer_s0_0009765625` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.963956 | 575,967.9 |
| 4 | `contextmixer_s0_000244140625` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.967108 | 576,580.3 |
| 5 | `contextmixer_s0_0625` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.968075 | 576,768.1 |
| 6 | `variablecontext_o2` | NONSEMANTIC_GENERATOR | VARIABLE_HISTORY_OR_METADATA_SOURCE | 2.989391 | 580,910.4 |
| 7 | `contextaxis_o2` | NONSEMANTIC_GENERATOR | SPARSE_CONTEXT_AXIS_SOURCE | 2.990100 | 581,048.2 |
| 8 | `contextmixer_s0_0` | NONSEMANTIC_GENERATOR | ONLINE_CONTEXT_EXPERT_MIXTURE | 2.990822 | 581,188.5 |
| 9 | `sparsemeta_currier_o2` | NONSEMANTIC_GENERATOR | SPARSE_CURRIER_SOURCE | 2.997480 | 582,482.3 |
| 10 | `lineinitial_old_italian_tuscan_o2_s64101` | HYBRID | LITERAL_PROSE_LINE_INITIAL_OLD_ITALIAN_TUSCAN | 2.998316 | 582,644.8 |
| 11 | `lineinitial_medieval_czech_o2_s64102` | HYBRID | LITERAL_PROSE_LINE_INITIAL_MEDIEVAL_CZECH | 2.998598 | 582,699.5 |
| 12 | `lineinitial_latin_o2_s64103` | HYBRID | LITERAL_PROSE_LINE_INITIAL_LATIN | 2.999552 | 582,884.9 |
| 13 | `lineinitial_old_hungarian_o2_s64103` | HYBRID | LITERAL_PROSE_LINE_INITIAL_OLD_HUNGARIAN | 2.999567 | 582,887.8 |
| 14 | `lineinitial_latin_o2_s64101` | HYBRID | LITERAL_PROSE_LINE_INITIAL_LATIN | 2.999653 | 582,904.5 |
| 15 | `lineinitial_middle_french_o2_s64102` | HYBRID | LITERAL_PROSE_LINE_INITIAL_MIDDLE_FRENCH | 2.999952 | 582,962.7 |
| 16 | `lineinitial_latin_o2_s64102` | HYBRID | LITERAL_PROSE_LINE_INITIAL_LATIN | 3.000120 | 582,995.4 |
| 17 | `lineinitial_middle_french_o2_s64103` | HYBRID | LITERAL_PROSE_LINE_INITIAL_MIDDLE_FRENCH | 3.000298 | 583,029.9 |
| 18 | `lineinitial_middle_french_o2_s64101` | HYBRID | LITERAL_PROSE_LINE_INITIAL_MIDDLE_FRENCH | 3.000327 | 583,035.5 |
| 19 | `lineinitial_middle_high_german_o2_s64101` | HYBRID | LITERAL_PROSE_LINE_INITIAL_MIDDLE_HIGH_GERMAN | 3.001364 | 583,237.1 |
| 20 | `sparsemeta_hand_o2` | NONSEMANTIC_GENERATOR | SPARSE_HAND_SOURCE | 3.001409 | 583,245.7 |

## Result

The current winner is an explicit canonical-locus-order prequential nonsemantic context mixer. For each second-order history it combines seven pre-event KT experts: shared local history, one longer-history expert, and Currier, section, hand, layout-kind, and grammar-scope experts. Bayesian weights update only after observing each symbol and use a paid fixed-share rate of 1/64. This serialization is the frozen corpus-lattice order, not asserted manuscript writing chronology. Including the rare-sign channel, a one-bit family selector, and every common observation cost, it scores **2.960465 bits/source symbol** (575,289.5 total bits), 5,620.9 bits better than the previous variable-context source model.

This is a stronger null, not a decipherment. Independent CPU code reproduced every share-grid score exactly. A global source-symbol permutation preserves the gain, while the Timm copy/modify synthetic manuscript gains 20,499.3 bits—far more than the real manuscript. The mixer is therefore a generally better adaptive source code, not manuscript-specific evidence for language, cipher, or meaning.

The strongest language-side effect maps the 512 most frequent complete groups to 27 latent characters under a fourth-order medieval-Czech corpus model. After allowing both language and null families to select their paid scale, it gains **5,881.0 bits** over the best group-code null and only **576.1 bits** over an optimized anonymous 27-state bottleneck. But the three K=512 restart partitions disagree severely (pairwise adjusted Rand 0.136–0.182), and the best total remains 67,402 bits above the new global source winner. This is a real-specific group-compression effect, not a stable Czech decoder.

The final cheap orthogonal source family assigned an explicit K=2–4 hidden state to every modeled within-line event, paid the complete first-order state-path code, and emitted symbols from state-by-observed-history tables. Its best run scores **3.397039 bits/source symbol**, 84,836.8 bits behind the mixer, and all three restart paths disagree at every K. It is stopped, with all nine paths retained. The remaining distinct semantic mechanism—homophonic letters with source boundaries erased and plaintext spaces inserted by exact historical-LM Viterbi—also loses decisively: after a 12-configuration screen and three retained restarts, its best score is **4.898428 bits/source symbol**, 376,592.7 bits behind the mixer.

A bounded omitted-vowel diagnostic let an order-2 historical LM insert unbounded `a/e/i/o/u` vowels and spaces around a deterministic inherited 21-consonant projection. Medieval Czech was best at **1,230,922.91 bits**, still **655,633.45 bits worse** than the mixer. No wider key search was performed, and this projected-key result makes no inference about unsearched consonantal keys.

The literal first modeled sign of each of 4,035 confirmed-prose physical lines was also scored in numeric top-to-bottom page order as a possible historical-language/acrostic channel. Old Italian/Tuscan was the least costly retained map, but it lost **5,813.56 bits** to the matched anonymous line-initial code and **7,354.31 bits** to the selector-adjusted global source leader (**7,355.31 bits** versus the raw leader); the three supported-sign maps agreed on only 0.0–6.7% of coordinates. This bounded line-initial channel is stopped.

Direct character, positional, context-conditioned, Currier-specific, boundary-rule, periodic, fixed-block, learned-multigraph, whole-group character/expansion, whole-word nomenclator, null-symbol, latent-plaintext-space, consonantal-skeleton, literal prose line-initial, STA-family/member, morphology, slot, differential-record, carrier/payload, scaffold-core language, and reading-order systems were tested. A new construction-root character model also crossed its own weak matched null but lost badly to the whole-group code and global source baseline. No mapping is retained as a reading.

No candidate met the freeze requirements. **No translation has been obtained.** No confirmation branch is recommended.

All results are exploratory and branch-local.

A frozen-state switching-key screen then conditioned one or two Middle High German homophonic keys on the already-published `latentline_k2_s28104` line partition. Two keys improved on one by **9,287.69 bits**, but the best remained **484,254.21 bits worse** than the matched frozen-state anonymous source model and **499,729.02 bits worse** than the selector-adjusted global leader; the retained two-key mappings were unstable. This closes only the fixed two-state/order-2 screen; the anonymous states acquire no language or meaning.
