# Current-locus crosswalk — manual visual QC only

Date: 2026-08-07. Outcome: **PASS_NO_LAYOUT_CONTRADICTION**.

This inspection was performed only after the crosswalk had been built and
independently validated. Pixels did not select, score, move, reject, or gloss
any locus. No OCR, image model, feature extraction, crop matching, or glyph
reading was used.

Official Yale current-manifest canvases checked:

| target | Yale canvas | downloaded JPEG SHA-256 | restricted observation |
|---|---:|---|---|
| f70v2 / 70v foldout | 1006200 | `773c77f52b64c26e3493638907c6b8f23ae95a55c99f2b3c06295e441106bdce` | The fish diagram visibly has distinct populated inner and outer rings with separate short text loci. This is consistent with, and does not independently establish, the source's 10- and 19-location groups. |
| other 70v foldout view | 1006201 | `5ad7a91191bdf6c85202c689910ce775bc20ab7e5af01c6e1d3fe2417b71951b` | Confirms that the two Yale canvases are separate views of the same folded record, not independent manuscripts or replications. |
| f72r2 / 71v–72r foldout | 1006203 | `45a43e5a4c32574468ab401d740c247a886e0fc21701058614fd56d2397851d9` | Nested populated rings plus figures outside the diagrams are visibly present. This gives no contradiction to the human `INNER`, `OUTER`, and `OUTSIDE` scope keys; exact counts remain sourced from the manual annotations. |
| f75v | 1006209 | `9bd3b81df2ffa5cd26aa70c727b6c0317a67ae655e7b4ade508a10ea6a9764eb` | The upper pool visibly contains one set of ten figure/spout columns with two short written lines per column. This directly contradicts treating the U- and V-coded transcription records as forty separate physical locations and is consistent with twenty physical lines carrying two transcription witnesses each. |

The viewed files were temporary `/tmp` downloads and are not analysis inputs
or workspace evidence artifacts. Their URLs use the frozen official manifest's
IIIF service: `https://collections.library.yale.edu/iiif/2/{canvas}/...`.

Inference ceiling: this QC checks only gross layout/cardinality consistency.
It supplies no object identity, ownership relation, word reading, semantic
label, language, plaintext, or translation.
