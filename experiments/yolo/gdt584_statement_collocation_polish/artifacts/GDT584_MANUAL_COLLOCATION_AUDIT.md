# GDT584 manual collocation audit

Three independent passes inspected the frozen GDT583 edition before the
renderer was changed.

## Direction and process pass

All 25 warm/cool/dry cases, 51 grade-T cases and 13 form-T cases were read with
their complete statement context. Verdict for the 25 directional cases: two
already read well, 21 retained their meaning but required grammatical
rephrasing, and two required narrower meanings.

- Keep all ten warm readings and explicitly realize the following SH as warm
  holding when it is a hold voice.
- Keep eleven of twelve cool readings. `G407-E3488` has only AR at T and becomes
  outlet-side regulation.
- Keep drying only at `G407-E4476` and `G407-E4490`, where the following CHD is
  itself a fixed-charge grind. `G407-E4570` has AIIN at CHD and becomes liquid
  tempering plus broad processing.
- Keep all 51 grade meanings but remove the duplicated words “auf den Grad”
  from the action gloss.
- Keep all 13 form/stage meanings but put O and IIN into the natural German
  verb frame. `G407-E0297` explicitly says to bring the charge into preparation
  form and then set the processing stage.

## Material-practice pass

The 145 fine material readings were read with direct arguments, full remote
hosts and adjacent wet/dry operations. The working priority became immediate
wet process, then direct governor, then full remote governor, then fallback.

- `G407-E3903`, `G407-E4069` and `G407-E4407`: sieve → strain after a wet step.
- `G407-E4226`: strain → sieve because direct AIN outranks remote AIIN without
  a wet predecessor.
- `G515-E0243@4`: sieve → stage-conditioned broad separation.
- `G407-E0688`, `E0718`, `E4207`, `E4485` and `G515-E0183`: wet
  trituration/maceration rather than dry grinding.
- `G407-E0727`, `E4166`, `E4403`, `E4566` and `G515-E0245`: broad CHD →
  trituration/maceration of a charge in an extract.
- Eight SH fallbacks immediately before straining become standing/settling;
  two S fallbacks immediately after wet work become taking off.
- Five OR-only SH soak readings become material-unit holding so that a Pharma
  vessel is not literally “soaked”.

## Whole-statement editing pass

All 591 affected statements were scanned and forty difficult statements were
read manually. The selection spans all five registers and all 29 old rule
families; its exact IDs and before/after excerpts are published in
`gdt584_40_statement_review_deck.tsv`.

The pass found that most bad collocations were renderer failures rather than
bad meanings:

- 1,149 detached action-host fragments in 327 statements;
- 1,761 lowercase sentence starts in 424 statements;
- 62 fine arguments split from their licensing action;
- 360-like repeated-argument cases across the running/local review universe;
- embedded object and grade nouns in T and SH action glosses;
- 106 inherited statements over 100 words, including 37 over 200.

The remedy is statement-wide composition by exact `primary_governor_key`, not
automatic pronoun borrowing. Separate action heads retain separate argument
packages; repeated identical arguments are suppressed only within one reader
phrase and remain exact in the slot trace. OT and DY provide paragraph breaks.

## Final disposition

Manual spot checks after generation confirmed the named directional and
material cases, the complete remote `G407-E0360` host, the five-register
passage deck, and the absence of the old `beim …` fragments. The output remains
an exploratory working reading, not recovered plaintext.
