# GDT396 independent validation design

Status: `REGISTERED_BEFORE_CONFIRMATION`.

The final validator must be implemented independently of the scorer and may not
import any generator, decoder, scorer, or shared metric utility.

It will verify:

1. exact hashes for the GDT395 world freeze, interface, support modules, all ten
   generators/designs, original 200-corpus manifest/audit, GDT396 protocol,
   mapping commitment/reveal, decoder sources/attestations, qualification
   decisions, scorer, and output artifacts;
2. exact seed blocks and target size, deterministic regeneration, shared hidden
   trace, identical non-surface rows, unchanged codebook/genealogy/oracle,
   injective seed-independent two-atom maps, and constrained atom values only
   in `0..23`;
3. zero Voynich corpus/image/transcription inputs, zero manuscript rows, and
   explicit all-false `f84` and `f84r` access structures;
4. exact typed claim schemas/enums, safe IDs, Boolean spelling, rank
   contiguity, candidate membership, same-record scope, record constancy, event
   order, morphology status, finite scores, deterministic claims, and held
   model immutability;
5. complete qualification and confirmation Cartesian products, eligible-route
   freezes, no held-dependent representation/threshold/subtype selection, and
   decoder/world-designer separation;
6. direct oracle mappings only, including rejection of ambiguous typed
   relation pairings and identity-as-meaning or component-as-Boolean proxies;
7. independent recomputation of NMI, adjusted Rand, pair-F1, balanced accuracy,
   MCC, FDR, Hits@k, MRR, nDCG, interval IoU, coverage, hierarchical intervals,
   nulls, Holm correction, seed/decoder/world gates, W10 false positives,
   adversarial contrasts, surface ablation, and final decisions;
8. one result row for every registered
   `property×world×surface×representation×decoder×seed×variant` cell, including
   explicit no-capacity/unsupported rows;
9. aggregate-only public results containing no event IDs, oracle labels,
   visible strings/atom streams, local paths, secrets, credentials, or joined
   truth/claim rows; and
10. a separate validation artifact with only hashes, counts, Boolean checks,
    and sanitized stable failure codes, numeric tolerance at most absolute
    `1e-12` and relative `1e-10`.
