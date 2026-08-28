# GDT603 — blind end-to-end Naibbe recovery

Status: **END_TO_END_NAIBBE_CONTROL_RECOVERED_AT_PUBLIC_CAPACITY**.

## Result

The capacity-saturated primary model reconstructs the control without the
published key, table, aligned plaintext, or internal token segmentation.

| U size | role | exact segmentation | boundary F1 | exact tokens | edit accuracy | key accuracy after exact segmentation |
|---:|---|---:|---:|---:|---:|---:|
| 138 | primary public capacity | 96.7409% | 96.6833% | 96.6949% | 95.6802% | 99.9685% |
| 132 | navigation | 96.9796% | 96.9225% | 96.9336% | 96.0164% | 99.9686% |
| 115 | navigation | 97.4571% | 97.4219% | 97.4341% | 96.6414% | 99.9844% |

The primary segmentation induces 138 U, 131 used P and 133 used S surfaces.
It gets the coarse U-versus-P+S state right on 96.8559% of 34,764 token
occurrences and finds an exact state plus cut on 96.7409%. On the 369 recovered
state-specific code types that intersect the true code inventory, 99.1870%
receive the right letter; occurrence-weighted covered-key accuracy is
99.9674%. The residual end-to-end error is therefore overwhelmingly a boundary
error rather than a key error.

The complete blind object was written before evaluation and has SHA-256
`3336202aec8fe8d6f7b15df588ebe99730db3f3d384cec0184fee6109fceefa1`.
The independent validator passes 26 checks over the source hashes, freeze,
metrics, all 16,800 token-map rows and every recovered-key row.

## Interpretation

This closes the missing step between GDT602's oracle-segmented key recovery and
a genuinely end-to-end control. A verbose homophonic P+S cipher can be broken
from token strings and language order when its architecture and capacities are
known.

It is not yet a Voynich solution. Naibbe is a modern generator, its exact
published key already fails on the f84-free target in GDT601, and the real
manuscript has not supplied independent evidence for three 138-entry states or
six homophones per letter. The justified next action is an unchanged target
falsifier with held physical folios, restart agreement, multiple historical
language models and order-destroying nulls. Any attractive line that does not
survive those comparisons is pseudo-language, not a reading.
