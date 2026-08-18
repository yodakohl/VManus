# GDT312 — shared `s` entry-rule compression

GDT311 was already exposed before this analysis was chosen.  GDT312 is
therefore an explicitly post-hoc mechanistic compression, not a prospective
test.

Seven GDT303 exact target surfaces participate in both a `ch->s` and a `d->s`
pair.  Treat each as one unique three-surface choice set (`ch`, `d`, `s`), so
the shared `s` events are never double-counted.  Reuse the deterministic
GDT311 training/test folio split.

Fit ridge-10 binary models for `s` versus `{ch,d}`:

1. exact triad prior;
2. triad plus physical line start;
3. triad plus preceding physical-group DY;
4. triad plus both coordinates.

Score held log2 loss.  Freeze predictions, then permute held outcomes inside
exact `triad × register` strata for 8,192 descriptive worlds and max-three
correction.  Also export raw and triad/register-matched train/test deltas.

This analysis may compress two selected formal operations into a common
physical-entry renderer.  It cannot predict an unseen triad or identify a
morpheme, POS, meaning, sound, language, plaintext, or translation.  No f84
row may be opened, parsed, retained, joined, or scored.
