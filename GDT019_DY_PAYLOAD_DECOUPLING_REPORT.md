# GDT019 DY-payload continuation report

Status: **DY PAYLOAD NEXT STATE DECOUPLED AT TESTED RESOLUTION**

The presence of DY predicts the next formal state, but the tested payload
inside the DY-bearing group does not.  Across 2,344 post-DY boundaries and
84 held physical folios, no prefix, host, length, family-initial, exact-family, or
exact-host addition beats the position baseline after its parameter cost.

- `NEXT_STATE`: best raw addition `LONG_HOST` gains -22.116 bits; BIC-net -313.180 bits.
- `NEXT_Q`: best raw addition `HAS_CANDIDATE_CORE` gains +7.061 bits; BIC-net -15.329 bits.
- `NEXT_OT_LOCAL`: best raw addition `Q_FLAG` gains -3.316 bits; BIC-net -25.706 bits.
- `NEXT_DY`: best raw addition `Q_FLAG` gains +1.134 bits; BIC-net -21.256 bits.
- `NEXT_CARRIER`: best raw addition `LONG_HOST` gains +7.260 bits; BIC-net -15.129 bits.

The two largest raw binary gains are only about seven bits: candidate-core
presence for next-Q and long-host status for next-carrier.  Each needs four
additional binary parameters and loses after the approximately
22.39-bit BIC penalty, even before the ten-model
selector.  Exact host and exact family are substantially worse out of folio.

This suggests a layered generator: a DY checkpoint carries a local payload,
while DY itself—not the identity of that payload—licenses the next transition.
That is compatible with an abbreviated technical register in which content
and control are partly separated.  It is also compatible with a nonsemantic
templatic source process, so it is not meaning evidence by itself.

The result is limited to the tested low-capacity features and next-state
targets.  f84r was absent from the sole input and was not opened, retained,
joined, or scored.  No morpheme, word, syntax, sound, language, plaintext,
meaning, or translation is confirmed.
