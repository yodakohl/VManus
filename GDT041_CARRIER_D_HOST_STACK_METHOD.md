# GDT041 — carrier+D host-stack atlas

## Question

Is GDT040's `[carrier]+[d]+AIIN` construction specific to AIIN, or is it one
member of a broader Currier-B rule allowing literal `d` between a
`ch/che/sh` carrier and many residual hosts?

This is a surface/formal construction test. No function or meaning is assigned.

## Decomposition

For every strict-consensus GDT016 group, `outer_carrier=1` iff the frozen outer
wrapper is `ch`, `che`, or `sh`. If such a group's residual begins with
literal `d`, that `d` is removed once to define its comparison base and
`inner_d=1`. A noncarrier frozen `d|HOST` group supplies the corresponding
inner-D/no-carrier cell. Other groups retain their residual host and have
`inner_d=0`.

Base `y` is excluded before scoring because `ch/che/sh + dy` overlaps the
separately established right-edge DY construction and cannot identify an
internal-D operation. No other host is excluded by outcome.

## Tests

Compatibility is tested separately in Herbal-B, S/B, Herbal-A, other
registers, and pooled HB+S/B. Within every exact base-host × physical-folio
stratum, inner-D assignments are permuted among occurrences while carrier and
D margins remain fixed. The exact hypergeometric distributions are convolved.

The atlas retains all doubly occupied carrier+D hosts and their register and
folio support. Cross-section host overlap is descriptive. Leave-one-folio-out
and leave-one-base-host-out minimum excesses are required to remain positive
for the pooled Currier-B claim.

## Decision

The construction is broader than AIIN if multiple base hosts recur in the
double cell across HB and S/B, pooled compatibility is positive under the
host×folio control, and deleting any one folio or base host does not remove
the excess. Herbal-A and other registers are explicit comparators.

This can establish an HB/S-shared, potentially S-enriched constructional
permission/prohibition. It does not by itself establish a universal Currier-B
rule. It
cannot establish a morpheme, POS, sound, language, plaintext, meaning, or
translation. f84r remains sealed.
