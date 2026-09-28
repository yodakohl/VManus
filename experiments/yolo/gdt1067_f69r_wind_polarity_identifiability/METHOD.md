# GDT1067 method

The frozen question, assumptions and decision rule are in
`PREREGISTRATION.md`. Inputs are the already published sixteen-position class
inventories in `experiments/semantic_assumptions/f69r_matthew_phase_qc/
SOURCE_AND_METHOD.md`; no manuscript transcription or image is read here.

Number the schematic positions 0–15 clockwise. Matthew principal positions
are multiples of four, collateral positions are odd, and unused positions
are 2 modulo 4. Voynich f69r's matched classes are respectively green
(2 modulo 4), blue (odd), and blank (multiples of four). A candidate mapping
is `j = (offset + handedness * i) mod 16`, with offset 0–15 and handedness
+1 or -1. Retain a mapping when all sixteen classes agree. The opposite
polarity mapping adds 8 to every output slot.

The runner writes all 32 comparisons and each exact mapping's opposite
partner. The validator reconstructs the two class strings independently,
checks all maps, checks partner involution, and rejects a corrupted result.
This only tests identifiability under the inherited geometrical analogy. It
does not give wind names, orientations, language or translated words.
