# Optimal-transport alignment: local predecessors and semantic-input distinction

2026-10-03, bounded design review while GDT1163 authorship/review completes. No new experiment, target access, model download or fit. Empty exact-term searches are navigation results, not proof that this is new research.

## Local primary evidence read

GDT347 transports one three-edge Voynich formal-coordinate compatibility graph to controls. Its apparent manuscript specificity is conditional on a parser under which all controls have zero inner-D/DY changes. It neither learns cross-language word correspondences nor demonstrates their impossibility. [Primary report](../../../experiments/yolo/gdt347_fixed_graph_control_transport/REPORT.md).

GDT398 clusters opaque joint tuples for structural prediction. Its positive gain over exact identities is dominated by frequency/large classes, loses to the frequency baseline and fails the original gates. It supplies no latent lexicon. A new name for that clustering would not reopen it. It is not an evaluation of bilingual embedding-space transport. [Primary report](../../../experiments/yolo/gdt398_opaque_joint_tuple_predictive_equivalence_preflight/REPORT.md).

GDT1159 actually aligns unknown ingredient forms using finite relational and marginal information across six source collections, with supplied ingredient spans. Its small positive gain fails the fixed selection gates. A different transport objective would need to explain what additional independent information or genuinely different falsifier it supplies. Merely optimizing the same failed finite objective more impressively is not such a change. [Primary report](../../../experiments/yolo/gdt1159_corema_unknown_lexical_graph/REPORT.md).

## A graph-alignment result that does not start from opaque semantics

Tang et al.2023 FGWEA aligns supplied knowledge graphs. Its first stage embeds names and attributes with LaBSE/SimCSE; relation names also support alignment. Section4.3 replaces opaque Wikidata IDs with linguistically informative attributes. Thus “unsupervised” means no supplied matched entity pairs, not absence of semantic information. Table5 reports GW-only Hit1=.011 on DBP15KZH_EN and .004 on SRPRSEN_FR, compared with .763/.915 for semantic embedding matching alone; the combined system improves both. This ablation also changes optimization, so it is not a theorem that topology can never identify correspondences. These are published results, not local replications. [Primary paper, §§3.1,4.3–4.4, Table5](https://aclanthology.org/2023.findings-acl.205.pdf).

Our inference: feeding EVA spellings into that pretrained semantic encoder does not supply corresponding concept names. Feeding guessed translations into it would insert the very assumptions being tested. Independently trained word-context geometry is a different possibility, under separate corpus-size, comparability and stable-unit assumptions; its primary-literature review is in OPTIMAL_TRANSPORT_METHOD_REVIEW.md. No claim that a confirmed seed word is logically necessary follows.

## Decision boundary

No target graph or decoder selected by this note. A proposed successor must specify the observed units, independently informative relational geometry, and a meaning-bearing recovery criterion on an appropriate control. It must retain the source-only/Voynich distinction and the existing complete-search counterexamples. Algorithm names or a global matching objective alone cannot justify prioritizing a particular word meaning.
