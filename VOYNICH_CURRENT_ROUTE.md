# Voynich current route
Updated: 2026-09-05. Read first.

## Current mandate

User explicitly requested an independent methodological reset after GDT828.
Goal: a transferable decipherment. No confirmed lexemes or clauses exist.
Stop extending the guessed water/vapour/manual-treatment dictionaries as the
main research programme. Language, encoding, sign units and word boundaries
are open. Earlier model choices and route closures are claims to audit, not
proof that every other mechanism is impossible.

Read `docs/RESEARCH_RESET.md` for the current decision. Do not automatically
resume GDT828's attachment problem. Its conditional result remains archived.
`./vmanus-work lookup GDT827 GDT828 GDT612 GDT613` gives relevant audit pointers.

## Next work

Build a small explicit encoding attack with measurable plaintext recovery.
First candidate for specification: a two-phase homophonic letter channel on
continuous text across line breaks, with arbitrary displayed gaps, one emitted
letter per source atom and no word glosses. GDT001 already tests two-phase
homophony but resets at lines/groups and retains source spaces. The proposed
difference is cross-line phase/gap independence plus calibrated key recovery,
not the bare cipher family. This is a test candidate, not manuscript evidence.
Fix an auditable atom policy; opaque entities must not silently change phase.
Test hidden keys and arbitrary gaps on independent known-text controls.

Use normalized forward ciphertext probability; account for homophone choices.
Judge the method by recovery of withheld plaintext, not pleasant output,
roundtrip alone, dictionary coverage, or a successful artifact validator.
Do not import fixed FST34 role counts or the 98-unit BPE alphabet as facts.
A model unable to recover its own covered controls has not tested Voynich.

A joint segmentation/encoding model and recurrence-based neural decipherment
are methodological options, not established findings or automatic fallback
searches. Select one bounded executable mechanism at a time. GPU and subagents
are authorized; no other LLM API keys may be used.

## Source scope and fidelity

- Visual admission: original30 pages/35 selectors in GDT791
  `src/PAGE_SELECTOR_SPECS.tsv`, plus f21r/f32v/f100v/f101r in GDT812
  `src/PAGE_ADMISSIONS.tsv`:34 visual keys/39 selectors;16 admissions remain.
- Inherited text scope:179 selectors in GDT631
  `artifacts/PAGE_ALLOWLIST.tsv`. It is not179 visually inspected pages.
- GDT811 union190 and GDT327's91-folio edition do not enlarge admission.
- f84 and f84r remain sealed. Record admissions before any new page access.
- Preserve panel keys f67r2/f68r1. Page, selector and physical folio differ.
- Best source-group atlas: `experiments/semantic_assumptions/results/source_separator_transcription.tsv`.
  Query mixed sources ONLY through `./vmanus-exp query-tsv` with explicit
  selector allow-values and output columns; reject f84 prefixes before payload.
- EVA labels are not Latin initials or established phonetic units. ZL3b/IT2a/
  RF1b are alternate readings of one manuscript, not independent witnesses.
- Preserve raw groups, extended @entities, uncertain spaces and native flags.
  Legacy cleaners can split/delete source groups; source line ends are not
  established clause boundaries. GDT819 governs the active image corrections.
- Yale1006204 is72v,not72r. GDT812 `src/F72R_SOURCE_CORRECTION.md` governs.
  f116v is not admitted. No old image label identifies a word or species.

## Prior work and recording

Use `./vmanus-exp route-check QUERY` before a new route as navigation only;
inspect relevant primary reports and closed-family rows. Record the actual
scope of a past negative and the new discriminator. Do not repeat an unchanged
failed implementation or reinterpret successful software checks as semantics.

GDT001–336 byte-frozen;GDT337+ scaffold under experiments/yolo with manifest;
GDT394+ seal f84/f84r explicitly. New score-ready relation evidence requires
`./vmanus-exp check-edge-packet` and all capacity/provenance/held/mobile-null gates.
Structural relations remain distinct from translated words.

Publish material findings with compact reproducible source/results after staged
privacy checks. Keep unrelated work. The full worktree has pre-existing GDT600
binding/index debt; focused staged validation does not clear it.

`VOYNICH_ACTIVE_STATE.md` and the append-only ledger hold detailed claims.
Read targeted sections only. Old logs/handoff and prior route versions in Git
are recovery archives. Workflow: `docs/WORKFLOW.md`.
