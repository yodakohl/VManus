# GDT1160 — contextual historical abbreviation recovery

Status: CONTEXT_AND_NEURAL_INCREMENT. No Voynich text or image is an input.

See METHOD.md, SPEC.json and PREREGISTRATION.md. The fixed comparison is
frequency, layout, linear context and one small neural context architecture.
The source-ambiguity capacity receipt is in the production_origin_supply_20261003
proposal dossier. Previously exposed source labels are explicitly disclosed.

Use Python3.12 with NumPy1.26.4 and CPU PyTorch2.6.0. PyTorch's official CPU
wheel index is https://download.pytorch.org/whl/cpu; requirements.txt pins the
versions. No pretrained weights are used. The inference source is frozen before the first fit. Do not fit before the
public preregistration checkpoint recorded in artifacts/REGISTRATION_LOCK.json.

Reproduction uses src/run.py commands `prepare`, `selftest`, four `fit --fold N`
invocations for N=0,1,2,3, then `freeze` and `score`. Each fit saves both fixed
seeds and all candidate probabilities; it never evaluates held answers. Run
src/validate.py --release for independent result accounting; add --weights-dir
with the local NPZ directory for all24 forward replays. `--prepare` checks source
and invented fixtures before prediction artifacts exist. Existing fit outputs
are deliberately protected against overwrite: use a disposable reproduction
checkout and archive its generated PREDICTIONS_*, FIT_*, and PREDICTION_LOCK
artifacts before recomputation; retain REGISTRATION_LOCK and source files.
Local NPZ weights are working artifacts, not new scientific input. Public
source, dependency pins, seeds and probability outputs permit retraining and
independent result accounting without retaining large model binaries.

Result: REPORT.md; complete332-type table: CANDIDATE_TABLE.md. Source-control
macro accuracy68.315% frequency,68.857% layout,76.155% linear context,79.651%
neural context; no Voynich meaning is established.
