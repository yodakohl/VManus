# AO source acquisition

Acquired 2026-09-29 UTC from the official BnF Mandragore/IIIF path. The record `https://mandragore.bnf.fr/ark:/12148/cgfbt74042j` identifies **f. 26r, Rose des vents**, manuscript **Latin 18499**, folio **f. 26r**. Its own Mirador link is `https://mandragore.bnf.fr/mirador/ark:/12148/btv1b8101039h/f2`. The linked viewer HTML declares document id `btv1b8101039h`, page index 1; the official Mirador bundle constructs the manifest URL `https://mandragore.bnf.fr/ark:/12148/btv1b8101039h/manifest.json` and selects canvasIndex 1. Thus the association follows the BnF record's own viewer link and configuration, not an inference that “f2” means folio 26r.

The selected manifest canvas has dimensions **1920 × 2952** and offers `https://mandragore.bnf.fr/iiif/ark:/12148/btv1b8101039h/f2/full/full/0/native.jpg`. The full-canvas request returned JPEG bytes at those dimensions, below the preferred 2500–4000 px range and matching the maximum size declared by official IIIF metadata. No visual claim is made about whether the canvas depicts the entire physical folio: pixels were not viewed, so root should verify page extent during the first native inventory.

The unchanged image bytes, exact URLs, official folio identity evidence, dimensions, scope and SHA-256 hashes are in `AO_FETCH.json`. No adjacent folio, alternate source, crop, OCR, image edit, or Voynich data was accessed. Image bytes were not opened, displayed, or interpreted.

## Publication handling

The unmodified `AO_BNF_RECORD.html` retrieval is local-only because it embeds transient `;jsessionid=` URL parameters; its raw digest is intentionally not recorded. `AO_BNF_RECORD_PUBLIC.html` is an otherwise byte-preserving text projection with those URL parameters removed; its SHA-256 is bound in the receipt. The 16.8 MB official Mirador vendor bundle is retained locally as navigation provenance only and excluded from the reproduction packet. The public packet consists of the sanitized record projection, official Mirador HTML, IIIF manifest and Image API info JSON, and unchanged native JPEG. No cookies, response headers, or local machine paths are included.
