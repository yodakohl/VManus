# GDT892 — joint paradigm reconstruction with latent script units

The authoritative complete specification is `src/SPEC.json`. This is the first
concrete architecture selected for the user's models5+3 on9September, not an
increase in old decoder restarts. Whole lexical stems and inflectional endings
must use one globally shared orthographic channel. No free root-name mapping is
allowed. Latin is a candidate source language, not an inferred manuscript fact.

The new data are explicit LatInfLexi paradigm cells/forms, supplemented by fixed
ITTB attested forms and feature/dependency templates. LatInfLexi excludes
medieval-specific vocabulary and is not a complete Latin grammar. This first
channel operates on normalized spelling rather than asserting pronunciation.

Primary predecessors602/605 and832–837 supplied known units/roles, learned BPE,
or a co-lemma bonus; they did not solve this latent prefix-free CV channel with
complete paradigm feature constraints. The global letter channel removes the
free interchangeability of equally inflected root codes. It does not guarantee
that the resulting observed-text solution is unique. GDT616 remains closed.

For codewords of length1or2, prefix-freeness makes segmentation a function of
one global set S of standalone initial characters: read one character if it is
in S, otherwise two. Thus an alphabet of20 raw characters has at most2^20 such
segmentation functions, before word-boundary, vocabulary and grammar constraints.
Unseen codewords/parameters may remain equivalent. Every surviving plaintext
must be retained until uniqueness is proved; search exhaustion is not a proof
of either uniqueness or incompatibility.

An independent generator supplies complete discovery/held Latin sentences under
one hidden code. Its source selector is frozen before cipher generation. Root
may prepare the public reference lexicon but does not open selected control
plaintext or key truth until a fit lock. Control success is tool evidence only.
A manuscript fit requires a separate frozen contract; no new Voynich page or
sealed source is accessed here. No large external lexicon is republished; URLs,
commits and hashes permit exact acquisition into a user-selected cache.

Design budget30minutes; first implementation/control budget90minutes including
publication. Exact syntax-template implementation must be frozen before fitting;
if incomplete, do not silently replace it by a lexical-only success criterion.

Access deviation during design: a filename-oriented rg search was incorrectly
allowed to search mixed TSV contents and returned existing f69/f70 text rows.
No such row is a model/control input; no sealed row was displayed. Future text
projection remains selector-first through the guarded tool. This deviation does
not enlarge admission or provide research evidence.

Pre-fit implementation amendment: codebook completion counts every member of S,
including unused single-character codes. Therefore |S| plus observed two-character
codes must not exceed27; the total available code space must also reach27. An
independent enumeration of actual small codebooks caught the omitted lower bound
before any cipher existed. Independent scanner validation now passes11 tests/153
invocations. The independently written encoder agrees on109668 word/vowel cases.
The control selector now enforces the already registered all-six-vowel held
component coverage and rejects complete MWT sentences before key generation.
