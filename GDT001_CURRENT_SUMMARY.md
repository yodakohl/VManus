# GDT001 current exploratory summary

Runs retained: **4,131**; converged: **4,127**.

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
| 10 | `sparsemeta_hand_o2` | NONSEMANTIC_GENERATOR | SPARSE_HAND_SOURCE | 3.001409 | 583,245.7 |
| 11 | `sparsemeta_section_o2` | NONSEMANTIC_GENERATOR | SPARSE_SECTION_SOURCE | 3.012098 | 585,322.9 |
| 12 | `metasource_rare_channel_currier_o2` | NONSEMANTIC_GENERATOR | METADATA_RARE_CHANNEL_CURRIER | 3.025287 | 587,885.9 |
| 13 | `contexttree_rare_channel_d3` | NONSEMANTIC_GENERATOR | VARIABLE_ORDER_TREE_RARE_CHANNEL | 3.035728 | 589,914.8 |
| 14 | `contexttree_rare_channel_d4` | NONSEMANTIC_GENERATOR | VARIABLE_ORDER_TREE_RARE_CHANNEL | 3.036275 | 590,021.0 |
| 15 | `contexttree_rare_channel_d5` | NONSEMANTIC_GENERATOR | VARIABLE_ORDER_TREE_RARE_CHANNEL | 3.036288 | 590,023.7 |
| 16 | `contexttree_rare_channel_d6` | NONSEMANTIC_GENERATOR | VARIABLE_ORDER_TREE_RARE_CHANNEL | 3.036288 | 590,023.7 |
| 17 | `sparsemeta_grammar_scope_o2` | NONSEMANTIC_GENERATOR | SPARSE_GRAMMAR_SCOPE_SOURCE | 3.036415 | 590,048.4 |
| 18 | `sparsemeta_kind_o2` | NONSEMANTIC_GENERATOR | SPARSE_KIND_SOURCE | 3.037710 | 590,299.9 |
| 19 | `metasource_raw_currier_o2` | NONSEMANTIC_GENERATOR | METADATA_RAW_CURRIER | 3.038853 | 590,522.1 |
| 20 | `latentline_k2_s28104` | RECORD_NOTATION | LATENT_LINE_STATES_K2 | 3.040089 | 590,762.3 |

## Result

The current winner is an explicit canonical-locus-order prequential nonsemantic context mixer. For each second-order history it combines seven pre-event KT experts: shared local history, one longer-history expert, and Currier, section, hand, layout-kind, and grammar-scope experts. Bayesian weights update only after observing each symbol and use a paid fixed-share rate of 1/64. This serialization is the frozen corpus-lattice order, not asserted manuscript writing chronology. Including the rare-sign channel, a one-bit family selector, and every common observation cost, it scores **2.960465 bits/source symbol** (575,289.5 total bits), 5,620.9 bits better than the previous variable-context source model.

This is a stronger null, not a decipherment. Independent CPU code reproduced every share-grid score exactly. A global source-symbol permutation preserves the gain, while the Timm copy/modify synthetic manuscript gains 20,499.3 bits—far more than the real manuscript. The mixer is therefore a generally better adaptive source code, not manuscript-specific evidence for language, cipher, or meaning.

The strongest language-side effect maps the 512 most frequent complete groups to 27 latent characters under a fourth-order medieval-Czech corpus model. After allowing both language and null families to select their paid scale, it gains **5,881.0 bits** over the best group-code null and only **576.1 bits** over an optimized anonymous 27-state bottleneck. But the three K=512 restart partitions disagree severely (pairwise adjusted Rand 0.136–0.182), and the best total remains 67,402 bits above the new global source winner. This is a real-specific group-compression effect, not a stable Czech decoder.

Direct character, positional, context-conditioned, Currier-specific, boundary-rule, periodic, fixed-block, learned-multigraph, whole-group character/expansion, whole-word nomenclator, null-symbol, STA-family/member, morphology, slot, differential-record, carrier/payload, scaffold-core language, and reading-order systems were tested. A new construction-root character model also crossed its own weak matched null but lost badly to the whole-group code and global source baseline. No mapping is retained as a reading.

No candidate met the freeze requirements. **No translation has been obtained.** No confirmation branch is recommended.

All results are exploratory and branch-local.
