# GDT229 — q13 provisional semantic-role lattice

## Purpose

GDT229 turns the complete GDT227 abstract interlinear into an explicit working
semantic lattice.  It is YOLO hypothesis generation, not confirmation.  The
question is not which Voynich word means a bath term; it is which *document
role bundles* remain plausible for each mechanically delimited field when the
readable recipe instrument, the readable *De balneis* record schema, and the
permitted q13 page geometry are considered together.

## Frozen inputs

- `gdt227_q13_abstract_interlinear.tsv`: 701 source-native q13 fields;
- `gdt224_field_role_projection.tsv`: externally trained CoReMA role
  probabilities based only on relative position and field extent;
- `gdt228_visual_feature_manifest.tsv`: page-level, human-catalogue-normalized
  visible geometry;
- `gdt211_de_balneis_entry_inventory.tsv`: readable bath-record role
  prevalence;
- the published GDT212 visual-to-readable-text calibration.

Every retained input is asserted to contain no f84 row before its content is
used.  GDT229 does not query a global transcription table.

## Lattice rules

The external five-way role likeness is mapped to broad document-role bundles:

| external likeness | leading latent bundle | mandatory alternatives |
|---|---|---|
| OPENER | identity/location/access header | case/indication header; generic record opening |
| OPERATION | practical description/indication | hydraulic description; procedure/caution |
| INGREDIENT or TOOL | material/case/quantity argument | component; local state; location |
| CLOSER | caution/outcome/formal close | generic renderer close |

Two page-level modifiers are allowed, and neither creates field ownership.
An explicit linear path raises `SETTING_OR_HYDRAULIC_DESCRIPTION` to the front
of the OPERATION alternatives because GDT212 found weak readable-manuscript
visual grounding for access/hydraulics.  Multiple bounded regions raise
`COMPONENT_PARAMETER_OR_LOCAL_STATE` to the front of the short-argument
alternatives because GDT228 found a weak, postselected page-level enrichment.

No PAGE_HOST identity changes a role assignment.  Exact strings are printed
only so that a human can use the lattice as an interlinear.  The same rule is
applied to all 701 fields.

## Interpretation discipline

The leading world is a hybrid therapeutic/balneological practical record with
hydraulic/setting description and short component/material/state values.  A
therapeutic-indication-list world, a hydraulic-apparatus-key world, and a
nonsemantic record-renderer world remain live alternatives.  World ranks are
abductive and explicitly post-hoc; they are not probabilities or test scores.

No field is assigned an English translation, and no PAGE_HOST is assigned a
lexeme, object, action, disease, material, body part, place, sound, language,
or plaintext value.
