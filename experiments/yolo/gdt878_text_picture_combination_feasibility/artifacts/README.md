# Artifacts

Root supplies `SOURCES.json`, `ROOT_OBSERVATION.json`, and
`GEOMETRY_B_OBSERVATION.json` locally. They may reference runtime image bytes;
the image bytes are not copied or published here. `run.py` writes a compact
`RUN_PACKAGE.json`, and `validate.py` writes `VALIDATION.json` when root binds
the final packets. These artifacts record feasibility and contract checks only.
