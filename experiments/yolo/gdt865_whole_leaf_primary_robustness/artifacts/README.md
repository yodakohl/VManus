# Compact reproducible artifacts

RESULT and VALIDATION contain the decision and independent audit. BASELINE and
LEAF_PREDICTIONS retain paired full rows. EVENT_METADATA contains source identity
and original feature hashes/counts. FOLDS contains counts, test IDs and ordered
training membership hashes, reconstructible from event metadata. METRICS includes
all eight score channels and paired per-carrier changes; LEAF_DELETE_RANGES keeps
all descriptive deletion calculations. GUARD_REQUESTS and SOURCE_HASHES preserve
source projection provenance. Normalized line/token projection hashes are recorded
by the runner; the validator independently rechecks the published prediction and
atlas projection hashes. Full feature arrays are rebuilt under ignored runtime.
