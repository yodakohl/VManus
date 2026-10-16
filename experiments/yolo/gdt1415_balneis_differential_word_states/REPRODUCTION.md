# Correct executable commands

The pre-lock README's validator example omits the required `--validate` flag. The scientific README/code/LOCK bytes remain unchanged. The manifest and commands below use the correct CLI; this documentation correction does not change any result.

    python3 experiments/yolo/gdt1415_balneis_differential_word_states/src/run.py
    python3 experiments/yolo/gdt1415_balneis_differential_word_states/src/validate.py --validate
    python3 experiments/yolo/gdt1415_balneis_differential_word_states/reproduce.py --isolated

Python3 and NumPy are required. The replay copies all exact LOCK inputs into a fresh temporary directory and compares CONTROLS, RESULT and VALIDATION byte for byte. The inherited source text, source-record metadata, normalized projections and complete native worksheet are all published inputs, not private runtime files. No test needs access to sealed pages or a hidden language model.
