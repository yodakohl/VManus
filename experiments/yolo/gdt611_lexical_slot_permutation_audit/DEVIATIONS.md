# Guarded implementation corrections

Recorded after the first mechanical run and before interpretation/reporting.

1. The preregistered section permutation treated the section code as a
   physical-folio label.  The guarded stream reveals four physical folios with
   two section codes (`f66`, `f76`, `f86`, `f85`).  A dominant-label
   permutation would silently relabel minority events.  It is retained only as
   a diagnostic.  The primary null now excludes those four mixed-section
   folios and recomputes both the observed score and every permutation on the
   remaining 87 single-section physical folios.  This is a stricter whole-folio
   test and cannot create an object-owned lexical anchor.
2. A held frame counts toward the preregistered reuse gate only if the *same
   exact frame* was shared by the same carrier pair in train.  Held-only shared
   frames are reported nowhere as transfer evidence.  This implements the
   frozen instructions “held reuse” and “do not add a held-only edge.”

No candidate, label order, threshold, family score, or paragraph selection was
changed.
