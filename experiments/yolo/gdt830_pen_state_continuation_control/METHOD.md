# GDT830 method

PREREGISTRATION.md and src/SPEC.json govern the measurement and decision.
SOURCES.json freezes native source bytes; ROWS.tsv freezes86 selected strips
before feature extraction. measure.py extracts digital contrast on near-vertical
stroke interiors and nuisance measurements. run.py fits nuisance regression
on odd rows only, ranks fixed continuation candidates on even rows, and applies
all operational gates. No manuscript transcription is parsed.

Requirements: NumPy1.26.4 and Pillow10.2.0 (versions used in this run); Python3.
No OCR, external LLM, image enhancement or generated manuscript pixels.
Synthetic pixel arrays test the measurement code only.

Controls do not establish physical ink concentration, temporal direction or
intended reading order. Artificial cuts do not simulate actual pen lifts.

Pre-score instrument correction: synthetic constant-ink fixtures exposed a
width-dependent bias with the draft9-pixel background filter. The final
registered filter is15pixels and is tested across the full2–10pixel band.
No manuscript feature or outcome was used to choose this correction.
