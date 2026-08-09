# f69r.49 `ed` / `em` manual reading QC

Date: 2026-08-09

Status: **POST-HOC HUMAN TRANSCRIPTION QC — `ed` FAVORED**

## Scope

This audit asks only which manual EVA surface is the better representation of
the physical two-character item at f69r.49. It was motivated by the completed
F69C001 result and therefore cannot upgrade or rerun that experiment.

No OCR, automated image recognition, embedding, enhancement, classifier, or
machine-generated caption was used. Images were downloaded, located from the
human folio catalogue, and cropped without contrast or colour changes for
direct human inspection.

## Sources

1. The first digitization is the 2004 f69r JPEG distributed at
   `https://www.voynich.com/folios/color/069r.jpg`, 1152 by 1536 pixels,
   SHA-256 `093f4550a86050db1264870f9dd41e847f9b91d0b25141253ff845c1eab514ff`.
2. The second is file `125.jpg` from the Internet Archive item `voynich`, whose
   metadata identifies the files as original-quality JPEG conversions of the
   2014 Yale JP2 scans. It is 2793 by 3763 pixels, SHA-256
   `803e02a64a0f68a6fe38ec5b50c5167a47888ade4221b5088f637ce2b34f84a7`.
3. The human quire catalogue independently maps f69r to Yale child object
   `1006198` and documents that the manuscript was digitized separately in
   2004 and 2014.
4. The existing exact-locus annotation says for f69r.49 at 07:30 that René
   confirmed the `ed` reading against the original manuscript.
5. ZL3b records `e[d:g]`, RF1b records `ed`, and IT2a records `em`. These are
   alternate transcriptions of one physical item, not independent votes.

Reproduction crops, expressed as `(left, top, right, bottom)` in the downloaded
images, were `(330,500,730,900)` for the 2004 center and
`(800,1200,1900,2300)` for the 2014 center. Within the latter center crop, the
known single `d` at f69r.45 was inspected at `(375,270,520,420)` and f69r.49 at
`(300,565,470,735)`. Coordinates only locate pixels; they do not generate a
reading.

## Human observation

In the 2014 scan, f69r.49 visibly contains an initial `e`-like component and a
second loop-and-descender component consistent with the known central `d` at
f69r.45 after allowing for radial orientation. The lower-resolution 2004 scan
is compatible with the same reading and shows no contradictory stroke. This
agrees with the existing original-manuscript confirmation.

Retain **`ed` as the best current physical reading** and `em`/`eg` as recorded
transcription uncertainty. This is a human paleographic QC judgment, not a
computational result.

## Consequence and ceiling

F69C001 remains a validated nonconfirmation under its registered
all-transcription gates. Do not delete IT2a, change its stored source, rerun
F69C001, or call the nominal rank a pass. This QC authorizes only a separately
named, explicitly post-hoc `ed`-resolved sensitivity calculation asking whether
the one disputed surface accounts for the failed ranks. It cannot establish a
joined orientation, start, handedness, sound, word, root, lexeme, language,
plaintext, direction name, or translation.
