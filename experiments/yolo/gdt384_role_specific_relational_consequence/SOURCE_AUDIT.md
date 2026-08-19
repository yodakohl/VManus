# GDT384 relational-gold source audit

## Included gold

### CoReMA

The frozen six-collection editor oracle provides element role, exact recipe and
element order, `parent_instruction_ordinal`, editor concept identity and
annotation flags.  Parent links are independent fields rather than relations
inferred from token proximity.  They support backward-reference, parented
scope, sibling-child and cross-context reuse tests.  They do not supply a
general COORDINATOR or FUNCTION_WORD gold label.

Source: repository-bound `gdt176_corema_role_oracle.tsv`, SHA-256
`170afc09327d7e2589107d1f4bd28f7725bfb8bcedcdd84bb9e7fb1c2c7f24ec`.

### PCEEC2

The exact GDT378 snapshot was independently reconstructed from public commit
`bf79d1c46e8ef983a7347b0664d0d80243f32831`.  Its 84 Penn-style parsed files
reproduce the frozen bundle SHA-256
`c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714`.
Constituent spans, attachment and POS remain hidden oracle material.  Only
derived relation booleans and scope lengths may enter GDT384 outputs.

Source: <https://github.com/beatrice57/pceec2>.

## Deliberately unsupported relation gold

Cambridge Curious Cures, the Harleian cookery texts and *The Book of Quinte
Essence* retain their frozen GDT378 lexical role oracles and composite
observations.  They have no bound constituent parse, coreference links,
operator scope, sibling attachment, or proposition-pair annotation.  Their
tokens and layout cannot be promoted to relation gold merely because an `and`,
`or`, `not`, `until`, or reference-like word is known.  They remain useful for
role-recovery diagnostics but not relation confirmation.

This restriction means several GDT384 consequences are necessarily
single-domain positive controls.  Every such result must be reported as a
capacity limitation even if its held collection folds pass.

## Independence statement

Relation membership is computed from hidden editor links or parse topology,
not from the role-label column and not from GDT383 role scores.  The observation
layer never exposes source words, POS, parse labels, editor roles, concepts or
parent links.  A dedicated source-only overlap audit can reject a relation even
when its hidden-gold derivation is valid.

No Voynich source or GDT381 target artifact was used in this audit.  f84 was not
opened, parsed, retained or scored.
