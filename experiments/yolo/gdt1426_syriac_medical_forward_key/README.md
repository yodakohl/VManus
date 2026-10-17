# GDT1426 — one Syriac medical key on a whole paragraph

Status: REGISTERED_UNSCORED.

See METHOD.md, PREREGISTRATION.md and src/SPEC.json. The source is HUNAYNNET’s fixed Syriac Hippocratic Aphorisms edition, not an invented medical lexicon. Its strict edited subset is a reference wordgraph, not complete grammar or an identified source. Source XML and derived data retain the project CC BY-NC-SA4.0 license; see SOURCE_NOTICE.txt.

Prepare source with src/source.py and validate_source.py; src/run.py --prepare constructs the unchanged IT59 input. After LOCK.json/publicregistration: src/run.py --gate; src/validate.py --gate; only a PASS permits src/run.py --native and src/validate.py --native. On stop, run.py --native writes a zero-native stop record. Final static replay: src/validate.py --validate. No automatic retries or new corpus/control.
