# GDT466 — the mixed dictionary is now executable

## Result

The 107-label codebook now has one deterministic intake order:

> exact label → calibrated function shell → matching owner family → learned
> owner-class whole name.

It contains 44 general function channels and eighteen owner-family markers.
All 107 known labels replay exactly. When exact identity is hidden, the general
channels reproduce the complete function mask of 105 labels. The only two
partial cases are the intended exact-package cards:

- `ykyd`: the general `yky=Y+K+Y` prefix survives, while final `d=HIER` belongs
  to the known complete card;
- `yddy`: its `Y+D_ADDR+Y` value is licensed as one overlapping whole package,
  not as a free edge rule.

Those two are read correctly in production because exact known labels have
first precedence. Cold replay produces no extra function character anywhere.

## The reader survives changed name cores

Each of the 89 labels with at least one learned character receives one
synthetic `x` inside its name core. The exact form is therefore absent, but all
old function substrings remain visible. The intake reader recovers the expected
function mask in 89/89 cases.

For example, unseen synthetic `otxainy` reads:

`DANACH · [STERNSTELLENNAME:x] · ANTEIL · POSTEN`

The result comes from the general `ot` prefix and `ainy` suffix, not from an
exact label card. The `x` is only a probe marker and predicts no manuscript
spelling.

All 44 individual function-channel probes pass. All eighteen family markers
match in their own class and are blocked in the wrong class. A surface with no
match, `zxqv`, safely becomes `[PFLANZENNAME:zxqv]`. Thus no sequence is left
without a default, but an opaque default is never disguised as a translated
word.

## One real consistency correction

Compiling every accepted rule exposed one missed propagation from GDT462.
`ararchodaiin` already contained internal `ar=AUSGANG` and terminal
`daiin=AIIN=WERT`, but its initial `ar` had remained inside the learned name
despite the later accepted general prefix `ar=AR`.

The corrected reading is:

`AUSGANG · AUSGANG · [DROGENNAME:cho] · WERT`

Its known function count rises from 7/12 to 9/12. The complete dictionary rises
from 440 to 442 of 713 function characters; its architecture remains eighteen
full formulas, 87 shell/name hybrids, one family-only label and one whole label
(`oiil`). This is propagation of an existing value, not a new interpretation.

## Practical contract

```bash
python3 experiments/yolo/gdt466_future_address_mixed_dictionary_intake/src/read_address.py \
  SURFACE CONTENT_CLASS
```

Accepted content classes are stellar position, drug/ingredient object,
bath/outlet station, pictured plant, and unknown local address. The command
returns JSON containing the selected route, function channels, learned
character count, family markers, ordered recipe and German working reading.

Validation passes 77/77 checks with a byte-identical rebuild. No new page,
component meaning, individual object identity, surface prediction, plaintext,
language or confirmed lexeme is added.
