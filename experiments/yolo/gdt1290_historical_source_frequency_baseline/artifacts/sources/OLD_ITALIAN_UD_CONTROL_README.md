# Summary

Italian-Old is a treebank containing **Dante Alighieri's Comedy** (composed between approximately 1306 and 1321), based on the 1994 Petrocchi edition and taken from the [**DanteSearch corpus**](https://dantesearch.dantenetwork.it), originally created at the University of Pisa, Italy. It is a treebank of Old Italian, specifically  Florentine.

# Introduction

This treebank includes 3 419 sentences (122 038 syntactic words) and is a literary text (poetry). It is divided into three sections, known as Cantiche: Inferno, Purgatorio, and Paradiso. Specifically, Inferno includes 1 228 sentences and 41 368 syntactic words; Purgatorio consists of 1 174 sentences and 41 277 syntactic words; while Paradiso contains 1 017 sentences and 39 393 syntactic words.

The treebank is split into three subsets, `dev`, `test` and `train`, with approximate ratios of 10%, 10%, and 80%, respectively, for Inferno, Purgatorio, and Paradiso. These subsets are then merged into unique `dev`, `test` and `train` sets.

The distribution of Inferno (tokens: 41 368) with respect to the subsets is as follows:
* `train`: 1002 sentences (OldItalian_Dante_Inferno-1; OldItalian_Dante_Inferno-1002) - 33104 tokens
* `dev`: 107 sentences (OldItalian_Dante_Inferno-1003; OldItalian_Dante_Inferno-1109) - 4136 tokens
* `test`: 119 sentences (OldItalian_Dante_Inferno-1110; OldItalian_Dante_Inferno-1228) - 4128 tokens

The distribution of Purgatorio (tokens: 41 277) with respect to the subsets is as follows:
* `train`: 958 sentences (OldItalian_Dante_Purgatorio-1; OldItalian_Dante_Purgatorio-958) - 33031 tokens
* `dev`: 100 sentences (OldItalian_Dante_Purgatorio-959; OldItalian_Dante_Purgatorio-1058) - 4130 tokens
* `test`: 116 sentences (OldItalian_Dante_Purgatorio-1059; OldItalian_Dante_Purgatorio-1174) - 4116 tokens

The distribution of Paradiso (tokens: 39 393) with respect to the subsets is as follows:
* `train`: 814 sentences (OldItalian_Dante_Paradiso-1; OldItalian_Dante_Paradiso-814) - 31546 tokens
* `dev`: 101 sentences (OldItalian_Dante_Paradiso-815; OldItalian_Dante_Paradiso-915) - 3951 tokens
* `test`: 102 sentences (OldItalian_Dante_Paradiso-916; OldItalian_Dante_Paradiso-1017) - 3896 tokens

The treebank also includes enhanced dependencies annotation, with a specific focus on the `orphan` dependency relation. For the criteria adopted in the enhanced annotation, please refer to the paper "«Are you Afraid of Ghosts?» A Proposal for Busting Predicate Ellipsis in Universal Dependencies" (Corbetta et al., 2025).

**!!  Italian-Old treebank is still under revision to check for mistakes and inconsistencies throughout the annotation of the Cantiche; therefore, its structure is subject to change. If you use the resource and find any problems, please do not hesitate to contact the author to suggest a correction or improvement.**

# Acknowledgments

This work has been carried out in collaboration with the research center CIRCSE (Università Cattolica del Sacro Cuore di Milano) and the University of Pavia-Bergamo (Università degli Studi di Pavia; Università degli Studi di Bergamo).
Further acknowledgment goes to the CA21167 COST Action UniDive, funded by COST (European Cooperation in Science and Technology), which supported this work, with special thanks to Daniel Zeman, Petya Osenova, and Kiril Simov for their valuable feedback throughout this research.
We extend our gratitude to all the individuals who made this work possible. 
The annotation of the sonnet by Arnaut Daniel (Purgatorio, XXVI vv.140-147) was carried out by Michele Tron.


For any doubts, suggestions, or reports, please do not hesitate to contact the person in charge: claudia.corbetta@unibg.it.


## References

To cite the treebank please refer to:

* C. Corbetta, M. Passarotti, F. M. Cecchini, G. Moretti, Hell Awaits: Building a Universal Dependencies Treebank for Dante Alighieri’s Comedy. IJCoL. Italian Journal of Computational Linguistics, 11(11-1), 2025.


* C. Corbetta, M. Passarotti, F. M. Cecchini, G. Moretti, Highway to Hell. Towards a Universal Dependencies Treebank for Dante Alighieri’s Comedy, F. Boschetti, G. Lebani, B. Magnini, N. Novielli (Eds.), Proceedings of the Ninth Italian Conference on Computational Linguistics (CLiC-it 2023, Venice, Italy, Nov 30 - Dec 2 2023), Associazione italiana di linguistica computazionale (AILC).

Other:

* D. Alighieri, La Commedia secondo l’antica vulgata voll. i–iv, number 7 in Edizione nazionale delle Opere di Dante Alighieri a cura della Società Dantesca Italiana, Le Lettere, Florence, Italy, 1994. URL: https://www.lelettere.it/libro/9788871661483, editor: Giorgio Petrocchi.


For information on the enhancement process, refer to:

* C. Corbetta, F. Iurescia, M. Passarotti, «Are you Afraid of Ghosts?» A Proposal for Busting Predicate Ellipsis in Universal Dependencies, Proceedings of the 23rd International Workshop on Treebanks and Linguistic Theories (TLT, SyntaxFest 2025), 2025.


# Changelog

* 2024-11-15 v2.15
        * Paradiso
* 2024-05-15 v2.14
        * Purgatorio
* 2023-11-15 v2.13
        * Initial release in Universal Dependencies: Inferno.


<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD v2.13
License: CC BY-SA 4.0
Includes text: yes
Parallel: no
Genre: poetry
Lemmas: converted with corrections
UPOS: converted with corrections
XPOS: automatic
Features: converted with corrections
Relations: manual native
Contributors: Corbetta, Claudia; Passarotti, Marco; Cecchini, Flavio Massimiliano; Moretti, Giovanni
Contributing: here
Contact: claudia.corbetta@unibg.it
===============================================================================
</pre>
