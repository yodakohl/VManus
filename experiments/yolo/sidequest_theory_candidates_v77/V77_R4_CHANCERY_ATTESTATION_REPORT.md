# V77 R4 — chancery corrector: source-first exact-card attestation

## Verdict

`TWO_SIMPLE_PERIOD_ATTESTED_CATEGORIES_AS_EXPLORATORY_DEFAULTS`

The old dictionary was too elaborate. Of 24 frozen exact cards and 197
occurrences, R4 retains only two deliberately small **creative defaults**:

- `dcda95c81a5460feb191` → `ET?` — editorial German: **UND / AUCH?**;
- `b5fcea1eaed06b2f2291` → `PER?` — editorial German:
  **DURCH / GEMÄSS?**.

Both exact lexical categories occur in the genuine Florentine key *Cifra
Decemviri di Balia* of 1414. This satisfies the new historical vocabulary rule
at the level of dictionary granularity. It does **not** show that either
Voynich card has that value. The question marks are part of each entry.

Two other cards remain structural editorial labels, not words. The other 20
are `EXEMPLAR_VALUE_UNKNOWN`. None of the former sentence-sized values such as
“temperieren”, “bis die Flüssigkeit klar abläuft”, “Auffanggefäß” or
“Pflanzenmaterial zeitgebunden beschaffen” survives as a portable dictionary
word.

## Source-first inventory

Before comparing card contexts, I froze 50 visible entry↔code rows from four
genuine keys or key editions:

1. Gabriel de Lavinde, key 13, 1379 manual stratum: AAV Collect. 393,
   ff.166–181; exact entries include `Matrimonium=ln`, `pax=pR`, `guerra=pl`,
   `Sequaces sui=br`, and `Gentes armorum=gm`.
2. The Pisan-papal key between Dominico and Marco Canetoli, after 1412:
   Archivio di Stato di Bologna, Archivio Demaniale, PP. Min. Conv. di
   S. Francesco, Mazzo 237/4369; its exact nomenclator includes `scripsi=22`,
   `quia=23`, `non=24`, `litere=25`, `denarii=26`, `arma=27`, and `amici=28`.
3. Florence Fi1, 1414: Archivio di Stato di Firenze, *Chiavi delle cifre* II,
   Pars 3, Nr.1. The key has exactly three whole-word signs: `per`, `et`, and
   `che`.
4. Pisa Pi1, 7 November 1442: *Spedali, Opera della Spina, Memorie e
   documenti*, filza Nr.1895. Its seven frequent-word signs are `ihs`, `che`,
   `et`, `per`, `pre`, `pro`, and `pra`.

For signs not safely representable in Unicode, the inventory records their
unique facsimile-row locator instead of inventing a transcription. The complete
frozen list is in `V77_R4_SOURCE_FIRST_CODEBOOK_INVENTORY.tsv`.

Primary documentary edition: Aloys Meister, *Die Geheimschrift im Dienste der
päpstlichen Kurie* (1906), pp.23 and 173, public-domain scan:
https://archive.org/download/diegeheimschrift00meis/diegeheimschrift00meis.pdf

Florence/Pisa documentary edition: Aloys Meister, *Die Anfänge der modernen
diplomatischen Geheimschrift* (1902), pp.49–50 and 58–59:
https://books.google.com/books?id=8-Ux0geGhPIC

Independent structural check: Judit W. Somogyi, “Caratteristiche strutturali
di cifrari monoalfabetici italiani nei secoli XIV e XV,” *Verbum* 2016,
pp.195–217:
https://www.epa.oszk.hu/05200/05289/00028/pdf/EPA05289_verbum_2016_1-2_195-217.pdf

## Why `ET?` survives R4

The `dcda…` card occurs 19 times on f10r, f81v, and f83r. It is usually medial
and twice forms a visible `A – dcda – B – dcda – C` chain. It also occurs at a
field edge or alone, which is compatible with an additive continuation such as
“and/also,” though not diagnostic of it. The atomic `ET?` reading costs less
than the old long gloss “link the active working state” and is directly a
whole-word category in Fi1.

This is an explicitly exploratory reassignment. A generic continuation marker,
list separator, or nonlexical link remains equally possible.

## Why `PER?` survives R4

The `b5fcea…` card occurs nine times. Seven occurrences begin a field. Of the
two exceptions, one is the last card before a physical-line break and the same
exact card restarts the continuing statement on the next line. The remaining
exception precedes a terminal card. A minimal relation such as “through/by/in
accordance with” is therefore a coherent instruction-entry default, and `per`
is an exact whole-word entry in Fi1.

This is weaker than `ET?`: the contexts do not select Latin, do not establish a
preposition, and do not decide among “through,” “by,” “for,” or a purely formal
entry prompt.

## False-friend audit

- `scripsi=22` is real in the after-1412 key, but terminal Voynich cards are
  split among several exact families; assigning all of them “I wrote/finished”
  would simply rename the closure confound.
- `non=24` and `quia=23` are real, but no frozen card supplies an invariant
  exclusion or causal environment on these ten pages.
- `pax`, `guerra`, and `Matrimonium` are genuine codebook words, but the images
  and card contexts do not independently anchor peace, war, or marriage.
- `che` is frequent in period keys, but frequency alone cannot choose a
  complementizer.
- Similar-looking EVA strings and historical code signs were never compared.

## Coverage and ceiling

The mechanical audit covers exactly the central target freeze:

- 24 anonymous exact cards;
- 197/197 occurrences;
- 50 source-first historical entries;
- 2 exploratory codebook-attested categories;
- 2 formal nonword labels;
- 20 unknown exemplar values;
- 0 f84/f84r rows.

`V77_R4_VALIDATION.json` is `PASS`. The two retained rows license only a
historically plausible **size and kind of dictionary entry**. They do not
license language, sound, plaintext, word segmentation, or translation.

## R4 working rule for V78

Use `ET?` and `PER?` literally and minimally wherever their exact card occurs.
Do not expand them into medical or technical clauses. Put all remaining local
content in visibly bracketed owner/exemplar expansions. If either tiny default
makes a full occurrence incoherent in the next round, withdraw it rather than
adding senses.
