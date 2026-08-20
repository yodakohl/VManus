# GDT395 blind decoder implementation API

This file specifies mechanics only; `DECODER_CONTRACT.md` defines the
scientific observation boundary.

Each decoder module exports:

```python
DECODER_META: dict
def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]
def classify_world(train_rows: list[dict]) -> dict
```

The decoder must use only the Python standard library. It receives training
observation rows from corpus seeds 0–14 and one untouched held seed from
15–19. It never receives oracle rows. Learned vocabularies, thresholds,
components, clusters, and context tables must be fit from `train_rows` only.

`DECODER_META` contains `decoder_id`, `designer_model`, `method_family`,
`oracle_blind`, and `supported_representations`. `oracle_blind` must be true.

`decode` returns exactly one row per held event using the event-claim fields in
`decoder_api.py`. Every row must repeat the requested representation and
decoder ID. Unsupported predictions are `UNRESOLVED`. Confidence is a float in
`[0,1]` and cannot be fitted to truth.

`classify_world` returns `decoder_id, architecture_cluster, language_like,
notation_like, codebook_like, semantics_light_like, confidence`. These are
blind structural hypotheses, not readable family labels.
