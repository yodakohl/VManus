# B4 / Gr1 written-data contract review

Source-only technical inventory, 3 October 2026. **GO for a fixed, conservative editor-encoded written-source protocol with explicit unknowns; NO for claiming that every word has a lossless native spelling or independent native word boundary.** No fit, dataset builder, image view, new corpus retrieval, or target access occurred. The companion JSON contains the exact two source pins, body-tag/reference inventories, all 46 expanded-only blocks and the proposed reference-only glyph keys. Counts below describe markup before any eligibility projection; they are not model sample counts.

| Body inventory | B4 | Gr1 |
| --- | ---: | ---: |
| Top-level recipe `seg` records | 269 | 268 |
| `abbr` | 1,174 | 5,054 |
| With both `ex` and `am` | 1,164 | 4,990 |
| With neither | 10 | 63 |
| With `ex` but no `am` | 0 | 1 |
| `ex` / `am` nodes | 1,166 / 1,166 | 5,089 / 5,081 |
| `expan` / `choice` | 0 / 0 | 46 / 0 |
| `w` / `w` containing line breaks | 55 / 49 | 169 / 167 |
| `w` containing page breaks | 0 | 9 |
| `del` / `add` | 66 / 17 | 160 / 23 |
| `unclear` / `supplied` | 1 / 9 | 30 / 261 |
| `sic` / `corr` / `gap` | 11 / 0 / 0 | 21 / 0 / 0 |

**Characters can be projected without exposing abbreviation boundaries or gold restoration positions.** Walk the original body in document order. Omit `ex` text from the written stream; unwrap `abbr` and `am`, retaining their actual written text and glyphs. Do not emit wrapper boundaries, abbreviation flags, the number/location of `ex` nodes, or semantic glyph names to the learner. Preserve ordinary literal character case and Unicode distinctions. Ignore `g` display text as a fallback because it can be normalized (`1/2` is not the declared stroked-j glyph). Full original markup belongs in a separate conservation ledger. The expanded stream and its alignment belong to training/scoring supervision, not to written-input construction.

The reference-only key is the consistent documented Unicode/graphic class in `o:corema.chardec`, not its `normalized` or `transcription` mapping. Private-use codepoints remain opaque graphic classes. There are 42 used reference categories across the two bodies, including the missing-reference category. Thirty-six references have consistent documented keys, collapsing to 25 graphic keys; six categories remain unknown under the conservative rule. This inventory does not prove that those classes capture all native allographs.

| Same documented graphic key | References that must not become different written signs |
| --- | --- |
| U+0305 overline | `bar_d/e/em/en/in/m/n` |
| U+0315 comma above right | `combcomma_e/er/r` |
| U+A751 stroked p | `pbardes_per/perir` |
| U+F153 superscript ur-shaped mark | `urrot/tur/uitur` |

Gr1 uses undeclared `jbar` 11 times, `bar_tl` four times, `indot` once, and one `g` without `ref`. These stay UNKNOWN; similar names are not a repair license. Two declared categories also need UNKNOWN rather than automatic codepoint merging: `tlbar` says codepoint U+2114 but displays an overline and has glyph name TL BAR SYMBOL, whereas `lbbar` consistently represents ℔; `etcamp` says U+0026 but its graphical symbol field is `&c`. The JSON retains both conflicting fields. It would be premature to select which is the native shape without further evidence. Counts include deleted/editorial contexts; a future projection must publish its own affected-position counts.

**Gr1 cannot supply a native spelling for every expansion.** Its 46 `expan` blocks are not `choice` pairs; 45 occur inside one foreign passage. Most contain expanded words alone; some contain ordinary glyphs or a surviving mark. Their whole native spelling is nevertheless not recoverable by stripping `ex`, because the source does not distinguish all supplied letters. Keep each affected source span as UNKNOWN, with complete content in the withheld gold/conservation ledger. Never copy its readable expansion into the written input or silently delete the span. Expanded-word counts within such a span must not become input boundaries; scoring may charge all its gold obligations as unknown/error.

The single `abbr` with `ex` and no `am` is `plu<g ref="#combuml"/>rme<ex>n</ex>`: its surviving carrier is preserved, but no artificial mark may be added. Nine Gr1 abbreviations have unequal `ex`/`am` counts (including this case, a two-restoration/one-mark `sequitur`, and seven `talentum` instances). That is not automatically an encoding error or an epsilon writing law: one sign can support several restorations. Do not train separate restoration positions from the `ex` structure as if they were observable sign boundaries. Neither source has whitespace inside `ex` nodes.

**Word boundaries are available only under an explicit editorial boundary convention.** Most words are separated by literal source-transcription whitespace, without `w` tags. XML indentation is formatting, not measured word gaps. A reasonable fixed projection collapses whitespace outside `w`, treats line/page/column changes outside `w` as separators, and joins the pieces inside `w` across their line/page breaks. Preserve written hyphen glyphs as characters or a separately fixed graphic event; do not delete them opportunistically. B4 has 50 `w` nodes with the double-oblique-hyphen glyph; Gr1 has 167. No `lb` has an explicit `break` attribute. Thus `w` is editor-supplied word-join information, independent of expansion letters but still a boundary assumption. Do not assert it was discovered by the learner. A derivation relying on wrappers around `abbr`/`ex` to create word boundaries would fail this contract.

**Revisions and reading uncertainty need a frozen projection, not concatenation.** Preserve notes and all changes in the source ledger, but exclude modern editorial `note` text, heading pointers and transposition instructions from character input. `supplied` characters are not observed writing. `unclear`, expanded-only spans, conflicting glyphs and ambiguous revision boundaries must yield explicit unknown spans. `add` is written addition; `del` is deleted writing. Root must choose an unchanged final-state or layered transcription policy before model construction; concatenating both produces false words. `mod`, `metamark`, `handShift`, and `listTranspose` occur in Gr1 and cannot be mistaken for lexical characters. Margin/heading insertion order is already editorially encoded; XML order is not a complete two-dimensional physical-position claim.

These conditions allow a source control to keep every admitted record and disclose all unresolved obligations. Novel abbreviations, held out-of-vocabulary expansions and unknown spans remain separately counted errors/uncertainty. They do not establish a native writing-channel inverse, a target lexicon, or permission to modify previous control outcomes. No model selection is made here.
