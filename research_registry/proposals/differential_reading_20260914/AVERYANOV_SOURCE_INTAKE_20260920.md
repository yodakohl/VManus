# Source-only review: Averyanov workshop model, 20 September 2026

## Decision and scope

No manuscript decoding experiment is selected from this intake. GDT604 remains
closed for its original U/P/S attack; neither a new paper nor a failed external
hill climb changes that decision. No new Voynich transcription or image was
opened, no third-party module was imported or executed, and all reserves remain
closed. This is a source-method finding, not manuscript or translation progress.

Question: does the new public model supply a reproducible route to content beyond
our earlier Naibbe controls? Smallest adequate review: publication metadata,
package directory, selected generator and inverse-attempt source only. The
inclusive intake budget was 20 minutes from approximately 00:20 UTC; this note
was written at the timestamp below, within that budget. A real reversible content
mechanism could motivate a separate fixed proposal; a statistics-only fit or an
inapplicable inverse test does not justify rebuilding a decoder.

## Exact public sources examined

- [Paper I and replication package](https://doi.org/10.5281/zenodo.21761192),
  publication date 2026-08-02, CC BY-NC-ND 4.0 according to Zenodo metadata.
- [Paper II metadata](https://doi.org/10.5281/zenodo.21761983), same date,
  CC BY 4.0 according to metadata. Its sigla interpretation was not replicated.
- [Replication ZIP](https://voynich.site/files/voynich_replication_v1.zip): central
  directory and selected source files only; embedded manuscript corpora, scans,
  labels and result tables were not opened. No full-paper content review claimed.
- Local GDT603 and GDT604 complete reports; topic excerpts controls/differential;
  bounded registry and route searches. Unknown cipher topic was followed by
  targeted lookup; empty Averyanov search was not treated as proof of novelty.

The homepage's strong mechanism language is not adopted. The publication's own
abstract distinguishes mechanism from decipherment and says no key was recovered.

## What the source code actually does

`test_hybrid.py::gen_hybrid` sometimes takes a previously emitted plaintext unit
from the current line instead of advancing the source pointer. It then encodes
that unit anew. A copied unit can therefore have a different written surface.
`test_secburst3.py::gen_m5` retains this choice and adds section-specific table
subsets and one recoding attempt when the surface equals the previous surface.
These are source-code observations, not replication of the claimed statistic fit.

`test_keyrecover2.py::collapse`, by contrast, removes an exact written word if
that same surface occurred among the previous five words of a flattened stream.
This neither identifies copies written through another table nor preserves the
within-line boundary of the generator. It can remove a legitimate source repeat.
Its subsequent decoder also reduces a retained group to one selected prefix and
suffix and does not invert all generator paths. Thus this program is not a full
inverse of the published generative mechanism. The negative hill-climb outcome
cannot establish universal internal unidentifiability or exclude better attacks.
The source's own blanket conclusion is therefore not adopted.

Even with a known table, the unmarked insertion choice can be ambiguous: an
observed decoded unit sequence A,B,A is compatible with source A,B followed by
a reuse of A, or source A,B,A with no reuse. Both source paths have nonzero
probability under a nondegenerate reuse parameter. This elementary witness is
not a claim that natural-language constraints cannot resolve particular cases.
It does show why simply treating every written group as independent source
content is not the same model. No synthetic benchmark is needed to prove this
small non-injectivity witness, and none was counted as a research result.

## Consequence for our next choice

A genuinely new content proposal would have to distinguish original units from
inserted copies jointly with the code and retain all competing readings. It would
need an end-to-end known-content control and a fixed target consequence. Removing
nearby equal words, improving entropy fit, or choosing Latin by default is not
that proposal. No such target consequence was supplied by this intake, so no
large control, corpus acquisition or decoder implementation follows automatically.

The next content work returns to explicitly hypothetical whole-passage readings.
No confirmed word, independent meaning validation, significance or reopened
reserve results from this source review.
