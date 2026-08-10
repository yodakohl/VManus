# LRG004 initial-family discovery calibration

Status: `CORRECTED_V3_TARGET_BLIND_SYNTHETIC_CALIBRATION`

LRG003 localizes most of the confirmed edge-profile projection to the
group-initial-family block. LRG004 may identify stable individual families only
after a simultaneous, target-blind calibration over all 24 official families.

Use the exact 2,767-row LRG001 B/P page-by-length panel and its fixed 288 label
quotas. For each physical folio and family, average within-cell differences in
initial-family frequency (manual labels minus prose), then average cells equally.
Average folios equally for the global effect. Test both signs.

Generate one deterministic 8,192-assignment fixed-quota label permutation within
every exact cell. For each assignment take the maximum absolute effect across
all 24 families. A family's FWER p-value is
`(1 + count(null_max >= abs(effect))) / 8193`.

A family registers only when all gates pass:

* max-statistic FWER p <= .01;
* absolute equal-folio effect >= .04;
* at least 10 of 13 folios have the global direction;
* signed B and P effects are each >= .02;
* signed odd and even effects are each >= .02;
* weaker/stronger signed-effect ratio is >= .35 for both B/P and odd/even;
* every leave-one-folio-out signed effect is >= .02;
* maximum absolute folio-effect concentration is <= .25.

Calibration contains 64 null worlds; distributed positive-full, positive-half,
negative-full, and two-family worlds; and ONE_FOLIO, ONE_SECTION, ONE_PARITY,
FOLIO_RANDOM_FAMILY, SECTION_OPPOSITION, PARITY_OPPOSITION, IDENTITY_ONLY,
PAGE_ONLY, and LENGTH_ONLY controls, eight worlds each. All intended planted
families must register in every distributed world; no adversarial or null world
may register any family. The two-family world must recover both planted signs.

V1 is preserved as a pretarget stop. Its negative plant could change family 1
by at most its roughly .08 base frequency and therefore could not cross the
simultaneous max-statistic null; v2 makes the negative fixture material by also
placing family 1 in 35% of matched prose controls. V1 also allowed five
one-section/one-parity/opposition worlds through when random unplanted strata
barely cleared the absolute .02 floor. V2 adds the symmetric .35 balance gate
above, matching the already calibrated LRG002 remedy. No real family identity
was opened and no target statistic, multiplicity correction, effect floor,
support, deletion, concentration, or other fixture changes.

V2 recovered all 40 intended planted families and rejected every control except
one nominal PARITY_OPPOSITION world. Audit showed that both opposition fixtures
were incorrectly positive for family 0 in one stratum but negative for a
different family 1 in the other. V3 corrects only those fixtures so family 0 is
positive on one side and negative on the other. This is a control-definition
repair, not a gate or target change; real family identities remain unopened.

Only a fully reconstructed calibration authorizes a separately frozen target.
A target may emit all 24 aggregate metrics and stable family codes, but no
member code, learned weight, row, form ranking, EVA spelling, sound, morpheme,
word, POS, name, identifier, meaning, plaintext, or translation.
