# GDT1166 — natural shared-sign candidate control

## Question and decision

Can a finite shared writing channel generate previously unsupplied expansion candidates for unseen abbreviated written forms in a real medieval recipe witness, using only an opaque written training stream and an unpaired other-book reference? The primary problem is candidate generation, not choosing among supplied per-form expansions.

This is a source-only control. It does not identify a Voynich language, authorize a target decoder, or establish a word meaning. GDT1160 retains its supervised context/neural gain;1164 retains its failed opaque whole-word ranking. GDT834 already recovered hidden synthetic roles and3,160 novel composed forms. New here is naturally observed optional abbreviation, with genuinely shared documented sign classes and variable editorial restorations. GDT837/995 mandatory wholeword precedence is not imported. GDT1165 remains invalid; no repair is attempted.

The smallest selected channel is deliberately partial: ordinary symbols have one shared character output; one latent sign class may license missing letters anywhere within its word. Wholeword/multichar signs such as the development example for libra are known unsupported cases, not post-result exceptions. A positive result would justify this bounded source candidate generator, not a complete historical writer. A failure closes this fixed search/channel; no automatic optimizer, source, threshold or language repair follows.

## Sources and exposure

The original CoReMA B4 TEI is the control witness: Berlin Ms.germ.qu.1187, dated1437–1475 by its manuscript description. The other five already-owned original witnesses B6,Br1,Bs1,Gr1,W1 supply readable expanded reference words. Source-byte receipts and licenses are pinned by src/SOURCE.json and the preceding COREMA_NATIVE_ABBREVIATION_SUPPLY dossier. These are richer original representations of a previously used corpus, not newly discovered books. Related recipes and editorial practice mean the reference witnesses are not independent traditions.

The first two complete B4 entries and their20 abbreviations were read while selecting the design. Project-wide sources and old normalized recipe derivatives were already exposed. A publication whitespace check additionally displayed source excerpts before fitting; no settings were changed in response. Computational training/held separation is not analyst blindness or reserved semantic confirmation. No Voynich source, image, reserve, f84/f84r or f116v is an input. No external contact occurs.

PREPARATION.md fixes the exact source projection before execution. Written input drops supplied ex letters, unwraps abbr/am without emitting their boundaries, and preserves ordinary carriers and documented graphical sign identities. Value-bearing IDs such as bar_e/bar_m/bar_n must collapse to the same documented overline before opaque remapping. Raw IDs, normalized sign values, ex positions/lengths, abbreviation flags and expansion pairs never enter the fitter. Inconsistent/undeclared glyphs and unreadable/supplied writing remain explicit UNKNOWN. The original XML and conservation ledger remain separate.

Word boundaries follow a declared transcription-whitespace and w-join convention. They are given editorial boundaries, not learned authorial segmentation. Character case, native distinctions and written hyphen events are not silently normalized away. Readable reference/gold may use declared ordinary-glyph normalization; this does not license applying those values to opaque written input. Final-state/revision, note, heading, transposition and unknown policies are fixed in PREPARATION and the preparer, not chosen after results.

## Physical split, unknowns and capacity

B4 has42physical leaves71–112. Complete records confined to the first21 leaves71–91 form discovery; complete records confined to92–112 form held evaluation. Record131 crosses91/92 and is retained as an unused bridge. This gives130discovery,138held and1bridge records. Every record and source obligation remains conserved. No alternate split is allowed after a capacity or score failure.

The opaque alphabet may include IDs for all B4 graphic classes, disclosing only alphabet size, never their identities. Actual learned support is stricter: fit eligibility excludes written types containing UNKNOWN(-1), then selects the top512 known-input discovery types by count descending, opaque-array lexical ties. No expansion/gold flag filters training. All original130 discovery records/types, not merely these512, define held novelty. Report unused training types and their reasons. At least two fit-supported atoms and a reference alphabet of2–1024 characters are required by the executable search. Unfit atoms in a held word force empty predictions; random initialized values are not treated as learned meanings.

K is the set of known-input held abbreviated written types absent from every discovery record, with at least one known-expansion held abbreviated occurrence. Abbreviated means contained in an original TEI abbr element; unknown-expansion occurrences enter U only, including when other occurrences of the same known written type enter K. For each such type, average exact prediction success across its eligible known-expansion held occurrences. U is the count of held abbreviated occurrences whose written input or expansion remains UNKNOWN. Each is a mandatory zero-credit obligation; an UNKNOWN bucket is not evidence that different occurrences are one word type. U is not described as a count of distinct lexical types. The primary conservative score divides the sum of K's within-type accuracies by K+U. Known-only type accuracy is diagnostic. All OOV and channel-unsupported known cases remain errors in K. Any overlap of known-type and unknown-expansion obligations must be prevented by the explicit scorer partition.

