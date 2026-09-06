# GDT855 — metadata-only new leaf-margin source availability

Unknown: whether the current179selector textual scope contains any herbal
physical folio beyond all60previously judged LM001/LM001X/LM001Y folios.
Root reviewed LM001/Y/LM002 predecessors. LM001 contributes32folios including
16calibration and16held; extensions add19and9. LM002's44does not include the
16calibration folios and is not the total exposure exclusion. GDT363 reused
the same44visual panel without adding image exposure; its broad formal atlas
does not supply new physical observations. No formal-atlas fit is selected.

Freeze five TSV projections in SPEC before any query. ANN only page,
source_tags,quire; ZL only page,language,section,hand,quire, both selected by
explicit179page allow-values. Historical selection tables only page and
physical_folio, selected by explicit f1..f116 excludingf84. Their broader
page metadata reconstructs old exposure even where a selected page is outside
current179; it does not admit those pages to new text/image inspection.
All use ./vmanus-exp query-tsv, explicit selector/columns/allow-values and
both f84/f84r prefix exclusions before payload materialization. No text,
glyph, leaf outcome or image fields are requested. The LM002
parisel_cho_che_folio_states.tsv file is forbidden even for hashing.

Retain the first ZL metadata row per page in source order, as old selectors
do. Require ANN page uniqueness; duplicate ANN pages cause a source-
inconsistency stop rather than an arbitrary first-row eligibility choice. Join
on exact page; quire=ANN quire when nonempty, else ZL quire. Eligible pages
must be in179, have SOURCE_HERBAL_PAGE as a substring of source_tags,
have first-ZL language A or B, and a numeric fN folio prefix. Keep every
eligible page; do not pick one hash-ranked page per folio. Subtract the
ENTIRE old60physical-folio set, regardless of which old page was selected.

Verify historical tables have32/19/9rows, unique physical folios within each,
and disjoint sets totaling60. Any inconsistency stops remainder calculation
with an explicit source-inconsistency status; do not repair old selection.
Report OLD_EXPOSURE, full SAFE_METADATA and EVERY remaining page/physical
folio with its projected metadata. No association test, outcome reading,
new page admission or calibration follows automatically. Nonempty remainder
would identify available source candidates, not visually known margin states;
empty remainder closes this current-scope acquisition option.

The experiment binds safe projection bytes/hashes and compact outputs, not
full restricted source-table contents. Reproduce via the same guarded
projections; cached --check validates the saved metadata derivation. An
independent validator checks first-row joining, exposure consistency and
set subtraction. No new statistical model. Budget10min total including root
publication, starting about05:28UTC. Public preregistration and GO precede
all five queries. Do not expand scope or reopen protected outcomes on zero.
