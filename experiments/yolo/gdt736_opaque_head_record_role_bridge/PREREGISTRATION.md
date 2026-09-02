# GDT736 design-fix note

This is an honest source-informed design record, not a blind preregistration.
The invalid four-Latin-initial model had already been rejected in GDT735, and
the initial H1/H2 versus H3/H4 placement difference was known before the
validator was written.

Before validation, GDT736 fixed these questions:

1. Does the entry/internal contrast survive all 24 bodies, all represented
   sections, a strict alternate-reader subset, and stratified controls?
2. Do the 24-body frequency vectors independently select a cross-pairing?
3. Does H1 separate from H2 at paragraph starts?
4. Do reader boundary splits support, contradict, or leave unresolved the
   secondary free-form proxy?
5. Can all 96 forms and all 24 inherited examples be rendered without the
   retired head nouns?

The primary failure conditions were disappearance of the location contrast
under body control, a different or nonunique strongest body-profile pairing,
inability to reproduce all 1,166 occurrences and 875 reader-exact aggregates,
or any output claiming a literal head lexeme, EVA letter/sound/Latin initial,
physical glyph shape, portable component meaning, new page, `f84`, or `f84r`.

The validator was implemented after these source decks and decisions were
fixed. It performs an independent artifact audit and a byte-identical temporary
builder replay.