At least20known novel abbreviated types are required to score the registered endpoint. If this capacity fails, report NO_CAPACITY, preserve predictions/accounting, and do not change the split or threshold. No oracle-reference coverage is used to select a more favorable evaluation subset.

## Finite key panel and three fixed arms

SPEC.json supplies the exact algorithm, seeds, arithmetic, objectives and tie rules. A key gives each fit-supported opaque atom one reference Unicode character; many-to-one mapping is allowed. No literal/mark identity, supplied26L/4S/8W capacities, plaintext word candidate list per form or B4 plaintext is provided.

The common search guide is an occurrence-weighted within-word character fourgram score derived only from reference words, with three start pads, one terminal, additive0.1 smoothing and per-word length normalization. Eight fixed20,000-step anneals start from frequency-ranked keys plus the declared seed-dependent perturbations. Four forbid omissions; four may select one omitted opaque class or none. The former protect the literal comparator from relying solely on keys fitted while a glyph had no score contribution. Four fixed snapshots per start yield32states, including duplicates; there is no best-checkpoint or gold selection. This is a heuristic panel, not exhaustive key identification or demonstrated convergence.

Every final arm has access to all32keys. Every fit-supported opaque class plus none is considered for the single latent mark. Search-time omission flags do not supply a final role. LITERAL decodes every actual atom, including any glyph omitted by the search guide. C and V remove all occurrences of their selected mark and retain all other decoded carriers in order. A marked word must retain at least two carriers. Unmarked words use exact literal decoding in all arms.

- LITERAL: the exact decoded word must occur in the reference vocabulary.
- CONSTANT: one global residual string r is emitted per marker occurrence. With k markers, a compatible reference word must have an ordered-carrier alignment whose removed characters equal r repeated k. Total removed characters is0–4.
- VARIABLE: the reference word contains every retained carrier in order, with0–4 additional letters in total at any positions in the same word. No carrier substitution/deletion, arbitrary whole-word replacement or per-form rule is allowed.

The constant domain is empty r plus all valid repeated residuals supplied by discovery/reference alignments, not held truth. Multiple alignments count a reference word once. The d in every score is the number of inserted letters, never an edit distance. This distinction and repeated markers have explicit independent synthetic fixtures.

For each compatible reference word v, weight is its other-book occurrence prior times2^(-d). Fit word mass sums these weights once per word. The final objective is the fixed frequency-weighted sum of log(1e-8+(1-1e-8)*mass) over actual fit types. It is an unnormalized compatibility/search score, not a calibrated probability or model likelihood. Each arm independently selects its best key/mark/residual from the same complete panel. All ties within the fixed tolerance and deterministic lexical choice are saved. Broader candidate compatibility may improve training score without improving the held result; the latter is the actual decision.

Predictions are the five highest-weight compatible reference words, with exact Unicode lexical tie order. Cutoff ties are documented without expanding Top5. No free frequency guesses fill an empty or short candidate list. Every held word is predicted, not only marked or favorable examples.

## Locks, scoring and claims

No real-source fit before public preregistration of code, SPEC, METHOD, source contract and bound inputs. FIT_RELEASE identifies that commit and its hashes. Fitting reads only TRAIN_INPUT and REFERENCE_INPUT. KEY_SELECTION_LOCK precedes first HOLDOUT_INPUT access; a separate root PREDICTION_RELEASE binds that key lock. All held predictions and input/key bindings are frozen in PREDICTION_LOCK before the separate gold scorer runs. These are computational access controls, not a claim that the human-readable historical source was secret.

Primary endpoint is conservative exact Top5 score on K+U. Selection requires K>=20, VARIABLE score>=0.50, VARIABLE minus LITERAL>=0.10 and VARIABLE minus CONSTANT>=0.10. All comparisons use the same denominator. Report Top1, known-only macro, occurrence-weighted outcomes, OOV, unsupported/unfit/unknown cases, every per-type candidate/result, and all alternative selected contracts. Never promote a favorable subgroup after the main failure. A source-control success does not itself establish word meanings in the Voynich.

After predictions are locked, source truth may diagnose absence from reference, search-panel miss, or channel incompatibility. Such diagnostics never repair the score or launch another search. No suitable entire-search null is supplied here, hence no significance or translated-word probability claim. Independent validation checks source/prediction conservation, bindings, compatibility, selection and metric arithmetic without importing the runner; any unreplayed optimizer trajectory or other limitation is disclosed.

## Checkpoint and reproducibility

Implementation selection occurred during the active17:47:39–03:47:39UTC ten-hour block. The bounded source experiment has a two-hour total-work checkpoint from final selection, including preparation, validation and publication. It limits expansion, not completion of an already frozen scientific run. The ten-hour block is not declared complete by this shorter checkpoint. Exact commands and release receipts are added to README before public preregistration. No legacy source bytes or decisions are modified.
