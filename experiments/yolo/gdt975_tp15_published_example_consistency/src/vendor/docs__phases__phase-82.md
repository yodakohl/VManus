# Phase 82: Decode Trace

[← Back to Phase Index](README.md)

## Purpose

Reviewer Response v1 (Reviewer 3.8): produce a complete, reproducible trace of the decoding pipeline from raw EVA through to decoded Latin syllables, so that any reader can follow the full chain without re-running the code. Reviewer 3.8 asked for more transparency on how a given EVA token becomes a given Latin reading.

## Method

For each of the Table 5 word-level identifications, record:
- Original EVA token
- Stroke-triple decomposition
- Triple → syllable assignment (with source: T_P15 confirmed, CVC coda, modifier, or wildcard)
- Assembled syllables
- Final decoded string
- Dictionary match (with edit distance if non-exact)

The trace is also applied to two full passages: f54r (104 tokens) and f57v (175 tokens).

## Results

All Table 5 identifications are traced end-to-end, including:
- `chedy → cora` (CVC decode)
- `daiin → din`
- `qokeedy → berara`
- full walkthrough of `ch → co`, `ed → ra` decomposition

Both passages output the EVA source aligned with the decode, showing identified and unidentified tokens in context.

**Verdict: PIPELINE_TRACED** — the decode is fully reproducible from first principles.

## Interpretation

This phase is a documentation artifact, not a test. It produces a machine-readable record that serves as the audit trail for reviewers and future research. The output JSON can be consumed directly by downstream tooling to regenerate the paper's worked examples.

## Files

- **Implementation:** [src/voynich/phases/p82_decode_trace.py](../../src/voynich/phases/p82_decode_trace.py)
- **Output:** `results/p82_decode_trace.json`
- **CLI:** `voynich decode-trace` / `voynich phase82`

## Dependencies

- `results/combined_refine.json`
