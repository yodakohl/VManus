# Artifacts

SOURCE_VALIDATION.json reconstructs the fixed source capacity. TESTS.json records
17 invented integration checks. FIT_INPUTS.json accounts for discovery projections;
fits/ contains the 48 restart files and six selected files, all frozen by FIT_LOCK
before truth evaluation. RESULT.json records the six selected outcomes and the
predeclared STRICT_RECOVERY_FAIL decision. VALIDATION.json confirms independent
source, generation, fit selection, score, role and held-metric replay.

Confirmation source gold is stored once; the three separate world truth files
contain maps and provenance only. See prepared/GENERATION.json for all compressed
and decompressed byte commitments.

POSTHOC_ERROR_CENSUS.json separately counts existing restart mismatch classes
and attributes selected word errors. It does not alter the preregistered decision
or add fits, objective evaluations or selections.
