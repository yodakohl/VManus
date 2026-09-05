# Replaying the completed control

The registered fitter and evaluator remain byte-frozen. On the completed-result
checkout, rebuild the ignored reference model and audit the published fits:

```sh
python experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py --reference experiments/yolo/gdt832_joint_family_context_control/prepared/reference.jsonl --families experiments/yolo/gdt832_joint_family_context_control/prepared/families.json --out experiments/yolo/gdt832_joint_family_context_control/runtime/reference_model
python experiments/yolo/gdt832_joint_family_context_control/src/run.py --check
python experiments/yolo/gdt832_joint_family_context_control/src/validate.py --data-dir experiments/yolo/gdt832_joint_family_context_control --model-dir experiments/yolo/gdt832_joint_family_context_control/runtime/reference_model --check
python experiments/yolo/gdt832_joint_family_context_control/src/summarize.py --check
```

For a fresh optimization replay, start with the preregistration commit
`8beefeec1db6a17e1e3e816159d622d617782d48` and run the fitter there. Existing locked
fits are deliberately not overwritten. Source regeneration follows METHOD.md;
the now-published truth files match the pre-fit commitments.

`src/post_result_audit.py` is explicitly post-result analysis. It counts letters
and errors of already fixed keys, without fitting or scoring replacement keys.
