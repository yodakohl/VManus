# GDT953 — a complete purpose guess survives equality, but fails composition

The fixed whole-purpose model P leaves one common arrangement, R16, in the three
readings. Only IT2a has all28 literal labels known and gives a fully checked
equality-compatible arrangement. ZL3b and RF1b retain uncertainty. The stronger
component model C fails in every arrangement and every reading; at R16 none of
the11 recurrent source atoms has even one noncontradictory cached root unit.

| Reading | P contradicted /56 | P remaining | C remaining | Known labels / component views |
|---|---:|---|---:|---:|
| ZL3b |55|R16, unresolved|0|22 /22|
| IT2a |55|R16, equality-compatible|0|28 /26|
| RF1b |52|F08,F17,F21,R16, unresolved|0|23 /21|

All56x28 predictions were frozen and publicly committed as165d8c151 before fresh
target intake. The source selection was nevertheless motivated by the previously
known f69v.14/.18 `okeod` collision; this is not a blind discovery or a statistical
test of the historical source. The input retains all100 raw groups and84 cached
edition/locus records. There are58,968 pair consequences and30,184 atom/unit
checks, all retained rather than reporting only the promising arrangement.

## The actual candidate and its contradictions

R16 places source rows3 and7, both “to acquire every good”, at f69v.18 and.14.
It also places source row22, the explicit lacuna, at f69v.27. ZL/IT read a third
`okeod` there. Thus compatibility requires the unavailable source heading to agree
with the same meaning. We neither supply that missing heading nor count this
unresolved implication as supporting evidence. F08, which fits the first known
duplicate in forward order, fails ZL/IT because of that third `okeod`.

The complete conditional28-row reading, including the source lacuna and every
observed form, is in [REMAINING_P_READINGS.tsv](artifacts/REMAINING_P_READINGS.tsv).
It is an explicit source alignment, not an established translation. Examples of
what it predicts, with IT2a's fixed cached units:

| Required repeated meaning | Complete predicted forms | Observed consequence |
|---|---|---|
| ACQUIRE: good / enmity | `okeod` / `ykeydy` | `ok+od` and `ed` have no common unit |
| REMOVE: anger / fever and pain | `saral` / `oar alys` | `ar` and `o al+s` have no common unit |
| SEPARATE: lovers / man and woman | `oeesa` / `ykeey` | `oees` and `e` have no common unit |
| WELL_RECEIVED: rulers / general reception | `oteol` / `ytody` | `ot+ol` and `od` have no common unit |
| ILLNESS: make ill / heal the ill | `otody` / `okody` | Shared `od` also occurs at source3 “every good”, where this explicit atom must be absent |

All11 atoms and all three readings have small inspectable witnesses in
[R16_COMPONENT_WITNESSES.json](artifacts/R16_COMPONENT_WITNESSES.json).
The remaining RF arrangements fail the full component model too. Its few isolated
permitted units and its one anonymous unknown-only unit are not word readings.
No segmentation, synonym rule, prefix or error allowance was changed after intake.

## Decision and remaining ambiguity

Do not adopt `okeod = Gutes erlangen` as a working translation on this evidence.
It names a concrete weak hypothesis whose compositional extension has now failed.
P's one common rotation does not identify a language, a sound value or a
word-building rule. It allows an arbitrary whole-label codebook and relies on
the unfilled source22 implication; equal-word coincidences alone cannot distinguish
that from an unrelated register. Rows3/7 are semantically indistinguishable within
the chosen source. Catalogue order also remains a conditional assumption, not an
independently certified reading direction.

Close this fixed heading-plus-cached-unit model. Do not rescue it by changing
source edition, filling the lacuna, relaxing the11 atoms or substituting another
parser after the result. Other writing systems and other contents are not refuted.
The weaker whole-purpose alignment is retained for transparency, with its full
contradictions and uncertainties, and is not the selected next reading route.

All target observations belong to one previously exposed physical leaf. This
test has zero independent confirmation leaves, no appropriate null for the whole
source search and no independently bound meaning. Confirmed words remain zero.
No reserve, f84/f84r, f116v or new page was accessed.

## Reproduction and source

`src/prepare.py` replays only the28 declared loci through the selector-first guard;
`src/run.py` checks the immutable preregistration hashes and generates all results.
`src/explain.py` renders all P survivors and the small component witnesses.
The initial independent validator failed at target intake; its original bytes and
source-only receipt are preserved. The repaired validator actually reproduces all
results; see VALIDATOR_CORRECTION.md. The scored code and protocol stayed frozen. The
complete large component TSV is published as deterministic gzip; the validator
accepts it directly, and the runner regenerates its uncompressed bytes.
`artifacts/COMPONENT_STORAGE.json` binds both forms and their exact roundtrip.

Source: Pingree's1986 edition of *Picatrix Latinus*, IV.ix §§29–56, printed228–234,
[Warburg Institute](https://commons.warburg.sas.ac.uk/downloads/8g84mm241?locale=en).
Root read the entire passage and checked source pages229,230,233,234 natively.
The27 known purpose clauses and the lacuna are retained in src/SOURCE.json.
The modern PDF/image cache is not distributed. The source's purposes describe
historical intended effects, not demonstrated efficacy.
