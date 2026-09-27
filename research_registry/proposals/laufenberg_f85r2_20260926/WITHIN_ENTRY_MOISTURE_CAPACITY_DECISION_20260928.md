# Opposed-moisture within-entry idea: bounded capacity decision

2026-09-28. The proposed discriminator was to compare whether a putative
`ch=dry, sh=moist` code produces contradictory qualities within one Herbal
plant entry more often than a readable materia medica assigns opposite
qualities to one drug or its parts. GDT623/624 already document the strict
families and same-line one-bit pairs; GDT1057 fixes only first-320-character
qualities from detected numbered source entries. The route/registry duplicate
screen returned GDT623–625 and GDT810, and GDT624's primary edge table already
contains the strongest same-line examples.

A read-only capacity preflight reused GDT623's guarded 179-selector ZL3b
query, excluding f84/f84r and f1r before token materialization. Among Herbal
pages, strict `^qo(k|t)(ch|sh)(y|ey)$` occurs on 68 pages; 29 pages have two
or more codes, seven contain both CH and SH. Under the inherited broader
`^qo(k|t)(ch|sh)` prefix, 98 pages have a code; 68 have multiple codes and
15 contain both CH and SH. The seven exact opposed pages are f18v, f19r,
f25r, f28v, f44r, f44v and f94v. GDT624 had already recorded same-line
`qotchy/qotshy` on f19r.1 and f25r.3, and `qotchey/qotshey` on f28v.5.
These are one manuscript reading, not independent confirmations.

GDT1057's first-window table has 16 of 286 numbered starts with two or more
humidity words, but that does **not** mean 16 genuine dry-versus-moist drug
assertions: a repeated term, attributed opinion, patient condition or
preparation can produce the count. More decisively, a historical drug entry's
first 320 characters is not comparable to a full Voynich folio, whose text may
cover multiple drawings, parts or operations. Any page-level rate comparison
would confound unit length and ownership. The same-line target examples are
already known but have no independently readable part/condition owner.

Decision: do not register a larger within-entry meaning test on these inputs.
This preflight supplies location and capacity only, no new word or quality
confirmation. A useful reopening would require a repeated, singularly owned
plant/part/condition scope that lets both sides be counted in comparable
complete units. No reserved page, new Voynich page or sealed content was opened.
