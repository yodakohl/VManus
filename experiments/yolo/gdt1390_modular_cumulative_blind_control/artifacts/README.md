# Artifact roles

- `MODELS`, `SHAPE`, `SOURCE_*`: fixed numerical models and public source pins.
- `MODEL_VALIDATION`, `SHAPE_VALIDATION`, `VALIDATOR_CONTROLS`,
  `ENGINE_VALIDATION`: independent numerical and source checks.
- `PROTOCOL_REVIEW`, `ENGINE_REVIEW`: prospective reviews.
- `BENCHMARK`, `GO_RECORD`: outcome-blind runtime selection.
- `CASES`, `RECOVERY_INPUT_LOCK`: anonymous public search input and its seal.
- `RESTARTS`, `RECOVERY`, `RECOVERY_LOCK`: complete fixed search output before
  truth was released.
- `UNBLIND_RECEIPT`, `TRUTH`: timed release of the artificial control sources,
  keys and generator seed. These are not manuscript translations.
- `RESULT`, `VALIDATION`, `RESULT_REVIEW`, `REVIEW`: primary result, independent
  checks, scope review and registry assessment.

No raw full language corpus, private credential or machine-specific path is
included. Models and short control fragments are reproducible from the pinned
public inputs; source attributions are retained separately.
