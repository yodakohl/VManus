# GDT604 target contract

This contract was frozen before the target transcription was queried.

- Target rows are emitted only through `./vmanus-exp query-tsv` from the
  GDT327-derived explicit page allow-list; `--forbid-prefix f84` is mandatory.
- The split is by physical folio: first 23 by
  `sha256("gdt604-held-v1|" + folio)` held, the other 68 training.
- Dictionaries, cuts, keys, restarts and ranking use training folios only.
- Primary capacity is U/P/S=138/138/138. U=115 and 132 cannot override it.
- Reference languages are Latin, Old Italian and Middle High German, each
  paired with a chunk-order-destroyed model under the same renderer.
- Seeds are 11, 29 and 47, two restarts each, 50,000 iterations; held order has
  32 deterministic within-run null shuffles.
- A reading must pass all five gates in `METHOD.md` for exactly one language.
- Readable fragments, high order z or one favourable restart cannot override
  failed stability or real-versus-destroyed typicality.
- f84 and f84r are forbidden. No output resemblance alone licenses a word,
  sound, language, translation or meaning.
