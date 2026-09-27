# Preregistration: complete Galen season-concept profile

This source-only pilot instantiates only the countercheck in the linked decision.
It does not execute607's eight-concept/three-work proposal or608's target bridge.

## Fixed endpoints

For every authorial HTML paragraph in the fixed English maintext, annotate
WINTER and SUMMER separately with exactly one local state:
- E: expressed season, directly named or unambiguous seasonal paraphrase;
- A: anaphoric seasonal reference, with identified antecedent in this work;
- U: unresolved seasonal-versus-weather/other reading, or uncertain antecedent;
- N: no local expression of that season after reading the complete paragraph.
Negation, reported speech, hypothetical and quoted seasonal references count:
concept presence is not assertion of an event. Cold, heat, rain, storm, humoral
quality, age or day/night does not automatically denote a season. An explicit
argument about plant winter dormancy does. Merely a generic 'season' does not
select winter or summer. Both concepts may occur in the same paragraph.

Keep a separate topic_scope state for each concept: ACTIVE or NONE or UNCLEAR.
ACTIVE needs an explicit seasonal heading or previously stated temporal topic
that continues governing the paragraph; provide the antecedent and scope reason.
One earlier mention does not automatically govern the rest of a chapter. A local
reference already counted E/A may also be topical. U is never silently N.
Document seasonalmetaphors or winter-of-life cases as U unless literalseason
remains expressly invoked; never add them to an unqualified physicalseason count.

Per row: paragraph_id, chapter_id, paragraph_sha256, reader, complete_read=true,
winter, summer, winter_topic, summer_topic, antecedents, note. For N/N without
topic, note may be a brief content paraphrase, not a quotation. All positives,
anaphora, topic carryover and U require a specific pointer and reason.
No inherited Voynich glosses or guessed source-language keyword classification.

## Complete extraction and result

Use chapter anchors I_1...I_17, II_1...II_9, III_1...III_15 in document order.
All authorial p elements in this whole span are included; remove footnote bodies,
inline footnote reference numbers and editorial page markers. Preserve inline
text and paragraph order with whitespace normalization only. Native chapter
headings are context, never denominator rows. Inspect any nonheading authorial
text outside p; if found, retain an explicit extraction exception and stop
negative claims until its coverage is resolved. No convenient passage selection.
The full extraction stays local/runtime; publish source URLs, hashes, paragraph
metadata, original annotations and correction records, not the full source.

Primary local incidence interval: E/A definite; E/A/U possible. Separate scope
interval additionally includes ACTIVE/UNCLEAR topics. Chapter incidence is the
union across its paragraphs, not a new sample. Report book-specific and wholework
counts, paragraph wordlength range, all positive/uncertain records, and complete
read coverage. No conversion to source-token counts or Voynich unit probabilities.

After firstannotations are frozen, independent limitedreview covers ALL positive,
anaphoric, topical or U rows plus first and last paragraph in EVERY chapter
(deduplicated). Reviewer reads whole corresponding chapters for context. Log
changes explicitly and report original/reviewed results. Then supplementary
case-insensitive winter/summer/hiver/hibern/aestiv/season/cold/heat search can
identify omitted candidates; it never licenses unread negatives. Newly spotted
issues are recorded as corrections, not edits to the original annotation.

Runner replays extraction/coverage/count arithmetic and requires all41chapters.
Validator independently verifies raw hash, chapter/paragraph coverage, annotation
schema and aggregation; code cannot certify semantic truth. Limited secondread
is separately identified from mechanical PASS. A missing row or incomplete read
makes the pilot INCOMPLETE with no low-seasonality conclusion.

## Prior exposure, decision, and ceiling

Existing Galen extracts/arguments and the earlier winter mistake are known.
The complete sourcebody/counts have not been opened for this pilot before this
registration. Hypothesis motivation is retrospective; endpoints are prospective.
Unexpectedly widespread seasonalcontent changes the qualitative rarity expectation.
Low incidence leaves the already unpreferred WINTER/SUMMER guesses unchanged.
Strong scope sensitivity weakens the heuristic. No mechanical threshold converts
this one work into a representative corpus or a universal upperbound. No third
concept, new source, target search, classifier or semanticdecoder is authorized.
