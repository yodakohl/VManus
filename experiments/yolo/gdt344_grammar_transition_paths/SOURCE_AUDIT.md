# GDT344 source and capacity audit

Date: 2026-08-19

The target page whitelist comes only from the already published GDT340
Recipe/Pharma record inventory. Guarded pre-parse selection retains 2,694
GDT278 native events and the same 2,694 GDT327 atomic-tuple rows. The join is
one-to-one on `(page,locus,group_index)`.

The panel has 17 physical folios, 94 records, 349 fields, 298 physical lines,
31 coordinate states, and 827 exact atomic tuple IDs. Adjacent page order yields
2,660 transitions: 2,600 within records, 705 crossing field boundaries, 264
crossing physical lines, and 60 explicit record resets.

The exact predeclared transition representation has 1,292 observed signatures.
There are 368 signatures on at least two folios, 377 realized by at least two
distinct exact tuple pairs, and 358 satisfying both conditions. Thus abstract
path recurrence has testable capacity even though 2,373 exact tuple-pair types
are sparse and only 165 exact pair types recur across folios.

The readable comparator remains the six hash-frozen CoReMA collections: 1,136
complete records before the MATERIAL+OPERATION eligibility rule. Its editor
roles and normalized concept identities are evaluation/oracle data; words,
labels, and role names are not model inputs.

The GDT327/GDT278 sources contain no f84 row. The loaders nevertheless reject
every `f84*` selector before parsing. No other Voynich section is retained or
scored.
