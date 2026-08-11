# f68r2 Sun-ring native visual script check

Date: 2026-08-11

This is a bounded source check of the existing `F68CL001` stop, using the
user-authorized source-bound native visual method. It is not OCR, a decoder
test, or a lexical search.

## Selection and source

The physical target was fixed by the earlier public-source audit before this
image pass: locus `f68r2.31`, the circular text around the lower Sun-face
medallion. The inspected witness is the official Yale canvas labelled `68r`:

- manifest: `https://collections.library.yale.edu/manifests/2002046`
- canvas: `https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006196`
- image: `https://collections.library.yale.edu/iiif/2/1006196/full/full/0/default.jpg`
- dimensions: 7993 x 3828 pixels
- image SHA-256:
  `4b0f31d1e08b8f026886aa599232b7dfcd33417b1eef43a44e619c3ebd21faa5`

The initial whole-panel view located the medallion. Before the final
magnified and rotated inspection, the following questions were fixed:

1. Is most of the ring visibly written in ordinary Voynich-style forms?
2. Do the disputed final marks occupy the same circular text band?
3. Do rotations expose a stable, independently readable plain-script
   sequence?
4. Does the image itself support `SUN`/`Suna` without using that proposed
   reading as a prompt?
5. Does the image resolve the ZL3b/RF1b illegible-mark reading against IT2a's
   `koiin` reading?

Display crops and 0/90/180/270-degree rotations are deterministic views of
the same source image. They add no image evidence.

## Decision rule

The route reopens only if the full disputed ending can be segmented and read
as a stable plain-script sequence from the source image without importing a
proposed word. Otherwise the existing no-cleartext stop remains active.

## Exclusions and ceiling

No OCR, CLIP, embedding, batch recognition, prompt-scored reading, automated
glyph classifier, or external decoder claim is used. The observations are
machine-authored native visual inspection, not literal human annotation. A
stop at this image resolution does not rule out a future independently
documented multispectral or specialist palaeographic reading. It establishes
no word, sound, language, cipher, plaintext, meaning, or translation.
