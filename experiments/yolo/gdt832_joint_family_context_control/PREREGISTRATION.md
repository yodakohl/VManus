# GDT832 prospective fit registration

This registration is published **after source preparation and capacity
inspection, before any decoder fit or recovery score**. Source capacity is
not claimed as a publicly preregistered result. `prepared/CAPACITY.json` retains
the initial four-mandatory-suffix STOP; `prepared/ACTIVE_RULE_CAPACITY.json`
documents the explicit pre-fit observational-domain correction. The latter
does not alter the text, split, output deck, recovery or improvement thresholds.

The question, exact algorithm, all candidate pools, source partitions, seeds,
four arms, pseudo controls and numerical criteria are fixed in METHOD.md,
src/SPEC.json and src/ENCODER_SPEC.json. PREREG_LOCK.json binds the actual
implementation and public fit inputs. Independent source validation and toy
software checks are completed before fitting. No source/score selection follows
fit outcomes. Truth keys remain excluded from fitting and from root inspection.

Outcomes are decided in the fixed order:

1. Source capacity stop, if final coverage prerequisites fail.
2. CONTROL_RECOVERY_FAIL, if FULL misses any registered reconstruction floor.
3. CONTROL_RECOVERED_NO_JOINT_GAIN, if reconstruction passes but FULL lacks
   the registered additional recovery over CUT or OFF.
4. JOINT_GAIN_WITH_ORDER_CONTROL_FAIL, if recovery/gain pass but held order
   evidence fails on real or pseudo data.
5. JOINT_CONTROL_RECOVERY_AND_GAIN_PASS, if all conditions pass.

These are control outcomes only. No result authorizes a Voynich target fit or
retuning of this experiment. Three keys share one historical content split.
Inactive parameters receive no reconstruction credit. The initial source
capacity failure and subsequent pre-fit correction remain part of the record.
