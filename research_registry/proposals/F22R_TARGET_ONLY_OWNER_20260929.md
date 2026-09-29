# f22r target-only owner review — 2026-09-29

Exploratory target-side evidence freeze for the two-structure source-capacity screen. This note does not assign a botanical identity or word meaning and does not alter GDT765 or GDT1087.

## Sources inspected

- `VOYNICH_CURRENT_ROUTE.md` — live boundary and current route.
- `research_registry/proposals/F22R_TWO_ORGAN_SOURCE_CAPACITY_20260929.md` — question, decision consequences, and screen limits.
- `experiments/yolo/gdt765_ofchy_schor_content_field_discriminator/REPORT.md` and the claim-bearing artifacts `TARGET_6_EXACT_OCCURRENCE_ATLAS.tsv`, `TARGET_RAW_EXACT_AUDIT.tsv`, `F22R_4_VALUE_GRID.tsv`, and `F22R4_9_TOKEN_WORKING_READER.tsv`.
- `experiments/yolo/gdt1087_botanical_blind_name_audit/REPORT.md` — f22r row for `pol` / MORUS.
- [Official Yale f22r canvas](https://collections.library.yale.edu/iiif/2/1006116/full/full/0/default.jpg) — admitted f22r image; the previously verified local cache copy was viewed at native resolution.
- Guarded `./vmanus-exp query-tsv` results from `transcription/voynich_zl3b_lines.tsv` and `transcription/voynich_cross_transcription_lines.tsv`, selected only for `page=f22r`.

No external source candidate, source-only review, botanical ID list, f84/f84r, f116v, or reserve material was inspected.

## Image observations and bounded inference

**Observed in the admitted image:** One plant drawing has a single visible root mass, a central upright stem, leaves attached below the upper structures, and one paragraph of text above the drawing without visible pointers or labels to individual organs. Three dark blue cup/bell-like terminals occur at the top. Each is at the end of a distinct, relatively long branch connected to the upper central stem: one nearly vertical central branch and two lateral branches. Beneath and around those branch junctions, numerous thin pale stalks fan outward from the same upper stem region; each carries repeated red and pale outlined bead/ring shapes. The two structural arrays overlap in the same compact upper crown area, with the blue terminals visually above the bead-bearing array. There is no separately drawn root system or explicit boundary between two plants.

**Inference, limited to the drawing:** The blue terminals and bead-bearing axes belong to one illustrated plant architecture and are drawn as distinct terminal structures on distinct branches/stalks. The picture is compatible with simultaneous unlike organs, successive stages represented together, or a composite/stylized rendering. Their common plant attachment supports visual co-occurrence; it does not resolve whether the structures coexist biologically, represent stages, or are composite. The image does not connect any written field to a specific terminal or stalk, and it gives no temporal relation.

The image does not establish that every bead-bearing stalk independently branches from the main axis; several bases converge and overlap in the crown, so individual attachment paths are partly obscured. Nor does “cup-like” or “bead-bearing” identify an organ type.

## Complete admitted text owner and exact fields

The complete admitted target-side page owner is the f22r page in the ZL3b line cache, with IT2a and RF1b retained as alternate readings of the same manuscript. The guarded page query returned 13 lines, all tagged Herbal (`H`), language `A`, hand `1`, paragraph-line records. f22r.4 is a 9-token line. The exact line in all three owner columns is:

```text
pchaiin ofchy daiin cfhy doroiin ypchol sy schor daiin
```

The first two paragraph lines also agree across all three readings. Other differences elsewhere on f22r (for example f22r.2, .3, .6–.9, .11, and .13) show that the reading columns are not globally interchangeable, but none changes the two f22r.4 target fields. These are transcription-owner facts, not evidence that the two fields caption the drawing.

GDT765 proposes two exact value fields on the same line. Both are in the middle of the line, separated by four tokens (`cfhy doroiin ypchol sy`):

| Exact field | Position in f22r.4 | GDT765 structural/default proposal | Status and live alternatives |
|---|---:|---|---|
| `ofchy daiin` | `ofchy` ordinal 2; `daiin` ordinal 3 | `ofchy` as a nominal material/preparation head; `daiin` as a scalar value (III). Bold concrete rendering: “three units of flower mass.” | Role selected at C2 context convergence; concrete `Blütenmasse` is C0 bold family lead. `Blütenzubereitung` remains the close concrete rival; value may be amount, value, or class III. No confirmed lexeme. |
| `schor daiin` | `schor` ordinal 8; `daiin` ordinal 9 | `schor` as an H2 item / plant-part head; `daiin` as a scalar value (III). Bold concrete rendering: “three units of inflorescence.” | Item-head/value-carrier role C2; reproductive-part identity is only C1. `Samenstand` and generic plant-part item remain rivals; value may be amount, value, or class III. No confirmed lexeme. |

GDT765 records the full local sequence as nine tokens and its claim ceiling explicitly does not identify an image, new transcription, confirmed lexeme, or global meaning for `daiin`. Thus “two fields” is a local structural proposal. It is not an independently established pair of organ labels.

## Exact recurrence and boundary facts from existing caches

GDT765’s reader-exact audit reports three exact `ofchy` positions: f22r.4 token 2 (`ofchy daiin`), f26v.5 token 8 (`ofchy chs ar`), and f39v.1 token 7 (`ofchy kar or aiin`). It reports four raw occurrences overall; raw f39v.5 is excluded because ZL3b has `ofchy` while IT2a/RF1b read `opchy`. The audit requires reader-exact targets, so that disputed occurrence is not evidence for the exact form.

The same audit reports three exact `schor` positions: f22r.4 token 8 (`schor daiin`), f32r.4 token 1 (`schor`, line-initial before non-exact `dshor`), and f42v.10 token 1 (`schor okchey`, line-initial). No non-exact `schor` locus is listed. The exact f22r.4 pair occurs in one line but the heads are not adjacent: `cfhy doroiin ypchol sy` separates them. The line cache and cross-reading cache confirm the f22r.4 token sequence and line extent; they do not supply punctuation, semantic field boundaries, or image links.

GDT765's two exact fields are therefore complete as *proposed spans* (`ofchy daiin`, `schor daiin`), while their content identities and any alignment to the drawing remain working interpretations. The `f22r.4` assignment does not cross a line boundary. Broader attachment of either field to a pictured organ would require evidence beyond the co-presence of text and illustration on the same folio.

GDT1087's exact f22r row is: `pol` — MORUS — **UNDECIDABLE** — “Blue cups and red bead spikes may be differing organs; no reliable mulberry fruit or tree diagnosis.” This preserves unresolved visual identity and is not a plant-name anchor.

## Facts versus inference

- **Facts from the consulted records/image:** a single depicted root/stem/leaf architecture; three blue terminal cups on separate branches; many bead-bearing stalks clustered below/on the same upper axis; text above without explicit visual callout; a 13-line admitted f22r ZL3b owner; identical f22r.4 readings across all three columns; GDT765's two proposed value spans and its stated confidence limits; GDT1087's undecidable f22r classification.
- **Inference only:** the two arrays likely represent unlike drawn structures on one plant. Simultaneous organs, successive stages, and composite/stylized representation remain viable explanations. No botanical identity, relation of stages, or semantic field-to-image alignment follows from these observations.

## Possible falsifiers / reopening evidence

- A fresh, independently checked tracing or better official image showing that one array is detached, belongs to another figure, or does not attach to the shared plant axis would falsify the shared-architecture inference.
- A material/overpaint examination that changes the visible branch and attachment paths could revise the geometry; the current image alone cannot decide hidden overlaps.
- An admitted primary source with explicit text or illustration showing that both unlike structures are simultaneous organs, successive stages, or a composite could discriminate the relation. A look-alike image or source name alone cannot.
- A revised admitted reading at f22r.4 or a justified line-boundary correction changing either exact string/span would falsify the transcription facts used here. Current guarded cache readings agree exactly for both fields.
- Even an explicit source relation would not by itself confirm `ofchy` or `schor`; a fixed Voynich contrast with preregistered contexts and independent confirmation would still be needed before semantic commitment.
