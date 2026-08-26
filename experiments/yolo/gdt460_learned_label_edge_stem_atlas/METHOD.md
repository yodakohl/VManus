# GDT460 method

## Question

Are GDT459's 107 learned singleton labels really indivisible, or do they embed
portable functional prefix/suffix stems around learned object-name cores? Do
any remaining internal substrings recur on both pages of the same visible
content class?

## Inputs

- GDT407's 4,576 running events, used only to calibrate edge behavior.
- GDT413's unchanged component working dictionary.
- GDT459's 183-address interlinear; the target is exactly its 107 Tier-D
  learned labels on six already admitted pages.

## Method

### Functional edge stems

1. Build the invariant running surface→recipe table.
2. For every running surface of at least two characters, treat it separately
   as a candidate prefix and suffix.
3. Collect every other running surface extending that edge. Retain a
   direction-specific edge channel only if it has at least four extension
   types, its component recipe appears at the corresponding recipe edge in at
   least 90% of those types, and it touches at least one of the 107 labels.
4. For each learned label select the longest qualifying prefix, then the
   longest qualifying nonoverlapping suffix. Everything between them remains a
   learned owner-class name core.

This yields 27 channels over 24 surface stems: eight prefixes and nineteen
suffixes.

### Owner-class family stems

1. Enumerate every substring of length two through five once per learned label.
2. Retain substrings occurring in at least three labels, exclusively within one
   content class, and on both current pages of that class (`f71v`+`f72r` for
   stellar positions; `f88v`+`f89r` for drug/ingredient objects).
3. If a longer candidate has exactly the same occurrence set, retain the longer
   form. This leaves seventeen replicated family markers.

### Hybrid release

- `FULL_EDGE_FORMULA`: calibrated left and right edges cover the whole label.
- `FUNCTION_EDGE_PLUS_LEARNED_CORE`: at least one calibrated edge remains
  readable and the middle stays a learned name core.
- `OWNER_FAMILY_STEM_ONLY`: no functional edge, but a replicated class-family
  marker occurs.
- `WHOLE_LEARNED_LABEL`: no retained structure; memorize the complete label.

## Decision rule and claim ceiling

The edge value is inherited only from its direction-specific running-text
calibration; no value is inferred from the label's picture. A family marker may
receive only the visible class default `STERNSTELLENFAMILIE` or
`DROGENFAMILIE`, never an individual name. A middle string is not decomposed
merely because characters resemble known atoms.

This working atlas adds no core meaning, page or surface prediction and confirms
no lexeme or object identity. It supplies a prospective reading rule: read a
calibrated functional edge, preserve the name core, and memorize the whole form
when neither channel is licensed.
