# W03: Engineered Catalogue Code

W03 is a deliberately clean catalogue and stock-indexing control.  Its hidden
world is a mutable inventory of 48 products, 6 product classes, 12 storage
locations, 24 lots, and 10 suppliers.  Completed records instantiate one of
eight fixed schemas: catalogue declaration, receipt, issue, transfer, recount,
reservation, return, or cross-reference.  Receipt, issue, transfer, recount,
reservation, and return records execute auditable state transitions over each
product's on-hand quantity, reserved quantity, location, and derived stock
status.  Cross-reference records connect products by substitution, bundle, or
supersession relations.  References normally point to the most recent earlier
event for the relevant product; record frames are explicit scope operators.

## Code construction

The system is an engineered code rather than a substitution cipher.  Each
atomic catalogue entity or function is assigned a deterministic five-symbol
codeword: a class digit, two within-class serial digits, a parity digit, and a
check digit over a 14-symbol alphabet.  Four common entities occupy a reserved
exception bank, modeling intentional legacy aliases without historical sound
change.  A field may carry one atomic codeword or a compositional operator and
argument.  Compositional fields take two payload symbols from the operator,
two from the argument, and recompute a checksum, so their visible group cannot
be decoded as a simple lexical substitution.  The oracle retains all current
components.

Three registers apply deterministic format transforms.  R0 preserves the
canonical payload, R1 rotates it and may suppress the checksum on a repeated
reference, and R2 reverses the payload and adds a guard symbol to state-changing
operators.  Line-final fields swap two positions.  Two hands use different
bijections of the same alphabet.  These transformations preserve a median
group length near five while producing controlled positional, register, and
hand variation.  The source code, codebook rules, and ordered engineering
genealogy make every realization exactly reconstructible after unblinding.

## Layout and adversarial purpose

Records contain 8--14 events and are laid out in physical lines of 4--9 groups.
Pages contain eight records and paragraphs two records.  Packed operator fields,
compact repeated references, and selected JOIN/SPACE alternations create
ambiguous visible boundaries; FIELD, LINE, RECORD, PARAGRAPH, and PAGE breaks
remain hierarchical.  Product and schema choice are intentionally skewed, so
the carrier has realistic recurrence despite the code's clean construction.

W03 is the engineered member of `PAIR_CODEBOOK`, with carrier profile
`CARRIER_CODEBOOK_MATCHED`.  Its confound is that strong recurrence, scoped
relations, state transitions, register differentiation, and boundary ambiguity
can all arise from an intentionally designed catalogue code without organic
linguistic evolution.
