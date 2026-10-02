# GDT1143 validation

**Protocol/accounting validation: PASS_PROTOCOL_ACCOUNTING (15/15 checks). Meaning: NOT ASSESSED.** This is not a parser, decoder, semantic test, or visual review.

The independent row reconstruction reconciles 176 accounted occurrences with the registered passage: {'IT2a': 57, 'RF1b': 59, 'ZL3b': 60}. The exact-reader row spellings and separators are checked against the page-bounded GDT1094 input. Status counts are {'CORE_C0': 86, 'UNKNOWN_OR_UNSEGMENTED': 22, 'EXTENSION_C0': 68}. All SOURCE pins and core/author byte receipts are checked. The exact daiin counts and immediate doubles are retained as recorded in VALIDATION.json.

Repeated surface values and paid C0 references are internally consistent. The proposed value of `daiin` consistently denotes the same plant at the lexical-assignment level; this does not establish that all those occurrences refer to one discourse entity. The author calls the construction manual and explicitly leaves the recipient for the eye/hair function and the hare→plant→naming connection underived. Habitat attachments are also not derived. Therefore this is a complete lexical inventory with a partial C0 proposal, not a complete connected reading.

The author selects the CXIII base-text version and explicitly excludes the beta eating variant and its `aestu` omission. The historical source does not establish a Voynich source witness. Confirmed meanings remain zero.
Paragraph evidence is asymmetric: registered IT2a and ZL3b flags each mark a single f25v paragraph start/end, while RF1b has no boundary flags in this projection. The latter is unscored/missing boundary evidence, not proof of no paragraph and not agreement; see {'IT2a': {'paragraph_starts': 1, 'paragraph_ends': 1}, 'ZL3b': {'paragraph_starts': 1, 'paragraph_ends': 1}, 'RF1b': {'paragraph_starts': 0, 'paragraph_ends': 0}}.

The frozen METHOD phrase prohibiting a “named animal/plant” sits in tension with C0 whole-form labels `hare` and `hare-plant/epithet`. The account distinguishes these as provisional lexical guesses, not pictured species, taxon, or identified native owner. This is retained as `REGISTERED_WORDING_AMBIGUITY`, not silently resolved by the validator; METHOD remains unchanged.
The frequent-form profiles support treating the guesses as high transfer-debt assignments. They do not supply semantic counterexamples, so the AUTHOR_READING.md phrase “contradicted by the breadth of their known contexts” is not established by the registered frequency profiles alone and is not treated as a semantic refutation here.

Per-check evidence and detailed counts are in [VALIDATION.json](VALIDATION.json). Reproduce with `python experiments/yolo/gdt1143_mixed_herbal_entry_whole_reading/src/validate.py`.
