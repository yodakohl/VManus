# D02 oracle-blind attestation

Decoder: `D02_MDL_COMPONENTS`

I designed and implemented this decoder while inspecting only:

- `DECODER_CONTRACT.md`
- `DECODER_IMPLEMENTATION_API.md`
- `src/decoder_api.py`

I did not inspect or use any observation corpus, held corpus, world generator,
design/generator document, artifact, manifest, method document, work directory,
oracle, codebook, genealogy, other decoder (including D01), Voynich file, or
f84/f84r material. I did not execute this decoder on any corpus.

The implementation uses only the Python standard library. It fits every
vocabulary, threshold-dependent structure, component inventory, role profile,
record schema, and architecture hypothesis from the supplied `train_rows`.
Held rows contribute only their permitted observable surfaces, equality,
ordering, and record membership when applying that fitted model.

## Independent design

D02 minimizes a simple two-part description length: recurring edge strings are
accepted as productive components only when their saved surface encoding cost
exceeds lexicon and attachment costs across multiple residual hosts and training
seeds. Recurring internal strings that compress the training vocabulary but do
not pass the productive edge test become fossilized candidates. Residuals form
anonymous host clusters.

Separately, the decoder learns high-recurrence positional tokens, operator-like
boundary/middle roles, record boundary shapes, and repeating record schemas.
Held reference and relation candidates require an unambiguous nearest prior
match within the same visible record; scope claims require both a recurring
training schema and learned start/end shapes. Unsupported fields remain
`UNRESOLVED`.

All emitted cluster names are truncated cryptographic hashes of structural
features. They neither expose nor assign readable meanings to observed forms.
