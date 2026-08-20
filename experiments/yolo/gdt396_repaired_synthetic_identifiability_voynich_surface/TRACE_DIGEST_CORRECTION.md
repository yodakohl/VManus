# GDT396 pre-decoder trace-digest correction

Status: `CORRECTED_BEFORE_DECODER_ACCESS`.

The first paired manifests computed `hidden_trace_sha256` from in-memory
generator values before deterministic TSV serialization. GDT395 normalization
retains integers in a few fields, while TSV reconstructs every scalar as text;
the digest was therefore not independently reconstructable from stored rows.

The paired corpora themselves are unchanged. The first validation established
byte-exact legacy FREE and oracle reproduction, exact paired non-surface rows,
exact constrained surfaces, legal relation/scope endpoints, and an exact
24-atom channel; only the redundant trace digest failed.

Before any decoder saw development data, GDT396 froze V2 manifests that bind
the original manifest hash and redefine `hidden_trace_sha256` over the stored
FREE observation rows with `visible_group` omitted plus the stored oracle rows,
all as TSV text scalars. The V1 manifests remain retained as historical
artifacts. No corpus, oracle, codebook, genealogy, surface, seed, threshold, or
scientific endpoint changed.
