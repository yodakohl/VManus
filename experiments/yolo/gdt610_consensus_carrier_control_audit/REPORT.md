# Consensus-coupled carrier decoder: final report

Status: **`CONSENSUS_STABILITY_INCREASES__WHOLE_WORD_KEY_STABLE_BUT_WRONG`**.

## Outcome

**FAIL — no concrete reading.** Coupling carrier maps inside the fit does raise
stability, but it also makes the entire synthetic whole-word category agree on
the wrong key. The planted control reaches only
33.7%
held character accuracy. Target words produced directly by W candidates are
therefore codebook injection, not translations.

The run used only the published 98-unit payload and independently hashed Latin,
Old Italian, and Middle High German references. The original scratch JSON had
the obsolete schema label `gdt605-historical-secretary-unit-sequences-v1`;
GDT610 corrects that inert label to the canonical GDT606 artifact. Deleting the
schema field makes both complete JSON payloads byte-identical.

## Frozen method

- Fixed target categories: 42 letter/homophone (L), 4 double (D), 34 syllable
  (S), 7 null (N), 11 whole-word (W).
- W anchors use standalone/boundary evidence, not positive frequency. The five
  nearly pure standalone forms `qokaN`, `qokEdy`, `qokaI`, `qokedy`, `qokEy`
  are all W anchors.
- Six deterministic leave-one-folio-block-out views jointly optimize their
  maps. After two independent warm-up sweeps, each coordinate move includes a
  reward for exact agreement with the modal output of the other views.
- Language objective: character 4-gram typicality plus a small reference
  word-length likelihood. It contains **no dictionary-match or word-frequency
  bonus**. Each stored non-null output additionally costs
  `(1 + output_length) × log2(27)` bits as codebook MDL.
- The positive coupling weight is chosen only on a planted Latin control. Its
  30,174 chunks reproduce the exact train/held chunk-length sequence; all 98
  units occur, rank-frequency Spearman is
  0.999885, and JS divergence is
  0.03432 bit.

## Synthetic calibration

| λ | all-six stable types | mean key types correct | held-weighted key correct | held character correct |
|---:|---:|---:|---:|---:|
| 0.00 | 37.8% | 67.5% | 62.9% | 31.6% |
| 0.03 | 46.9% | 72.1% | 64.8% | 32.5% |
| 0.10 | 81.6% | 77.6% | 67.2% | 33.7% |
| 0.30 | 76.5% | 65.1% | 59.3% | 28.9% |
| 1.00 | 92.9% | 56.8% | 55.1% | 26.5% |

The frozen choice is λ=0.10. It raises exact six-view stability from
37.8% to
81.6%,
but end-to-end held character recovery remains
33.7%.

The failure is sharply localized by category:

| category | types | all-six stable | mean oracle type accuracy | held-weighted oracle accuracy |
|:--|--:|--:|--:|--:|
| L | 42 | 38 | 92.5% | 92.9% |
| D | 4 | 4 | 100.0% | 100.0% |
| S | 34 | 20 | 77.0% | 67.9% |
| N | 7 | 7 | 100.0% | 100.0% |
| W | 11 | 11 | 0.0% | 0.0% |

All eleven W carriers are perfectly stable and all eleven are wrong:

| control unit | planted output | six-view output | stable | correct |
|:--|:--|:--|:--:|:--:|
| `C` | `in` | `omnibus` | yes | no |
| `E` | `atque` | `eorum` | yes | no |
| `S` | `ut` | `proelio` | yes | no |
| `aN` | `ad` | `atque` | yes | no |
| `al` | `qui` | `neque` | yes | no |
| `ar` | `et` | `caesar` | yes | no |
| `d` | `cum` | `castris` | yes | no |
| `o` | `quod` | `exercitum` | yes | no |
| `ok` | `se` | `propter` | yes | no |
| `ot` | `ex` | `quibus` | yes | no |
| `t` | `non` | `quod` | yes | no |

This is the clean bottleneck: typicality + MDL + consensus identifies a shared
pseudo-key, not the planted whole-word key. Syllables are the next weak point;
only 20/34 are stable in control, versus 38/42 letters, 4/4 doubles, and 7/7
nulls.

## Target behavior

| language | condition | all-six stable types | occurrence-weighted stable | real−destroyed bits/transition | post-hoc lexicon characters |
|:--|:--|--:|--:|--:|--:|
| latin | uncoupled | 19.4% | 18.6% | 0.3285 | 29.0% |
| latin | coupled | 33.7% | 27.1% | 0.3346 | 29.7% |
| old_italian | uncoupled | 13.3% | 15.4% | 0.2523 | 32.6% |
| old_italian | coupled | 31.6% | 25.8% | 0.2423 | 32.2% |
| middle_high_german | uncoupled | 19.4% | 19.9% | 0.2403 | 28.0% |
| middle_high_german | coupled | 36.7% | 25.4% | 0.2360 | 27.6% |

Coupling raises stability but does not improve held language evidence
consistently: Latin rises by about 0.0061 bit/transition, while Old Italian
falls by about 0.0100 and MHG falls by about 0.0043. The lexicon fraction is
post-hoc only and likewise falls for Old Italian and MHG.

Category stability after coupling:

