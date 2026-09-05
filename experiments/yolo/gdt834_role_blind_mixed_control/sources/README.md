# Summary

The **UDante** treebank is based on the Latin texts of Dante Alighieri, taken from the [**DanteSearch corpus**](https://dantesearch.dantenetwork.it), originally created at the University of Pisa, Italy. 

It is a treebank of Latin language, more precisely of **literary Medieval Latin** (XIVth century).

# Introduction

This treebank includes 1 721 sentences (57 242 syntactic words) and consists of
literary texts (letters, treatises, poetry). The treebank is licensed under the terms of
[CC BY-NC-SA 3.0](http://creativecommons.org/licenses/by-nc-sa/3.0/).

**UDante** includes the following Latin texts (mostly) by Dante Alighieri, or disputedly attibuted to him:

* *De vulgari eloquentia*:  13 873 syntactic words for 421 sentences over 2 books
* *Monarchia*: 23403 syntactic words for 682 sentences over 3 books
* *Letters*: 11 993 syntactic words for 376 sentences over 13 letters
* *Questio de aqua et terra*: 5 243 syntactic words for 133 sentences
* *Eclogues*: 2 730 syntactic words for 111 sentences over 4 eclogues

The syntactic annotation of the **UDante** treebank has been created through a manual annotation process performed in the context of a collaboration between the University of Pisa (responsible: Mirko Tavoni) and the [**LiLa: Linking Latin project**](https://lila-erc.eu) at the Università Cattolica del Sacro Cuore, Milan, Italy (PI: Marco Passarotti). 
The annotation process was co-ordinated by Flavio Massimiliano Cecchini, Giovanni Moretti and Rachele Sprugnoli (all based at the Università Cattolica del Sacro Cuore).

# Acknowledgments

The LiLa project has received funding from the European Research Council (ERC) under the European Union’s  _Horizon 2020 research and innovation programme – Grant Agreement No. 769994_.

We wish to thank all the annotators of the **UDante** treebank: Daniela Corbetta, Federica Favero, Federica Gamba, Martina de Laurentiis, Giulia Pedonese, Andrea Peverelli and Elena Vagnoni.

## References

* Flavio Massimiliano Cecchini, Rachele Sprugnoli, Giovanni Moretti, Marco Passarotti. 2020. *UDante: First Steps Towards the Universal Dependencies Treebank of Dante's Latin Works*. In: Johanna Monti, Felice Dell'Orletta, Fabio Tamburini (eds.), Proceedings of the Seventh Italian Conference on Computational Linguistics. CEUR Workshop Proceedings, pp. 1-7 ([link](http://ceur-ws.org/Vol-2769/paper_14.pdf)).

* Gamba, F. and Zeman, D. (2023a). [Universalising Latin Universal Dependencies: a harmonisation of Latin treebanks in UD](https://aclanthology.org/2023.udw-1.2/). In *Proceedings of the Sixth Workshop on Universal Dependencies (UDW, GURT/SyntaxFest 2023)*, Washington, DC, USA, March. Association for Computational Linguistics (ACL). 

* Gamba, F. and Zeman, D. (2023b). [Latin Morphology through the Centuries: Ensuring Consistency for Better Language Processing](https://ufal.mff.cuni.cz/biblio/attachments/2023-gamba-p3787387064232511302.pdf). In *Proceedings of the Ancient Language Processing Workshop associated with the 14th International Conference on Recent Advances in Natural Language Processing RANLP 2023*, Varna, Bulgaria, September. 


# Data and data split

## Corpus description

The **DanteSearch** corpus consists of all Latin works by Dante - Italian literate and politician of the XIII-XIVth century, originary of Florence, considered to be "the father of the Italian language" and most famous for its *Divina Commedia* (written in Tuscan literary Italian) - together with some related works by other authors. In particular:

* *De vulgari eloquentia* is a rhetoric and linguistic treaty about the identification of the "best" *vulgar* (i.e. vernacular language) among those spoken in Italy, and  the best practices for its use in poetry, as opposed to Latin;
* *Monarchia* is a political treaty about the relation between Empire and Church;
* the *Letters* are a collection of correspondence by Dante, mostly of political character. The collection includes letters in the name of other persons, and some incomplete letters. The actual authorship of the famous XIIIth letter to Cangrande della Scala (ruler of Verona) is disputed; 
* *Questio de aqua et terra* is a technico-philosophical dissertation about the shape of the Earth and the oceans, and is, too, of disputed authorship;
* the *Eclogues* are four poetic compositions of bucolic character in response to each other, two by Dante and two by Giovanni del Virgilio (Bolognese poet, grammarian and Latinist of the XIII-XIVth century).


## Annotation

The following table schematically describes for each layer of the **UDante** treebank how it has been obtained with respect to the original **DanteSearch** corpus, which is annotated only for parts of speech and morphological features by means of an own, specifically developed tagset. 

| CoNLL-U Field | Source |
| ------ | ------ |
| ID | Sentence segmentation and tokenization is based on the original **DanteSearch** corpus, but has been manually, and partially automatically, modified in some cases (by means of both splits and merges of tokens or sentences) |
| FORM | Obtained from the **DanteSearch** corpus; some minor mistakes have been manually corrected |
| LEMMA | Obtained from the **DanteSearch** corpus, but manually and partially automatically modified (and in some cases corrected) in some occurrences in order to fit with changes in other annotation layers (part of speech, morpholexical features), or for reasons of standardization |
| UPOSTAG | Converted automatically from the **DanteSearch** tagset, but manually and partially automatically modified in order to fit with annotation solutions related to the UD formalism |
| XPOSTAG | As in the **DanteSearch** corpus (may be split or merged over multiple tokens if the tokenization has been changed) |
| FEATS |  Converted automatically from the **DanteSearch** tagset, but manually and partially automatically corrected, modified and augmented according to the UD formalism and guidelines for Latin |
| HEAD | Manually annotated from scratch and later manually and partially automatically corrected |
| DEPREL | Manually annotated from scratch and later manually and partially automatically corrected |
| DEPS | Currently unused |
| MISC | `SpaceAfter` feature added automatically |

Besides reproducing the original text (`# text =`), the headers of each sentence identify it (`# sent_id = `) with a three-letter code representing the literary work they belong to (`DVE` = *De vulgari eloquentia*, `Mon` = *Monarchia*, `Epi` = *Letters*, `Que` = *Questio de aqua et terra*, `Egl` = *Eclogues*) coupled with a progressive key starting from 1, and also display a more precise reference (i.e. book, section, paragraph...) internal to that work by means of a row introduced by `# citation_hierarchy = `.

## Data split

The treebank is split into three subsets, `dev`, `test` and `train`, with a respective approximate ratio of 20%/20%/60%. Each section in the **UDante** treebank consists of ordered, running text and represents a complete literary work (*De vulgari eloquentia*, *Monarchia*, *Questio de aqua et terra*) or a coherent collection of texts (*Eclogues*, *Letters*): as such, no text has been further split, resulting in a somewhat skewed split ratio with respect to the canonically recommended 10 000 tokens for `dev`/`test` of corpora of comparable magnitude. The distribution of the works with respect to the subsets is as follows:

* `dev`: *Letters* = 11 993 tokens (21%)
* `test`: *De vulgari eloquentia* = 13 873 tokens (24%)
* `train`: *Monarchia* + *Eclogues* + *Questio de aqua et terra* = 23 403 + 2 730 + 5 243 = 31 376 tokens (55%) 

Since the **UDante** treebank represents all known Latin works by Dante, its structure is foreseen to remain quite stable in the future. 



# Changelog

<u>Please note:</u> as a byproduct of linguistic (or other) investigations performed on the **UDante** treebank, or its use for NLP purposes, constant corrections and improvements are performed on the syntactic trees as need be. It would not be sensible to list all such interventions in full, since the overall structure of the treebank is not affected. Whoever detects errors, inconsistencies or dubious annotation choices is gladly invited to report them! 

* 2024-11-15 v2.15
    * Reannotated `fixed` expressions *hoc/id/quod est* to regular copular structures (and *quod est* as relative clauses).
* 2024-11-15 v2.15
    * Implementation of new rules excluding descendants of syntactic words with dependency relations `det`, involving reattachment to the head and possible other minor corrections
        * the only case where this is not applied are the reduplicating determiners *quot quot* and *tot tot*
    * Minor correction of features of `Foreign=Yes` words, shifting `NameEntity` and `Proper` to the `MISC` field
    * Splitting of sentence `DVE-145` into three sentences to correct previous faulty segmentation, and especially the annotation of a Latin sentence (now `DVE-145-3`)
* 2023-11-15 v2.13
    * Implementation of overall syntactic and morphologic harmonisation following (Gamba & Zeman 2023a) and (Gamba & Zeman 2023b)
    * Introduction of the new subtyped relation [`flat:redup`]() together with `MISC` specifications for reduplications, occurring three times in the treebank: *quot quot* (distributive), *tot tot* (distributive) and *me me* (emphatic)
    * Steady reduction of the use of the [`fixed`]() relation
        * re-annotation of 1 gapping (i.e. non-projective) `fixed` construction
        * down from 130 to 45 occurrences of other `fixed` construction, such as *ex quo*, *in quantum*, spurious clitic univerbations, and an anomalous *Adriatici maris*
* 2022-11-15 v2.11
    * Implementations of the [amendment](https://universaldependencies.org/changes.html#multiple-subjects) for clausal non-verbal copular constructions and corrections regarding multiple subjects and introduction of the `:outer` subtype for subjects and copulas
    * Implementation of the [amendment for reported speech](https://universaldependencies.org/changes.html#reported-speech), with the introduction of the `:reported` and `:reporting` subtypes
        * this in turn has led to a complete revision of the use of `parataxis` in UDante, drastically reducing its presence
    * Implementation of the proposal of [`VerbForm`](la-feat/VerbForm) reform as for (Cecchini, 2021; see documentation entry for `VerbForm`)
        * at the same time, introduction of the `TraditionalMood` and `TraditionalTense` features in `MISC` to take into account traditional denominations  
    * Double-pronoun constructions, also called free relatives, have been retraced to their treatment in IT-TB and LLCT, i.e. the relative pronoun is no longer "promoted" as external head and argument of the matrix clause; the `:relcl` subtype is introduced for these cases
    * Many "small words" (especially particles) and their features have started being standardised among treebanks. For example, *is*/*ea*/*id* is now always a `PRON` with `PronType=Prs`, *nam* always a `PART`, `AdvType` has been added to many "adverbs"...
        * *et*, *nec* etc. now stay `CCONJ` even when acting as focalisers
        * *unus* is uniformed to a determiner (`DET`) with both cardinal numeral type and indefinite pronoun type, and numeric value `1`
        * multiple (comma-separated) `PronType`s have been revised and reduced to one; the interrogative `Int` value has been streamlined as possible 
    * Remotion of the value `Pos` for the feature `Degree` ("positive" degree is still retrievable as the absence of another degree)
    * Various other occasional corrections of the annotation, especially in the *Monarchia* section
* 2022-05-15 v2.10
    * Numerous manual or semi-automatic corrections have taken place, intervening on wrong sentence parsings, incorrect tokenisations, or more generally standardising some erratic annotations, especially with regard to adverbial and conjunctional elements. Some new annotation practices have also been implemented (for explanations, we point to the UD documentation pages for Latin). 
* 2021-05-15 v2.8
    * First release in UD


<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD v2.8
License: CC BY-NC-SA 3.0
Includes text: yes
Parallel: no
Genre: nonfiction poetry email
Lemmas: converted with corrections
UPOS: converted with corrections
XPOS: manual native
Features: converted with corrections
Relations: manual native
Contributors: Cecchini, Flavio Massimiliano; Moretti, Giovanni; Passarotti, Marco; Sprugnoli, Rachele; Corbetta, Daniela; Favero, Federica; Gamba, Federica; de Laurentiis, Martina; Pedonese, Giulia; Peverelli, Andrea; Vagnoni, Elena; Tavoni, Mirko
Contributing: elsewhere
Contact: flavio.cecchini@unicatt.it, marco.passarotti@unicatt.it
===============================================================================
</pre>

