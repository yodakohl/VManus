# Frozen source annotation instructions

Read each assigned100-word source window completely in the complete work's context. Windows are mechanical source-word units, not sentences, paragraphs, independent events or Voynich equivalents. No keyword-only labels. Do not inspect another observer's annotations before freezing your packet. Read full context as needed from the same source; all four full sources are available, no target data authorized.

For every window record six values E (concept expressed), U (genuine ambiguity) or N (no expression after complete reading). Negation, quotation and hypothetical conditions still express their concepts. A physical occurrence in the world need not happen. Anaphora requires an identifiable antecedent and a locally written referring expression. Topic alone, implicit ambient air and necessary but unmentioned apparatus do not count. Do not carry headings across every subsequent window. A heading actually inside a window is written content.

E and U require a short exact local quote (at most12 whitespace words) and a reason. Quotations may identify a word rather than a full sentence; retain source spelling. For anaphora also give an antecedent window ID and short quote. For U say which actual ambiguity licenses it; do not mark every conceivable unmentioned object U. When clear contextual sense excludes a category, use N, even if its spelling resembles a category term. Observe historical asserted material identity, not modern chemical truth.

## Six categories

- WATER: ordinary physical water as historically asserted, including spring, mineral, sea, rain and meltwater. A source's mistaken physical conversion can still denote it. Wine, blood, urine, humours and other clearly distinct fluids are not automatically water. Named aqua-vitae, quintessence and herbal distillates are U only where their asserted ordinary-water identity is genuinely ambiguous; clearly different substance N, explicitly ordinary water/aqueous constituent E. This is not a string search for water/aqua.
- AIR: physical atmospheric/elemental air. Ordinary literal wind and ordinary inhaled/exhaled physical air qualify by denotation without the extra word air. Ambiguous physiological breath/pneuma/spirit is U; explicitly spiritual spirit N. Vapour, heat, cold and seasons do not automatically denote air.
- BASIN_ART: manufactured concave receiving/holding space with basin, open bowl or pool function. Conventional literal basin/bowl/pool naming suffices; no separate storage action required. A generic closed flask/glass/still or unspecified vessel is not automatically a basin. A bath event or establishment is not automatically its pool; genuine bath-place/pool ambiguity is U.
- PIPE_ART: manufactured hollow conduit/channel for conveying material. Literal pipe/tube/conduit denotation suffices without a separate flowing event. An aperture, ordinary container, solid stick, generic stem or process does not suffice.
- BASIN_NAT: broader natural receiving reservoir/chamber. Fixed conventional classes include natural pools, stomach, urinary bladder and gallbladder, plus explicitly identified fluid-receiving anatomical chambers. A separate storing event is unnecessary. Whole generic organs, heart, brain, uterus, head and body do not qualify merely by existing; explicit chamber/reservoir sense or antecedent can qualify. This deliberately broader functional category is not a literal translation of Becken.
- PIPE_NAT: natural physical conduit. Fixed conventional literal classes include veins, arteries, ducts, ureters, urethra, windpipe/trachea, oesophagus and individual intestines. No extra flow event required. Generic entrails, nerves, stems, organs or paths do not automatically qualify; explicit hollow-conduit denotation or bound reference can qualify. Mineral vein versus anatomical vein and untyped lumen/cavity ambiguity stays U when unresolved. Source assertions override modern anatomy: a source explicitly treating a nerve as a hollow conduit can express this category.

ART and NAT remain separate; uncertain origin may give U in both. No double token counting is needed: every row is presence/uncertainty, not mention frequency. The broader natural categories are a declared rival interpretation with a larger denotational scope. No post-count widening or narrowing.

## Packet schema and freeze

Write only your assigned artifact, with schema:

    {"observer":"A or B","reader":"assigned name","recorded_utc":"...",
     "prior_exposure":"honest description","complete_reading":true,
     "rows":[{"id":"GALEN:0001","values":{"WATER":"N","AIR":"N",
        "BASIN_ART":"N","PIPE_ART":"N","BASIN_NAT":"N","PIPE_NAT":"N"},
        "evidence":{}}]}

Each E/U category has evidence object {"quote":"exact local span","reason":"short reason"}; optional antecedent_id/antecedent_quote. N requires no quote but requires actual complete reading. You may draft manually in a script after reading; do not implement keyword, dictionary or model-generated automatic labeling. No source concept search substitutes for first complete reading. Supplementary missed-mention search can be logged after packet freeze; do not silently repair frozen rows.

Report assigned row coverage and unresolved interpretation issues only after the packet is frozen. Keep complete text local; public packets contain short evidence only. Other source windows may be read for context but cannot be silently added to your assigned ownership. f84/f84r and all Voynich reserve/target material remain closed in this source task.
