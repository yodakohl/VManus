# GDT809 method

## Exact-head comparison

Use the inherited GDT760 amount-content deck and GDT764 X-daiin heads:
41 surfaces, six exact-Q152 exclusions, 35 active whole heads. Query mixed
transcriptions only through selector-first query-tsv, allowing the inherited
179 selectors and forbidding f84 and f84r before row materialization.
Keep the three transcription readings as alternatives, not independent data.

Join exact, rank-stable whole heads at signed offsets -2,-1,+1,+2 around the
1,777 GDT808 CORE events. Keep occurrence edges, distinct head/pivot links,
and primary windows with exactly one distinct admitted head separately.
L and DY remain separate. Use corrected log odds, 24 deterministic rotations
within axis/carrier/section/language/hand/target-free-length strata, and
leave-one-contact-folio-out direction checks. Rebuild after excluding heads
within edit distance one of Q152. None of this decodes a character.

D01–D07 in RELATION_DECISION_SPECS.tsv execute the unchanged formal thresholds:
four contacts on four folios, absolute log odds at least 1.25, rotation rank
at most 4/25, sign agreement at least .80, and compatible external records.

## External compatibility is not independent meaning evidence

External occurrences exclude the inherited discovery coordinates and radius
two around every CORE pivot. The record model is trained without the head's
contact folios and uses section, language, hand, line position, paragraph-line
position and target-free length. External folios can overlap its training
folios; that overlap is explicitly counted. The output is record/form
compatibility, not a prediction of the word's identity on unseen folios.

## Repaired candidate comparison

Twenty profiles include liquids, plant parts, substances, operations, herba
and an unnamed botanical head. A feature-producer registry identifies what
the current inputs actually measure. Source provenance is emitted per head,
candidate and gate. Inherited PRIOR tags are shown in a separate score and
excluded from the contextual score:
2 × observed required matches + observed optional matches
− 2 × observed hard-negative matches.
This is a descriptive ranking, not a calibrated confidence probability.

Broad botanical context cannot distinguish folium, herba and an unnamed
botanical word; their context profiles are identical. A drawing containing
leaves is not a word-to-leaf owner link. An unavailable candidate-specific
measurement is UNOBSERVED, never evidence that a meaning is impossible.
Exact ties share rank. A one-member family has no rival margin (NA).
D14 explicitly disables automatic literal promotion; all concrete meanings
remain working hypotheses regardless of context score. The 35-head table
and the smaller joint dictionary serve different purposes and are not merged.

## Four complete paragraphs, two joint interpretations

JOINT_PARAGRAPH_SPECS.tsv declares four complete paragraphs on already used
pages; paragraph-start/end flags and alternate readings are independently
checked. JOINT_LEXICON_SPECS.tsv provides 16 exact whole-word entries, with
a descriptive meaning, recipe meaning, common default, uncertainty,
positive evidence and counterevidence. No substring inherits an entry.

Each source token survives in both readings with position and provenance.
Recognized groups are rendered once; unassigned runs remain bracketed EVA.
Repetitions remain repeated. A historical syntactic interpretation may
reorder a recognized group in German but cannot silently add an operation.
The descriptive model reads plant-part / quality / degree combinations.
The recipe model reads ingredient / state / portion combinations.
Neither glosses every word and neither is a complete translation.

Seven JOINT_PROBE_SPECS.tsv probes audit lists, repeated three-token groups,
immediate repeats, recurrence with intervening text, repeated head-value
frames and alternating state candidates. Their scorecard counts observed
forms and the scope each interpretation needs, with zero identity-selection
credit. These motifs have relevant predecessor analyses, explicitly cited.

One local boundary comparison records f32v.8 ctho daiin versus RF1b
cthodaiin only where the surrounding sequence agrees. It illustrates a
possible segmentation alternative, not a new morphological or semantic rule.

## Validation and reproducibility

Run src/run_experiment.py to build both layers. src/validate.py reconstructs
the corpus, joins, model scores, provenance, ties and candidate tables without
importing the builder, then invokes src/validate_joint.py --no-write.
The joint validator independently reconstructs all 17 paragraph lines and
token preservation, dictionaries, probe counts, alternate-reader support,
boundary comparison, GDT388 output and artifact hashes.

Both new relation packets are passed to check-edge-packet. Text-only,
previously inspected relations have no sealed visual evidence credit.
All sources/specifications/scripts are hash-bound in experiment.json.
Registration is outcome-aware; formal validity never validates a translation.
