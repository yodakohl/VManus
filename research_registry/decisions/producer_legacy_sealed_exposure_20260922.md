# Producer incident: sealed material in a legacy result object

Sanitized incident record, 2026-09-22. Research and new nominations stopped after recognition. This document contains no sealed surface values, original-image content, or hashes of the exposed payload.

## File, fields and visible extent

The producer read:

`experiments/semantic_assumptions/results/rra001_recurrent_label_owner_atlas_result.json`

The problematic field was the top-level `observations` array. Its nested fields included `page`, `locus`, `physical_folio`, `surface`, `visible_basis`, `gates`, `exposure`, `canvas_id`, `review_region` and image/region hash fields. The read displayed **two visible rows concerning the currently sealed folio**, including surface-bearing fields. None of their values is reproduced here.

Two is the count of relevant rows visibly emitted in the tool result, not a verified count of every such row in the source file. The Python call loaded the complete JSON object before output truncation. The source has not been reopened to determine a larger count or recover the truncated remainder.

The producer had treated a historical result artifact as suitable for direct primary inspection. That assumption was wrong: historical result ownership does not supersede the current f84/f84r seal. The report-level result did not make the observation array safe to display.

## Action ordering and observed clocks

1. The last clock observation before the incident-bearing tool batch was **17:45:11 UTC**. That preceding batch inspected existing reports and registry pointers; the timestamp does not claim the exact instant of the subsequent disclosure.
2. A `functions.exec` call invoked `tools.exec_command` with an inline Python script. The script used `json.loads` on the file above, printed its top-level keys, and iterated selected result fields. It printed the `counts` field and serialized the **whole `observations` field**, applying a 9,000-character slice only to the already serialized string. There was no selector check before loading, serialization or display. A string-length output limit was therefore not an access guard.
3. The same Python command then read a separate, already-owned powder-proposal lexicon and printed its keys and a bounded lexical excerpt. The same orchestration call subsequently performed an ideas search for image adjudication, a route check for repeated-plant relations, and a filename search for existing repeated-plant reports. These commands were already written in that tool call and completed before the assistant received its aggregate output and recognized the sealed rows. They did not select a scientific candidate, run a target test or mutate research files.
4. On reading that output, the producer recognized the scope violation and immediately informed root. It discontinued that observation-array line of research and stated that none of the exposed information would support a nomination or semantic inference.
5. Root interrupted the producer and assigned incident documentation only. The next observed clock, obtained solely to timestamp this record, was **17:46:51 UTC**. Thus the incident-bearing read occurred after the observed 17:45:11 clock and before the observed 17:46:51 clock. No more precise execution timestamp is asserted.
6. After recognition, there was no further scientific selection, source investigation, target opening, image access, experiment, interpretation or new idea registration. The only subsequent work was the incident clock check and this sanitized file.

This ordering is reconstructed from the producer's own tool-call memory. Neither the source artifact nor the exposed rows were reopened for the reconstruction.

## Structural cause

The command selected an artifact field rather than permitted page selectors. The top-level report and artifact name concealed that the old observation inventory mixed currently permitted and sealed folios. `json.loads` materialized the entire object, and serializing `observations` exposed row payloads before any page-level decision. Truncating the resulting string bounded output size but did not exclude sealed selectors.

This was an actual legacy-result exposure, not merely a filename match or a warning that a sealed source might exist. No claim that this producer pass was f84-free or blind is valid. Future scientific use cannot treat this producer as unexposed to that material. The incident supplies no authorization to inspect the remainder, use the rows, relax the seal or revise a hypothesis around them.

## Work that predates the incident

The most recent completed producer batch had already created and registered these four proposals before the incident:

- **IDEA000525** — `research_registry/proposals/raw_f108r_amulet_use_state_whole_continuation_20260922.json`
- **IDEA000526** — `research_registry/proposals/raw_f17r_graft_actual_case_whole_continuation_20260922.json`
- **IDEA000527** — `research_registry/proposals/raw_f31r_seed_rite_disclosure_whole_continuation_20260922.json`
- **IDEA000528** — `research_registry/proposals/raw_f83r_loan_frozen7_compact_construction_offer_20260922.json`

Their registration/check batch had an observed clock of **17:39:49 UTC**. Earlier producer proposals IDEA000519–524 likewise already existed. These files were not revised using the incident output. The separate accidental printing of previously exposed, nonsealed paragraph bodies in that earlier batch was already disclosed in its own handoff; that earlier disclosure is not a substitute for this sealed-material incident.

At assignment of the new 17:42–18:12 producer batch, root had already announced parallel work on GDT1040 and a separate IDEA000520 author. This producer did not edit either task's files. No new proposal was created or registered in the incident-bearing batch. This record does not independently certify root's exact selection or execution timestamps.

## Containment and limits

No image was loaded in the incident-bearing batch. No original f84/f84r transcription or image source was opened; the exposure came from the derived legacy JSON described above. The old source remains unchanged. No semantic consequence, word comparison, target count, physical interpretation or proposal was drawn from the exposed rows.

The producer stops research and returns idle after this report. Root retains publication and any subsequent scope or personnel decision. This record documents the exposure without reproducing the payload and does not claim to undo it.
