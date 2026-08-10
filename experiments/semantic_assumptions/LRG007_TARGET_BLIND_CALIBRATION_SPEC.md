# LRG007 target-blind A/D edge-transfer calibration

Status: `FROZEN_TARGET_FREE_CALIBRATION_V1`

The target feature is the fixed three-state initial-family contrast: A=`+1`,
D=`-1`, every other family=`0`. This avoids pretending that mutually exclusive
A and D indicators are independent. The two primary channels are
FIRST-minus-CORE and LAST-minus-CORE within each exact page-by-length cell,
then equal-cell within folio and equal-folio across all 16 folios. Separate A
enrichment and D depletion contributions remain mandatory robustness gates.

The 8,192-assignment null independently permutes the complete three-state row
vector within each cell, preserving exact A/D/other margins and exclusivity.
Inference is one-sided in the direction already fixed by LRG002+LRG004 and
uses the maximum standardized null over both channels.

Each channel requires familywise p<=.01, z>=3, effect>=.08, at least 12/16
positive folios, signed B and P effects>=.04 with ratio>=.25, signed odd and
even effects>=.04 with ratio>=.35, every folio deletion>=.04, concentration
<=.30, and separate A-enrichment and D-depletion contributions>=.015. Both
channels must pass.

Use only the opaque capacity panel and exact per-cell margins. Require 0/64
null passes, 8/8 full and 8/8 reduced distributed plants, and 0/8 in each
first-only, last-only, one-folio, one-section, one-parity, folio-random,
opposite-edge, and direction-reversed control. Missing rows, margin drift,
nonfinite values, or null-hash drift hard-stop.

A pass authorizes only a separately registered, hash-frozen one-time target.
Calibration supplies no prose-edge association, opening, closing, word,
function, meaning, plaintext, or translation.
