# GDT676 artifacts

All outputs are rebuilt by `../src/run.py`; `../src/validate.py` independently
checks their counts, identities, hashes and byte-identical replay. The compact
result is `RESULT.json` and the human-readable edition is
`GDT676_V50_EXTERNAL_WORKING_READER.md`.

## Reader outputs

- `V50_EXTERNAL_TOKEN_READER.tsv` — all 479 source positions with upstream and
  V50 glosses, information class, action flag, abstraction flags and GDT675
  occurrence metadata.
- `V50_EXTERNAL_LINE_READER.tsv` — the 51 source lines in source order, with
  token strings, literal gloss vectors, practical reading, explicit residual
  forms, line mode and review note.
- `GDT676_V50_EXTERNAL_WORKING_READER.md` — the same 51 lines as a readable
  edition; every unresolved position remains `⟦surface:?⟧`.

## Rankings and diagnostic passages

- `LINE_INFORMATION_RANKING.tsv` — all 51 lines ordered by fewest residual
  unknowns, then other assigned support and compactness.
- `LOW_RESIDUAL_FRONTIER.tsv` — the 28 lines with at most two unknowns; it
  includes two complete, nine one-gap and seventeen two-gap lines.
- `PAGE_TRANSFER_RANKING.tsv` — the ten pages with multiple touched lines,
  ranked by assigned fraction and support.
- `PASSAGE_TEST_DECK.tsv` — the complete f112v.10 control, the f102v2.3
  singleton, adjacent f86v6.4–5 stability passage and adjacent f86v3.18–19
  action contrast.
- `REGISTER_HAND_PROFILE.tsv` — assigned coverage by section/register,
  language and hand.

## Renderer audits

- `ACTION_SCOPE_AUDIT.tsv` — licensed action ordinals and the named f26r.2
  nominal override for all 51 lines.
- `VALUE_ATTACHMENT_AUDIT.tsv` — 17 local attachment decisions: ten accepted,
  three provisional and four rejected jumps.
- `SYNTAX_TEMPLATE_CARDS.tsv` — eight visible context/scope templates.
- `RENDERER_RULE_CARDS.tsv` — the ordered information classifier and hard ban
  on generic work-item/work-cycle prose.
- `INFORMATION_CATEGORY_COUNTS.tsv` — the exact `51/136/77/215` partition,
  literal-overlay narrow counts `105/106`, working-reader narrow counts
  `113/114`, the extended class sensitivity count
  `311/343 = 0.906706`, and zero hard-generic matches in either layer.

## Certificates

- `RESULT.json` — status, basis, information and line counts, renderer summary,
  next frontier and SHA-256 hashes of generated reader artifacts.
- `VALIDATION.json` — independent 18,770-check reconstruction and
  byte-identical fourteen-file replay certificate.

These artifacts document 51 rendered lines, not 51 complete translations:
136 positions and 49 lines remain open. “Assigned” is never shorthand for
confirmed meaning. Both f84 and f84r are forbidden.
