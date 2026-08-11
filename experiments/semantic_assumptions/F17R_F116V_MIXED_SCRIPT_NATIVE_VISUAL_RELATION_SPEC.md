# f17r / f116v mixed-script native visual relation check

Date: 2026-08-11

This is a bounded manuscript-native inspection of the two folios most often
cited as possible plain-script/Voynich-script bridges. It does not evaluate a
proposed language or marginal transcription. The question is physical: do the
scripts occupy integrated lines, and does either line visibly assert an
equivalence?

## Official witnesses

Yale manifest: `https://collections.library.yale.edu/manifests/2002046`

- f17r canvas:
  `https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006106`
- f17r image SHA-256:
  `9ed091881b24f31504a5daa064c131f06b0bce10e8346f3dbe20de6cdaf2452f`
- f116v canvas:
  `https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006277`
- f116v image SHA-256:
  `0f2e8691a66f255159b28f3fc2984633016f96c30c6d4d89cff6396708e5bb17`

## Bounded questions

1. On each folio, do plain-script-looking and Voynich-style groups share one
   continuous line and approximate baseline?
2. Does either line contain an equality/gloss marker, correction, pointer,
   interlinear alignment, or repeated paired value?
3. Does the physical layout authorize treating one script span as a
   translation of the other?

## Decision rule

Same-line mixed-script adjacency is retained as a context candidate if both
script appearances share one line. A bilingual anchor additionally requires
an author-visible equivalence relation or independently repeated paired value.
Ordinary word spacing and continuation on one baseline are insufficient.

## Exclusions and ceiling

No OCR, automatic transcription, multispectral inference, proposed reading,
language fit, decoder claim, CLIP, embedding, or image-similarity score is
used. The observations are machine-authored rather than literal human
annotation.

A pass may establish only mixed-script same-line context. It cannot identify
the hand, language, word boundaries, syntax, glossary function, plaintext, or
translation.
