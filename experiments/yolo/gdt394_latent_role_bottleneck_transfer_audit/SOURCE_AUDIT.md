# GDT394 source audit

GDT394 uses only already published comparator artifacts.

* GDT382 oracle-blind observation layer, SHA-256
  `4c20dc0dd234f9b1947ce9c81d9d1c8645e30a1fd81321b6a9be755b3d229896`.
* GDT385 retained CoReMA predictions, SHA-256
  `319cb3a4a4288bc78d334cb74770651a0a71bbfadeb37cb12b1651619ff57526`.
  Only `CMP_PARENT_02` is the role route under audit; the readable calibration
  name is not inherited.
* GDT387 retained hidden governor oracle, SHA-256
  `67adc844f12dfdc4828d07d191d0a14e93080507126e135a2b72b1adb864ca8b`.
* GDT387 retained predictions, SHA-256
  `319311d4dcc940ae504ba550acbf050c1079a23b77b558b3938695433afa788f`.

CoReMA's outcome is an explicit editor parent-instruction link. PCEEC2's
outcome is the exact governor produced by the already frozen constituency head
rule. Both outcomes are readable-comparator gold used only for evaluation and
training of the explicitly labeled supervised control.

The source representation is deterministic and contains the information from
which every tested bottleneck is computed. This audit therefore makes no
conditional-information claim. It tests relative compression at a matched
one-dimensional budget.

The inputs contain no Voynich rows. `f84` and `f84r` are sealed explicitly in
the manifest and are absent by source construction.
