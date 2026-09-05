# GDT828 method

Audit the GDT827 MANUAL hypothesis under two fixed immediate nominal-complement
directions. The source packet is hash-bound and already admitted: four windows,
50 loci, 150 alternate reader lines. See PREREGISTRATION.md and src/SPEC.json.

The runner retains every exact chedy, both immediate neighbours, original
group IDs, separators and native paragraph flags. Fixed candidate types are
not decoded POS. Nominals/pronouns are type-compatible only, commands/relations
conflict with the imposed nominal slot, and unknowns remain unresolved.
Source lines are observation windows, not decoded clauses. No entity cleanup,
word splitting, ellipsis or meaning changes are allowed.

Two independent exposed reviewers examine source fidelity and the scope of the
grammatical inference. Their full notes are retained. A third agent implements
the validator without reading/importing the runner; it independently reconstructs
the complete expected table and tests negative mutations. Validation establishes
accounting correctness, not truth of the semantic or syntactic assumptions.

This continues GDT827's specific type conflict. The route-check's GDT575/GDT577
hits are historical renderer attachments; they provide no independent meaning
or attachment evidence here. Closed language/POS and image-semantics families
are not reopened. No GDT388 score-ready relation packet is claimed.

Reproduction:

```sh
python3 experiments/yolo/gdt828_manual_attachment_type_audit/src/run.py --check
python3 experiments/yolo/gdt828_manual_attachment_type_audit/src/validate.py --check
```
