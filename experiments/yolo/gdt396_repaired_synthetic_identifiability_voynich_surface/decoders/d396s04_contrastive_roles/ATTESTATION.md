# GDT396 decoder attestation — d396s04_contrastive_roles

I designed this decoder in an isolated Sol context under the GDT396 blind
development boundary. I read only `AGENTS.md`; the public GDT396 `README.md`,
`METHOD.md`, `CLAIM_INTERFACE.md`, `DECODER_QUALIFICATION_SPEC.md`, and
`DECODER_EXECUTION_SPEC.md`; `src/decoder_api_v2.py` and
`src/observation_api.py`; and development observations loaded through that
observation API.

I did not inspect any GDT395 world design, generator, oracle, scorer, or report;
any GDT396 oracle, scorer, validator, corpus generator, surface mapping, salt,
protocol artifact, sibling decoder source/output, claim, or metric; repository
history; Voynich text/data; or `f84`/`f84r`. I did not score against truth or use
cross-channel event linkage. No subagent participated.

The method is train-only register-contrastive multi-resolution latent-role
discovery. It intersects recurrence with register, layout, position, boundary,
and neighboring-context distributions, and separately discovers recurrent
proper substrings. It is not a graph, topology, or MDL-component decoder. Its
architecture output includes `PRIMARY`, a five-signal `MULTI_CONSTRAINT`
variant, and a matched repetition-rate `SCALAR_BOTTLENECK` variant.

Development-only self-tests were run independently for `FREE_SURFACE` and
`VOYNICH_SURFACE`. The tests checked deterministic fit/decode behavior, exact
nine-table shape validation, legal raw morphology offsets, required candidate
set literals, ranked-output monotonicity and caps, and byte-identical model
serialization before and after decode. No qualification or confirmation packet
was opened.

Caveats: all class and subtype IDs are anonymous and carry no semantic gloss;
scope and relation labels are induced from distributional recurrence rather
than grounded meaning; morphology spans are heuristic surface analyses; the
two-atom normalization uses only the public channel specification; and world
architecture flags are conservative structural hypotheses, not semantic
interpretations or transferable Voynich claims.
