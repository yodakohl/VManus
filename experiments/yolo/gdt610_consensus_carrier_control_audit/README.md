# GDT610 — consensus-carrier control audit

Status: CONSENSUS_STABILITY_INCREASES__WHOLE_WORD_KEY_STABLE_BUT_WRONG.

A six-view consensus term raises exact control-map stability from 37.8% to
81.6%, but held plaintext character recovery remains only 33.7%. The failure
is localized: all eleven planted whole-word carriers converge to one output
across all six views, yet all eleven outputs are wrong.

On target data, whole-word candidates are therefore injected pseudotext, not
translations. Removing those candidates leaves only eight repetitive Latin
matches (iiii, sese, cccc) and no Old Italian or Middle High German match.

This closes consensus as a substitute for independent whole-word or syllable
information. It does not test GDT609's compositional FST34 architecture.
