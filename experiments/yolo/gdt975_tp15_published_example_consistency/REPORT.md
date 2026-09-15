# GDT975: seven published passage pairings conflict with the cited rules

**Decision: PUBLISHED_EXAMPLES_INCONSISTENT.** All eight explicit token/output pairings in AppendixF of Matthew Ruckman's *The Voice But Not the Song* were checked against the documented TP15/CVC fragment using the original decoding functions. Seven conflict; one reproduces. All three separate Section7.5 technical examples reproduce exactly. This is an external-source consistency finding, **not a new Voynich translation**.

Source: [paper v2](https://mattruckman.com/papers/voice-but-not-the-song/voice-but-not-the-song.pdf), [pinned code](https://github.com/mruckman1/voynich_2/tree/2f1e4567511135028c1b1233b454aa84d265b702). Registration was published in commit8b6b8d1e2 before execution on15September2026; the examples and likely inconsistency had already been inspected. The audit is explicitly exploratory, not blind prediction. The machine check ran after public push confirmation at15:10:46UTC.

| Published location | EVA input | Printed output | Consequence of documented fragment | Decision |
|---|---|---|---|---|
| AppendixF, f54r,1 | okaiin | ne | ra + unknown k + n | Contradiction: immutable ra prefix |
| AppendixF, f54r,2 | shey | set | se | Contradiction |
| AppendixF, f54r,3 | qokeey | bes | bera | Contradiction |
| AppendixF, f54r,4 | okey | cos | ra + unknown k | Contradiction: immutable ra prefix |
| AppendixF, f57v,1 | chedy | cor | cora | Contradiction |
| AppendixF, f57v,2 | daiin | din | din | Exact reproduction only |
| AppendixF, f57v,3 | sheey | ser | sera | Contradiction |
| AppendixF, f57v,4 | okaiin | ne | ra + unknown k + n | Contradiction: immutable ra prefix |

The repeated okaiin is retained. Eight printed occurrences are seven distinct token types, not eight independent observations. Manuscript/page attribution is the author's and was not independently checked. The TSV contains every row and each syllable/coda contribution; JSON also preserves character roles and reproduction cases.

Section7.5 reproduction cases: chedy→cora, daiin→din and qokeedy→berara all match. These checks show that the selected fragment agrees with the paper's explicit technical trace. They provide no independent support for heart, daily, a plant, Latin, Italian or any other meaning. In particular, reproducing din does not establish a gloss.

## Why the missing table does not erase these contradictions

The repository intentionally omits generated results. Its complete `combined_refine.json` assignment and `modifier_integrate.json` classifications were not obtained or regenerated. Consequently this experiment does **not** pretend to possess or test the complete TP15 table. No values were fitted, and k remains unknown.

Five relevant syllables are documented or derived explicitly from the source. The sh→se value follows from its published CV shedy→sera together with e→ra and dy's listed modifier role; it is not independently established phonetics. The15 documented modifiers, static feature dictionary and exact append-only functions suffice for these short cases. e has a loop last stroke, so either allowable SYLLABIC/AMBIGUOUS classification gives the same output; the executed sensitivity check confirms that. No choice for unknown k can change an already appended ra into ne or cos. Even allowing an arbitrary-length string for k leaves that incompatibility intact.

The resulting claim is conditional and precise: **the AppendixF outputs cannot all be outputs of the cited documented fragment**. A missing runtime artifact is separately a reproducibility limit, not itself a failed scientific prediction. The paper may contain stale or inconsistent examples; that possibility does not make those examples usable as evidence. No author's intention is inferred, and no revised mapping is silently substituted.

## Scope, validation and next decision

The paper prints four aligned pairs and an ellipsis for each passage, although it describes longer passages. This audit tested every explicit pairing; it did **not** decode two complete paragraphs. No local manuscript corpus, upstream transcription corpus, image or reserve was read. f84/f84r remain sealed; f116v remains unadmitted. Prior project and public-example exposure remains disclosed. Independent confirmation capacity here is zero; alternate transcriptions would not create independence.

The separate validator reconstructs the selected constituents and immutable-prefix test without importing the primary runner or upstream decoder. It passes all eight checks, including all rows, all three reproduction cases, source excerpt hashes and exact TSV cells. Validation concerns implementation/source consistency, not meaning. No search-wide null or significance claim is made.

**Withhold the planned complete-context semantic follow-up for this published version.** Reopen with a complete fixed versioned table, classifications and internally consistent worked examples, keeping GDT975 intact. Do not start an optimization run to recreate a convenient table. This does not close tachygraphy, syllabic writing, Latin/Italian generally, or every later TP15 variant. The GDT604/609/911 and GDT972–974 decisions are unchanged. Confirmed translated words remain0.
