# GDT1002 — joint alternatives of five complete transport readings

See DECISION.md, METHOD.md and PREREGISTRATION.md. All ten pairs and the joint
five-paragraph system retain the entire old lexicon, grammar, raw text and
four semantic variants. No new source or word meaning is introduced.

Install requirements.txt in a Python environment. Run src/preflight.py for
synthetic checks, src/run.py --prepare only to reproduce the frozen panel and
predictions, src/run.py for all eleven systems, then src/validate.py.
If cvc5 is installed in a separate environment, preflight/validate accept
--cvc5-python EXECUTABLE. No environment path is a scientific input.