| language | L | D | S | N | W |
|:--|--:|--:|--:|--:|--:|
| latin | 11/42 | 3/4 | 1/34 | 7/7 | 11/11 |
| old_italian | 11/42 | 4/4 | 0/34 | 7/7 | 9/11 |
| middle_high_german | 14/42 | 2/4 | 2/34 | 7/7 | 11/11 |

The coupled target therefore repeats the control pathology: W becomes almost
fully stable, while only 0--2 of 34 S mappings stabilize.

### Why the apparent words are not readings

Among coupled exact-reference fragment rows, direct W-candidate outputs account
for 1218 Latin,
781 Old
Italian, and 967
MHG rows. Those matches are tautological because every allowed W output came
from that language's reference list, even though membership did not enter the
score.

Only 8 coupled matches are composed entirely from non-W carriers;
all are Latin and reduce to repetitive forms rather than a coherent passage:

| language | folio | locus | chunk | units | output | categories | reference count |
|:--|:--|:--|--:|:--|:--|:--|--:|
| latin | f18 | f18v.8 | 0 | `ol ol` | `iiii` | DD | 7 |
| latin | f23 | f23r.1 | 8 | `ol ol` | `iiii` | DD | 7 |
| latin | f23 | f23r.8 | 4 | `ol ol` | `iiii` | DD | 7 |
| latin | f23 | f23v.11 | 2 | `ol ol` | `iiii` | DD | 7 |
| latin | f23 | f23v.8 | 6 | `ol ol` | `iiii` | DD | 7 |
| latin | f47 | f47r.2 | 1 | `Col Col` | `sese` | SS | 48 |
| latin | f85 | f85r2.1 | 27 | `C C` | `cccc` | DD | 1 |
| latin | f89 | f89v1.23 | 0 | `ol ol` | `iiii` | DD | 7 |

The complete coupled W assignments, included for audit rather than meaning,
are:

| language | carrier | modal output | support |
|:--|:--|:--|--:|
| latin | `Sol` | `exercitum` | 6/6 |
| latin | `daI` | `propter` | 6/6 |
| latin | `daN` | `omnibus` | 6/6 |
| latin | `okaN` | `eorum` | 6/6 |
| latin | `okal` | `proelio` | 6/6 |
| latin | `qokEdy` | `atque` | 6/6 |
| latin | `qokEy` | `neque` | 6/6 |
| latin | `qokaI` | `caesar` | 6/6 |
| latin | `qokaN` | `quod` | 6/6 |
| latin | `qokal` | `castris` | 6/6 |
| latin | `qokedy` | `quibus` | 6/6 |
| old_italian | `Sol` | `altro` | 6/6 |
| old_italian | `daI` | `perche` | 6/6 |
| old_italian | `daN` | `quando` | 6/6 |
| old_italian | `okaN` | `come` | 6/6 |
| old_italian | `okal` | `altra` | 5/6 |
| old_italian | `qokEdy` | `quella` | 5/6 |
| old_italian | `qokEy` | `per` | 6/6 |
| old_italian | `qokaI` | `che` | 6/6 |
| old_italian | `qokaN` | `non` | 6/6 |
| old_italian | `qokal` | `tutto` | 6/6 |
| old_italian | `qokedy` | `disse` | 6/6 |
| middle_high_german | `Sol` | `vrouuuen` | 6/6 |
| middle_high_german | `daI` | `ritter` | 6/6 |
| middle_high_german | `daN` | `sprach` | 6/6 |
| middle_high_german | `okaN` | `unde` | 6/6 |
| middle_high_german | `okal` | `uuas` | 6/6 |
| middle_high_german | `qokEdy` | `der` | 6/6 |
| middle_high_german | `qokEy` | `uuan` | 6/6 |
| middle_high_german | `qokaI` | `daz` | 6/6 |
| middle_high_german | `qokaN` | `und` | 6/6 |
| middle_high_german | `qokal` | `uuaere` | 6/6 |
| middle_high_german | `qokedy` | `niht` | 6/6 |

## Conclusion

The different decoder succeeds at its narrow engineering goal—carrier
consensus is inside optimization, and the synthetic calibration shows that it
recovers L/D/N reasonably well. It fails the scientific goal. W consensus is
demonstrably wrong under a known key; S remains non-identifiable; and no
non-W carrier-aligned held phrase emerges in Old Italian or MHG. The eight
Latin rows are `iiii`, `sese`, or `cccc`, not a reading.

The localized next requirement is not more consensus. It is independent
information capable of identifying W and S outputs (for example an external
crib or relation constraint) that also improves planted-control character
recovery. Without that, the target is LM-driven pseudotext.

## Reproduction and artifacts

Run from this directory with Python 3 (standard library only):

```sh
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/consensus_carrier_decoder.py \
  --unit-sequences UNIT_SEQUENCES_JSON \
  --reference-dir REFERENCE_CACHE \
  --output-dir .
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/audit_and_report.py --output-dir OUTPUT_DIR
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/validate.py
```

The full run took about 33 minutes on the current host. Complete mappings are
in `target_complete_mappings.tsv`; all 9,838 held chunks and twelve decodes per
language are in `held_decodes_*.tsv`; the 295,140 control decodes are in
`calibration_held_decodes.tsv`. `carrier_fragment_audit.tsv` labels direct W
injection separately from composed non-W matches.
