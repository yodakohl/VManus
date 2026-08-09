# f57v–f77v COLD-position form bridge audit

## Result

**PROVISIONAL, transcription-sensitive cross-page candidate; no word gloss.**

The f57v label at the independently mapped southwest **COLD quality position**
and the top-center f77v label have the following manual readings:

| Edition | f57v.8 | f77v.3 | Complete equality |
|---|---|---|---|
| ZL3b | `olkeedal` | `olkeedal` | yes |
| IT2a | `olkchdal` | `olkeedal` | no |
| RF1b | `olkchdal` | `olkee al` | no |

The older Stolfi label inventory also prints `olkchdal` for both locations,
under different transcriber codes (`V` for f57v and `U` for f77v). This is
useful corroboration of a similar long form, but not an independent semantic
observation.

All three current readings preserve an `ol`+`k` parsed component in both
locations. That component is not specific: the same all-reading word-level
component occurs at 418 loci on 95 pages, including 16 `L` loci on 14 pages.
The broader written `keedal` family occurs 16/15/11 times in ZL/IT/RF and
crosses multiple sections.

## Ownership and witness QC

The human annotation fixes f57v.8 at 07:30 inside the four-person wheel. Its
COLD value is a **page-role translation** from the replicated Harley MS 3099 /
Walters W.73 phase, not a prior lexical reading of the string.

The f77v.3 annotation is explicitly hedged: the label is near the north/center
nymph and may instead belong to the left end of the right double-Y tube.
Proximity does not establish either owner, and neither possible owner has a
readable COLD value.

Quality-control inspection used only the official Yale IIIF witness, never OCR
or automated recognition. The live manifest matched the frozen SHA-256
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
The inscriptions are visibly similar in overall length and structure, but the
f57 middle cluster is faint enough that inspection cannot resolve `kch` versus
`kee`; RF's possible f77 space also remains. Pixels selected no transcription
and are not a semantic input.

## Interpretation ceiling

Retain only:

> f57v.8 COLD-position ↔ f77v.3 similar-form cross-page candidate.

Do **not** translate `ol`, `k`, `ol+k`, or `olkeedal` as COLD. Do not infer a
temperature, nymph, organ, tube, inlet, or outlet meaning for f77v.3. A real
test now requires either a third independently and explicitly owned
HOT/MOIST/COLD/DRY value frozen before its Voynich string, or new
author-visible evidence resolving f77v.3 ownership.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f57_f77_cold_bridge/audit_f57_f77_cold_bridge.py --output experiments/semantic_assumptions/results/f57_f77_cold_bridge.json
```

The script binds all three source files and asserts the reading, prevalence,
label, and `keedal`-family counts. It computes no significance score.
