# GDT1003 — joint transport worlds and shared word domains

This registered consequence test fixes the complete GDT993 lexicon, grammar,
world rules and four retained variants. It tests both remaining overlapping
GDT1002 pairs, all 190 existence/value queries, and up to 64 shared-value tuples
per pair. See DECISION.md, METHOD.md and PREREGISTRATION.md for scope and limits.
No word meaning is independently confirmed.

Install requirements.txt in a Python environment. Run src/preflight.py for
20 synthetic complete-program checks. Run src/run.py --prepare only to reproduce
the frozen query table, src/run.py for the target census, then src/validate.py.
If cvc5 is installed separately, preflight/validate accept --cvc5-python EXECUTABLE.
Environment paths are not scientific inputs. Public registration precedes target
execution; PREREG_LOCK.json binds the scientific sources and query population.
