# GDT018 DY boundary-function test

GDT018 tests two competing formal functions for terminal `DY`:

1. **LOCAL_RESET**: the group after DY is distributed like a line-initial
   state;
2. **INTERNAL_TRANSITION**: DY predicts a distinctive continuation while the
   physical line remains active.

The experiment reads only `gdt016_group_state_inventory.tsv`, a frozen table
that contains no f84r row.  It does not open a transcription or visual source.

Every internal source-group boundary becomes one event with previous state,
next state, next-position quartile, and physical folio.  Four Dirichlet-1/2
categorical models are fit on all but one physical folio and scored on the
held folio:

- next state from position quartile;
- next state from position quartile plus previous-DY status;
- next state from position quartile plus the complete previous state;
- next state from the complete previous state.

The frozen 15-state alphabet is shared.  A four-model selector costs two bits.
A conservative BIC-style penalty is also reported for the 56 additional free
categorical parameters in the position-plus-DY model.

For the reset test, line-start and non-DY-internal next-state distributions are
learned on other folios.  Each held post-DY next state receives the log2
likelihood ratio `P(start)/P(non-DY internal)`.  Positive values support reset;
negative values support an internal continuation.  Jensen-Shannon distances
are descriptive full-corpus summaries only.

Claim ceiling: a transferable anonymous boundary-state function.  No
morpheme, word, syntax, sound, language, plaintext, meaning, or translation.
