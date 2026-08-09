# DIRECTIONPLACEMENT001 target report

Date: 2026-08-09

## Result

**FINAL VALIDATED NONCONFIRMATION — zero of 13 frozen formal features passes.**

The registered target was invoked once after the source panel, 16 masked
pairs, feature representation, exact 65,536-swap null, thresholds, robustness
gates, and independent prescore validation were published.

No literal fragment, parsed-root form, or structural-role form passes the
complete gate. An independent nonimporting target implementation reconstructs
the target orientation, index 60,549, feature matrices, full family tails, all
six deletion orbits, every stored row and gate, the empty candidate table, and
the final decision in 16/16 checks.

## Closest diagnostic, not a result

The lowest adjusted familywise tail is shared by the formal structural atom
`ROLE_ATOM:BOUND_E` and its coextensive path
`ROLE_BIGRAM:BOUND_E+BARE`:

- length-adjusted familywise `p = 0.0989990234375` (required `<= .025`);
- raw familywise `p = 0.06640625` (required `<= .05`);
- east-minus-west raw effect `0.6875` in every reading;
- length-adjusted effects `0.545833` IT, `0.504167` RF, and `0.551786` ZL;
- the direction is positive on all six folios, including f68 and f88;
- all one-folio deletion familywise tails are between `0.121094` and
  `0.2890625` (required `<= .05`).

This is an honest near-miss because its direction and support are unusually
consistent, but it fails both primary significance gates and the deletion
gate by wide margins. `BOUND_E` is an existing structural category name, not
the letter E and not an English EAST word. It receives no gloss and must not
be promoted by lowering thresholds or dropping family/deletion correction.

## Interpretation

The fixed test does not establish recurrent morphology conditioned on whether
a human editor described a label east or west of an illustrated object. This
weakens a universal horizontal-placement marker hypothesis for the admitted
label systems. It does not prove that placement never matters, that labels do
not name objects, or that the text has no spatial vocabulary.

It supplies no EAST, WEST, direction, ownership, lexeme, plaintext, language,
or translation. Reopen only with genuinely new independent positional data or
a new author-visible falsifier—not a retuned feature set, threshold, subset,
pairing, or reuse of the same 57 annotations.

## Reproduction

The target runner is single-use and must not be invoked again. Validate the
existing immutable artifact with:

```bash
./vpy experiments/semantic_assumptions/directional_label_placement/validate_directional_label_target.py
```
