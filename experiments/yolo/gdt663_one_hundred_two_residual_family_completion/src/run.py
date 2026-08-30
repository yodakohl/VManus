#!/usr/bin/env python3
"""Build GDT663: close the 102-form V39 frontier as concrete V40 recipe cards."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt663_one_hundred_two_residual_family_completion")
ART = ROOT / BASE_REL / "artifacts"
G662 = Path("experiments/yolo/gdt662_seventy_six_residual_family_completion")
_spec = importlib.util.spec_from_file_location("gdt662_builder_for_gdt663", ROOT / G662 / "src/run.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load GDT662 builder")
g662 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g662)
TOKENS_REL, CROSS_REL = g662.TOKENS_REL, g662.CROSS_REL
STATUS = "PASS_1105_TARGET_POSITIONS__V40_CONCRETE_RECIPE_REGISTER"


def card(surface: str, meaning: str, composition: str, rival: str, family: str) -> dict[str, str]:
    return {
        "surface": surface,
        "working_meaning_de": meaning,
        "composition": composition,
        "strongest_rival_de": rival,
        "family": family,
    }


def parse_cards(raw: str) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    for line in raw.strip().splitlines():
        fields = line.split("\t")
        if len(fields) != 5:
            raise RuntimeError(f"bad GDT663 card row: {line!r}")
        rows.append(card(*fields))
    return tuple(rows)


# Replaceable exact-surface defaults. Component tags explain the current
# composition but never dispatch a substring on their own. Free l is the one
# deliberate split: exact-reader l has a learned libra-like weight reading;
# reader-supported joins such as o|l -> ol receive occurrence-scoped cards.
EXACT_WHOLE_SPECS = parse_cards(r"""
okeeshy	heißer, vollständig angefeuchteter Ansatz	O_PREP+K_HOT+EE_END+SH_MOIST+Y_BASE	nur heiß-feuchte Endstufe	MOIST_PREP
chokaiin	Trockenansatz, heiß auf Stufe III	CH_DRY+O_PREP+K_HOT+A+IIN_III	heiße Trockendroge III ohne Ansatz	HOT_DRY
lkain	Holzdroge, heiß auf Stufe II	L_WOOD+K_HOT+A+IN_II	erwärmte Flüssigkeit, Stufe II	WOOD
kalol	heißer Rohstoff der ersten Klasse	K_HOT+AL_RAW_I+OL_MATERIAL	bloß heißes Material	RAW_MATERIAL
okarol	Ansatzstoff aus heißer Drogenfraktion I	O_PREP+K_HOT+AR_FRACTION_I+OL_MATERIAL	heiße Fraktion I ohne Ansatz	FRACTION
qokeeody	vollständig ausgekochter Ansatz	QO_FRAME+K_HOT+EE_END+O_PREP+DY_FINISHED	vollständig erhitzen	HOT_PREP
alkal	Laugensalz / Alkali	LEARNED_ALKALI_WHOLE	Rohstoff I, heiß	LEARNED_DRUG
olkeeo	stark erhitzter Drogenauszug	OL_MATERIAL+K_HOT+EE_END+O_EXTRACT	stark erhitzter Drogenstoff	EXTRACT
arolkeey	Drogenfraktion I, vollständig erhitzt	AR_FRACTION_I+OL_MATERIAL+K_HOT+EEY_END	erhitze Fraktion I	FRACTION
chdar	abgemessene Trockenfraktion I, Anfangsstufe	CH_DRY+D_MEASURE+AR_FRACTION_I	trockener Grad statt gemessener Fraktion	DRY
sholkeedy	feuchte Drogenbasis, vollständig erhitzt	SH_MOIST+OL_BASE+K_HOT+EEDY_FINISHED	heißer Feuchtauszug	MOIST_PREP
chedar	abgemessene Trockenfraktion I, Mittelstufe	CH_DRY+E_MIDDLE+D_MEASURE+AR_FRACTION_I	anders getrenntes CHE+D+AR	DRY
teedar	abgemessene kalte Fraktion I, Endstufe	T_COLD+EE_END+D_MEASURE+AR_FRACTION_I	abgekühlte Fraktion ohne Maßwert	COLD
qotoiin	kalte Zubereitung, Form III	QO_FRAME+T_COLD+O_PREP+IIN_III	QOTAIIN-Lesevariante: kalt, Stufe III	COLD
qokchd	abgemessene heiß-trockene Droge	QO_FRAME+K_HOT+CH_DRY+D_MEASURE	verkürztes QOKCHDY	HOT_DRY
ykoly	Eintrag: heißer Drogenstoff	Y_ENTRY+KOL_HOT_MATERIAL+Y_CLOSE	heißen Auszug abseihen	ENTRY
choross	Pflanzenteil als fertige Arzneispecies	CHOR_PLANT_PART+O_PREP+SS_SPECIES	Pflanzenteile auskochen	PLANT_PART
sokchy	heiß-trockener Samenansatz, Grundform	S_SEED+O_PREP+K_HOT+CH_DRY+Y_BASE	Salz statt Saat	SEED
qokchol	heiß-trockenes Drogenmaterial	QO_FRAME+K_HOT+CHOL_DRY_MATERIAL	Trockengut erhitzen	HOT_DRY
odchaiin	Ansatz aus abgemessener Trockendroge, Stufe III	O_PREP+D_MEASURE+CH_DRY+A+IIN_III	Trockenheitsstufe III ohne Dosis	DRY
fshor	Blütendroge / Blütenstand	LEARNED_F_FLOWER+SHOR_PART	undurchsichtiges Pflanzenteil	FLOWER
ylg	in ein Holzgefäß geben	LEARNED_CONTAINER_ACTION	Drogenposten oder Abschlusszeichen	ACTION
cthoj	ein Bündel Kraut	CTHO_HERB_PREP+J_BUNDLE_UNIT	bloßer Krautansatz	HERB
choly	Trockenrückstand	CHOL_DRY_MATERIAL+Y_CLOSE	trocken abseihen	DRY
lo	Holzabsud	L_WOOD+O_DECOCTION	Flüssigkeitsansatz	WOOD
dchor	abgemessener Pflanzenteil	D_MEASURE+CHOR_PLANT_PART	trockene Portion	PLANT_PART
dosg	eine Dosis Rückstand	D_DOSE+O_PREP+SG_RESIDUE	abgemessener Samenansatz	RESIDUE
cthory	Portion Blatt- oder Krautdroge	CTH_HERB+OR_PORTION+Y_BASE	neutrale CTH-Materialform	HERB
shosaiin	eingeweichtes Saatgut, Charge III	SH_MOIST+O_PREP+S_SEED+A+IIN_III	feuchte Salzlösung, Menge III	SEED
ytchy	Eintrag: kalt-trockene Grundform	Y_ENTRY+T_COLD+CH_DRY+Y_BASE	hierzu kalt-trocken	ENTRY
tcho	Kalt-Trockenansatz	T_COLD+CHO_DRY_PREP	kühlen und trocknen	COLD
ckhor	Portion Arzneikompositum	CKH_COMPOSITE+OR_PORTION	undurchsichtige Pflanzenportion	COMPOSITE
sols	fertige Salzspecies	SOL_SALT+S_SPECIES	fertiger Saatgutposten	SALT
solaiin	Salz, Menge III	SOL_SALT+A+IIN_III	Saatgut, Charge III	SALT
shody	vollständig eingeweichter Ansatz	SH_MOIST+O_PREP+DY_FINISHED	einweichen	MOIST_PREP
ksheo	heißer Feuchtansatz	K_HOT+SHEO_MOIST_PREP	Feuchtansatz erwärmen	MOIST_PREP
akaiin	heiße Rohstoffportion, Stufe III	A_RAW+K_HOT+A+IIN_III	zu gleichen Teilen, heiß III	RAW_MATERIAL
ched	Trockenstufe Mitte, abgeschlossen	CH_DRY+E_MIDDLE+D_CLOSED	verkürzter Trockenbefehl	DRY
schesy	getrocknete Samendroge	S_SEED+CHES_DRY_MATERIAL+Y_BASE	gelernte Arzneispecies	SEED
chyky	trocken-heiß, Grundstufe	CH_DRY+Y_BASE+K_HOT+Y_BASE	trocknen und erneut erhitzen	HOT_DRY
shoqoky	Feuchtansatz, heiß am Anfang	SHO_MOIST_PREP+QOKY_HOT_START	Feuchtansatz erhitzen	MOIST_PREP
shocho	angefeuchteter Trockenansatz	SHO_MOIST_PREP+CHO_DRY_PREP	trocken angesetzte Feuchtdroge	MOIST_PREP
ckhal	Arzneikompositum, Rohstoffklasse I	CKH_COMPOSITE+AL_RAW_I	Qualitätsform statt Kompositum	COMPOSITE
sholoiin	eingeweichte Drogenzubereitung, Form III	SHOL_MOIST_MATERIAL+O_PREP+IIN_III	Feuchtstoff, Menge III	MOIST_PREP
yckhodaiin	Eintrag: Kompositum-Ansatz, Dosis III	Y_ENTRY+CKH_COMPOSITE+O_PREP+DAIIN_DOSE_III	hierzu Kompositum, Dosis III	ENTRY
keeody	vollständig ausgekochter Ansatz	K_HOT+EE_END+O_PREP+DY_FINISHED	vollständig auskochen	HOT_PREP
lchdal	gemessene trockene Holzdroge, Rohstoff I	L_WOOD+CH_DRY+D_MEASURE+AL_RAW_I	L als Flüssigkeit	WOOD
talody	kalter Rohstoff I, als Ansatz fertig	T_COLD+AL_RAW_I+O_PREP+DY_FINISHED	kalte Rohstoffdosis	COLD
char	Trockenfraktion I	CH_DRY+AR_FRACTION_I	CHOR als Pflanzenteil	DRY
chedyqokam	eine Maßeinheit heiß getrocknete Droge	CHEDY_DRY_FINISHED+QO_FRAME+K_HOT+AM_UNIT_I	verlorene Grenze CHEDY|QOKAM	MEASURE
oltedy	kalte Drogenbasis, Mittelstufe erreicht	OL_BASE+T_COLD+E_MIDDLE+DY_FINISHED	abgekühlter Auszug	COLD
sheety	vollständig angefeuchtet und gekühlt	SH_MOIST+EE_END+T_COLD+Y_BASE	anfeuchten und kühlen	MOIST_PREP
keed	Erhitzung bis Endstufe abgeschlossen	K_HOT+EE_END+D_CLOSED	bis zum Ende erhitzen	HOT_PREP
olkol	heißer Drogenauszug	OL_BASE+KOL_HOT_MATERIAL	bloß heißes Drogenmaterial	EXTRACT
olyly	seihe ein zweites Mal ab	LEARNED_OLY_STRAIN+ITERATIVE_Y	abgeseihter Holzauszug	ACTION
ldy	Holzdroge, fertig aufbereitet	L_WOOD+DY_FINISHED	L als Gewichtseinheit	WOOD
okeshey	heiß angefeuchteter Ansatz, Mittelstufe	O_PREP+K_HOT+E_MIDDLE+SH_MOIST+EY_MIDDLE	gleichzeitig heiß-feuchter Ansatz	MOIST_PREP
okeolor	erwärmte Drogenstoffportion	O_PREP+K_HOT+E_MIDDLE+OL_MATERIAL+OR_PORTION	erwärmte Zutat	EXTRACT
rory	Wurzelportion, Grundform	R_ROOT+OR_PORTION+Y_BASE	rohe Wurzel	ROOT
chedaiin	abgemessene Trockendroge, Dosis III	CH_DRY+E_MIDDLE+D_MEASURE+A+IIN_III	trocken, Stufe III	MEASURE
qoraiin	nimm eine Drogenportion, Menge III	QO_TAKE+OR_PORTION+A+IIN_III	nominale Ansatzportion III	ACTION
dary	abgemessene Fraktion I, abgeschlossen	D_MEASURE+AR_FRACTION_I+Y_CLOSE	Rohfraktion I	FRACTION
shee	vollständig anfeuchten	LEARNED_SH_MOIST+EE_END	vollständig feuchter Zustand	ACTION
ykal	Eintrag: heißer Rohstoff, Klasse I	Y_ENTRY+K_HOT+AL_RAW_I	hierzu heißer Rohstoff	ENTRY
dchokol	abgemessener heißer Trockenansatz	D_MEASURE+CH_DRY+O_PREP+KOL_HOT_MATERIAL	einen Trockenansatz erhitzen	HOT_DRY
okeshy	erhitzter, danach angefeuchteter Ansatz	O_PREP+K_HOT+E_MIDDLE+SH_MOIST+Y_BASE	gleichzeitig heiß-feuchter Ansatz	MOIST_PREP
ytaiin	Eintrag: kalt, Stufe III	Y_ENTRY+T_COLD+A+IIN_III	hierzu auf Stufe III kühlen	ENTRY
saral	rohe Samenfraktion I	S_SEED+AR_FRACTION_I+AL_RAW_I	rohe Salzfraktion I	SEED
cholchey	nachgetrocknete Droge, Mittelstufe	CHOL_DRY_MATERIAL+CHEY_DRY_MIDDLE	bloßes Trockengut, Mittelstufe	DRY
yshealdy	Eintrag: angefeuchteter Rohstoff I, fertig	Y_ENTRY+SHE_MOIST+AL_RAW_I+DY_FINISHED	hierzu angefeuchteter Rohstoff	ENTRY
chkain	trocken-heiß, Stufe II	CH_DRY+K_HOT+A+IN_II	heiß-trocken, Stufe II	HOT_DRY
rolchey	getrockneter Wurzelstoff, Mittelstufe	R_ROOT+OL_MATERIAL+CHEY_DRY_MIDDLE	trockener Wurzelauszug	ROOT
qor	nimm eine Drogenportion	QO_TAKE+OR_PORTION	nominale Drogenportion	ACTION
qokechey	heiß getrocknete Droge, Mittelstufe	QO_FRAME+K_HOT+E_MIDDLE+CHEY_DRY_MIDDLE	erhitze und trockne	HOT_DRY
deeeese	lange bis zur letzten Stufe ruhen lassen	LEARNED_LONG_REST_WHOLE	vierfach konzentrierte Arzneispecies	ACTION
olkaiin	heiße Drogenbasis, Stufe III	OL_BASE+K_HOT+A+IIN_III	Drogenbasis, Menge III	HOT_PREP
ary	Drogenfraktion I, abgeschlossen	AR_FRACTION_I+Y_CLOSE	Drogenfraktion I, Grundform	FRACTION
tolkain	gekühltes Material, wiedererwärmt auf Stufe II	T_COLD+OL_MATERIAL+K_HOT+A+IN_II	gleichzeitig kalt-heißes Material	COLD
qotl	kalte Holzdroge	LEARNED_CONTRACTION_OF_QOTOL	verkürztes kaltes Material	WOOD
l	Pfund / Gewichtseinheit	LEARNED_FREE_LIBRA_SIGLUM	freies Holzzeichen	MEASURE
ychedy	Eintrag: getrocknete Droge, fertig	Y_ENTRY+CHEDY_DRY_FINISHED	hierzu getrocknete Droge	ENTRY
olshey	eingeweichte Drogenbasis, Mittelstufe	OL_BASE+SHEY_MOIST_MIDDLE	nur feuchtes Material	MOIST_PREP
qoly	gib Vorstehendes hinzu und schließe die Zugabe ab	QOL_ADD+Y_CLOSE	Q+OLY: seihe ab	ACTION
taldain	kalter Rohstoff I, Dosis II	T_COLD+AL_RAW_I+D_DOSE+AIN_II	kalter Rohstoff, Stufe II	MEASURE
chetyry	getrocknete, abgekühlte Rohwurzel	CH_DRY+ET_COLD+R_ROOT+Y_BASE	gekühlte Trockenfraktion	ROOT
okair	heiße Drogenfraktion II im Ansatz	O_PREP+K_HOT+AIR_FRACTION_II	heißer Ansatz, Stufe II	FRACTION
oraiiin	Drogenportion IV	OR_PORTION+A+IIIN_IV	Qualitätsstufe IV	MEASURE
olaiin	Drogenstoff, Menge III	OL_BASE+A+IIN_III	Drogenstoff, Qualitätsstufe III	MEASURE
salchtedytar	fertig getrocknete, abgekühlte Samenfraktion I	SAL_SEED_RAW+CH_DRY+T_COLD+EDY_FINISHED+TAR_FRACTION_I	gelerntes langes Drogenetikett	SEED
qoteytyqoky	zunächst bis Mittelstufe kühlen, dann heiß ansetzen	QOTEY_COLD_MIDDLE+TY_SEQUENCE+QOKY_HOT_START	statische Qualitätsfolge	ACTION
sholdy	vollständig eingeweichte Droge	SHOL_MOIST_MATERIAL+DY_FINISHED	einweichen	MOIST_PREP
lkedy	erhitzte Holzdroge, Mittelstufe, fertig	L_WOOD+K_HOT+E_MIDDLE+DY_FINISHED	erwärmte Flüssigkeit	WOOD
qotaldy	kalter Rohstoff I, fertig aufbereitet	QO_FRAME+T_COLD+AL_RAW_I+DY_FINISHED	Rohstoff abkühlen	COLD
oychey	Ansatz aus dieser Trockenform I	O_PREP+Y_REFERENCE+CHEY_DRY_MIDDLE	gewöhnlicher Trockenansatz Form I	DRY
olain	Drogenstoff, Menge II	OL_BASE+A+IN_II	Drogenstoff, Qualitätsstufe II	MEASURE
opchey	Trockenpulver-Ansatz, Form I	O_PREP+P_POWDER+CHEY_DRY_MIDDLE	trockenes Pulver ohne Ansatz	POWDER
odain	Zubereitungsdosis II	O_PREP+D_DOSE+A+IN_II	Zubereitungsstufe II	MEASURE
ochedy	Ansatz aus getrockneter Droge, abgeschlossen	O_PREP+CHEDY_DRY_FINISHED	CHODY mit vertauschter Hülle	DRY
oldal	abgemessener Drogenrohstoff I	OL_BASE+D_MEASURE+AL_RAW_I	Materialzustand Rohstoff I	MEASURE
chody	Trockenansatz, abgeschlossen	CH_DRY+O_PREP+DY_FINISHED	bloß getrockneter Zustand	DRY
ckheody	fertiger Ansatz eines Arzneikompositums	CKH_COMPOSITE+E_BOUND+O_PREP+DY_FINISHED	undurchsichtiges Ganzwort	COMPOSITE
cthosg	Krautrückstand	CTHO_HERB_PREP+SG_RESIDUE	fertige Krautarzneispecies	RESIDUE
""")

TARGET_ORDER = tuple(row["surface"] for row in EXACT_WHOLE_SPECS)
TARGET_SURFACES = frozenset(TARGET_ORDER)
EXACT_BY_SURFACE = {row["surface"]: row for row in EXACT_WHOLE_SPECS}
CONTEXT_SCOPED_SURFACES = frozenset({"l"})
ACTION_SURFACES = frozenset({"ylg", "qoraiin", "shee", "qor", "qoly", "olyly", "deeeese", "qoteytyqoky"})
LEARNED_WHOLE_SURFACES = frozenset({"alkal", "fshor", "cthoj", "olyly", "deeeese", "qotl", "l", "ylg"})
ENTRY_SURFACES = frozenset({"ykoly", "ytchy", "yckhodaiin", "ykal", "ytaiin", "yshealdy", "ychedy"})
LOW_SURFACES = frozenset({
    "alkal", "arolkeey", "choross", "fshor", "ylg", "cthoj", "dosg", "deeeese",
    "salchtedytar", "chetyry", "qoteytyqoky", "cthosg",
})
STRONG_SURFACES = frozenset({
    "chokaiin", "lkain", "qokeeody", "chdar", "chedar", "qokchol", "choly", "dchor",
    "ytchy", "tcho", "shody", "char", "chedaiin", "dary", "shee", "ytaiin", "chkain",
    "qor", "olkaiin", "olshey", "qoly", "okair", "olaiin", "sholdy", "lkedy", "olain",
    "opchey", "odain", "ochedy", "chody", "ckheody",
})


def parse_counts(raw: str) -> dict[str, int]:
    return {item.split("=", 1)[0]: int(item.split("=", 1)[1]) for item in raw.split()}


EXPECTED_SURFACE_COUNTS = parse_counts("""
okeeshy=2 chokaiin=15 lkain=33 kalol=2 okarol=2 qokeeody=13 alkal=1 olkeeo=4 arolkeey=1
chdar=17 sholkeedy=2 chedar=31 teedar=3 qotoiin=2 qokchd=6 ykoly=1 choross=1 sokchy=1
qokchol=15 odchaiin=1 fshor=1 ylg=1 cthoj=1 choly=12 lo=20 dchor=23 dosg=1 cthory=2
shosaiin=4 ytchy=14 tcho=8 ckhor=8 sols=3 solaiin=1 shody=46 ksheo=5 akaiin=2 ched=17
schesy=1 chyky=4 shoqoky=1 shocho=1 ckhal=3 sholoiin=1 yckhodaiin=1 keeody=8 lchdal=2
talody=1 char=75 chedyqokam=1 oltedy=6 sheety=7 keed=2 olkol=3 olyly=1 ldy=24
okeshey=1 okeolor=1 rory=1 chedaiin=32 qoraiin=1 dary=19 shee=11 ykal=9 dchokol=1
okeshy=2 ytaiin=39 saral=3 cholchey=2 yshealdy=1 chkain=12 rolchey=1 qor=21
qokechey=1 deeeese=1 olkaiin=28 ary=15 tolkain=2 qotl=2 l=163 ychedy=11 olshey=13
qoly=7 taldain=1 chetyry=1 okair=18 oraiiin=1 olaiin=39 salchtedytar=1 qoteytyqoky=1
sholdy=6 lkedy=26 qotaldy=1 oychey=1 olain=11 opchey=26 odain=14 ochedy=8 oldal=2
chody=78 ckheody=5 cthosg=1
""")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_102_COMPLETIONS.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V40_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V40.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V40.tsv", "COMPLETE_PASSAGES_V40.tsv",
    "ONE_UNKNOWN_PASSAGES_V40.tsv",
)

LABEL_RENDER = {
    "l": "[Pfundzeichen]", "char": "[Trockenfraktionszeichen]", "dary": "[Fraktionszeichen]",
    "qor": "[Portionszeichen]", "olkol": "[Heißauszugzeichen]", "olaiin": "[Drei-Maß-Zeichen]",
    "saral": "[Saatrohstoffzeichen]", "ary": "[Fraktionszeichen]",
}
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"vorgang ausführen|gut bearbeiten|arbeitsprodukt|nimm werkzeug",
    re.I,
)
PRACTICAL_REPLACEMENTS = (
    ("Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz", "Grundansatz"),
    ("Eigenschafts-/Zustands-/Materialträger", "Grundansatz"),
    ("trocken in der Mitte des Grades, abgeschlossen", "bis zur mittleren Trockenstufe gebracht"),
    ("trocken in der Mitte des Grades", "bis zur mittleren Trockenstufe"),
    ("trocken am Ende des Grades, abgeschlossen", "vollständig getrocknet"),
    ("trocken am Ende des Grades", "vollständig getrocknet"),
    ("trocken am Anfang des Grades, abgeschlossen", "angetrocknet"),
    ("trocken am Anfang des Grades", "angetrocknet"),
    ("feucht in der Mitte des Grades, abgeschlossen", "bis zur mittleren Einweichstufe gebracht"),
    ("feucht in der Mitte des Grades", "bis zur mittleren Einweichstufe"),
    ("feucht am Ende des Grades, abgeschlossen", "vollständig eingeweicht"),
    ("feucht am Ende des Grades", "vollständig eingeweicht"),
    ("feucht am Anfang des Grades", "leicht angefeuchtet"),
    ("heiß in der Mitte des Grades, abgeschlossen", "bis zur mittleren Heizstufe gebracht"),
    ("heiß in der Mitte des Grades", "bis zur mittleren Heizstufe"),
    ("heiß am Ende des Grades, abgeschlossen", "bis zur Heizendstufe gebracht"),
    ("heiß am Ende des Grades", "bis zur Heizendstufe"),
    ("heiß am Anfang des Grades, abgeschlossen", "leicht erhitzt"),
    ("heiß am Anfang des Grades", "leicht erhitzt"),
    ("kalt in der Mitte des Grades, abgeschlossen", "bis zur mittleren Kühlstufe gebracht"),
    ("kalt in der Mitte des Grades", "bis zur mittleren Kühlstufe"),
    ("kalt am Ende des Grades, abgeschlossen", "bis zur Kühlendstufe gebracht"),
    ("kalt am Ende des Grades", "bis zur Kühlendstufe"),
    ("kalt am Anfang des Grades", "leicht gekühlt"),
    ("Pflanzen-/Reproduktionsteil", "Pflanzenteil"),
    ("reproduktiver Teil", "Blüten- oder Fruchtdroge"),
    ("trocken; nominal trockenes Gut/Material", "Trockengut"),
    ("feucht; nominal feuchtes Gut/Material", "Feuchtgut"),
    ("trocken; nominal trockenes Gut", "Trockengut"),
    ("feucht; nominal feuchtes Gut", "Feuchtgut"),
    ("feuchte CTH-Materialform; im Herbal feuchtes Blatt-/Krautgut", "feuchte Krautdroge"),
    ("trockene CTH-Materialform; im Herbal trockenes Blatt-/Krautgut", "getrocknete Krautdroge"),
    ("CTH-Drogenmaterial; im Herbal Blatt-/Krautdroge", "Krautdroge"),
    ("CTH-Drogenmaterial", "Krautdroge"),
    ("Grad-/Maßwert IV", "vier Maße"),
    ("Grad-/Maßwert III", "drei Maße"),
    ("Grad-/Maßwert II", "zwei Maße"),
    ("Menge-/Klassenwert IV", "vier Teile"),
    ("Menge-/Klassenwert III", "drei Teile"),
    ("Menge-/Klassenwert II", "zwei Teile"),
    ("Menge IV", "vier Teile"),
    ("Menge III", "drei Teile"),
    ("Menge II", "zwei Teile"),
    ("Qualitätsgrad IV", "Stufe IV"),
    ("Qualitätsgrad III", "Stufe III"),
    ("Qualitätsgrad II", "Stufe II"),
    ("Rohstoffklasse I im Ansatz, heiß am Gradanfang", "Rohstoff I, leicht erhitzt im Ansatz"),
    ("Rohstoffklasse I im Ansatz, kalt am Gradanfang", "Rohstoff I, leicht gekühlt im Ansatz"),
    ("Rohstoffklasse I, feucht in der Gradmitte", "Rohstoff I bis zur mittleren Einweichstufe"),
    ("Rohstoffklasse I, heiß in der Gradmitte", "Rohstoff I bis zur mittleren Heizstufe"),
    ("Rohstoffklasse I", "Rohstoff I"),
    ("heißer Ansatz in der Mitte des Grades", "Ansatz bis zur mittleren Heizstufe"),
    ("kalter Ansatz in der Mitte des Grades, abgeschlossen", "Ansatz auf mittlerer Kühlstufe abgeschlossen"),
    ("kalter Ansatz in der Mitte des Grades", "Ansatz bis zur mittleren Kühlstufe"),
    ("kalter Ansatz am Ende des Grades, abgeschlossen", "Ansatz auf Kühlendstufe abgeschlossen"),
    ("kalter Ansatz am Ende des Grades", "Ansatz auf Kühlendstufe"),
    ("heißer Ansatz am Ende des Grades, abgeschlossen", "Ansatz auf Heizendstufe abgeschlossen"),
    ("heißer Ansatz am Ende des Grades", "Ansatz auf Heizendstufe"),
    ("heißer Ansatz am Anfang des Grades", "leicht erhitzter Ansatz"),
    ("heiß, Grad III, im Ansatzrahmen", "Ansatz auf Heizstufe III"),
    ("heißes Material [terminal-M]", "eine Maßeinheit heißer Drogenbasis"),
    ("im Herbal ", ""),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def parse_compact(value: object) -> list[str]:
    return [] if str(value) in {"", "NONE"} else str(value).split("|")


def position_label(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def card_type(surface: str) -> str:
    if surface == "l":
        return "CONTEXT_SCOPED_LEARNED_SIGLUM"
    if surface in ACTION_SURFACES:
        return "LEARNED_ACTION_WHOLE"
    if surface in LEARNED_WHOLE_SURFACES:
        return "LEARNED_WHOLE"
    if surface in ENTRY_SURFACES:
        return "ENTRY_COMPOSITE"
    return "PRODUCTIVE_COMPOUND"


def card_strength(surface: str) -> str:
    if surface in LOW_SURFACES:
        return "LOW_EXPLORATORY"
    if surface == "l":
        return "CONTEXT_STRONG_READER_MERGE__FREE_SIGLUM_LOW"
    if surface in STRONG_SURFACES:
        return "STRONG_PRACTICAL_OR_COMPOSITIONAL"
    return "MEDIUM_EXACT_WHOLE"


def l_merge_candidate(
    line: list[dict[str, str]], index: int, cross_row: dict[str, str],
    known_meanings: dict[str, str],
) -> tuple[str, str, str]:
    """Return merge direction, merged surface and a concrete rendering."""
    left = line[index - 1]["eva"] if index else ""
    right = line[index + 1]["eva"] if index + 1 < len(line) else ""
    alternate_tokens = set(cross_row["it2a_clean"].split()) | set(cross_row["rf1b_clean"].split())
    candidates: list[tuple[str, str]] = []
    if left and left + "l" in alternate_tokens:
        candidates.append(("LEFT", left + "l"))
    if right and "l" + right in alternate_tokens:
        candidates.append(("RIGHT", "l" + right))
    for direction, merged in candidates:
        if merged in known_meanings:
            return direction, merged, known_meanings[merged]
    if candidates:
        direction, merged = candidates[0]
        if direction == "RIGHT":
            return direction, merged, "Holzdroge in der gebundenen Anschlussform"
        return direction, merged, "Grundstoff des vorstehenden Ansatzes"
    return "NONE", "NONE", EXACT_BY_SURFACE["l"]["working_meaning_de"]


def rendering_class(
    surface: str, position: str, kind: str, merge_direction: str = "NONE",
    merge_surface: str = "NONE",
) -> str:
    if kind == "L" or position == "ONLY":
        return "LABEL_SIGLUM"
    if surface == "l":
        if merge_direction != "NONE":
            known = "KNOWN" if merge_surface in TARGET_SURFACES else "READER"
            return f"L_{known}_MERGE_{merge_direction}"
        return "L_FREE_WEIGHT_SIGLUM"
    if surface in LABEL_RENDER and kind == "L":
        return "LABEL_SIGLUM"
    if surface == "qor":
        return "QOR_TAKE_PORTION"
    if surface == "qoraiin":
        return "QORAIIN_TAKE_PORTION_III"
    if surface == "shee":
        return "SHEE_MOISTEN_FULLY"
    if surface == "qoly":
        return "QOLY_ADD_AND_CLOSE"
    if surface == "olyly":
        return "OLYLY_STRAIN_AGAIN"
    if surface == "ylg":
        return "YLG_PUT_IN_WOODEN_VESSEL"
    if surface == "deeeese":
        return "DEEEESE_REST_TO_FINAL_STAGE"
    if surface == "qoteytyqoky":
        return "QOTEYTYQOKY_COOL_THEN_HEAT"
    if surface in ENTRY_SURFACES:
        return "ENTRY_WHOLE" if position == "BOS" else "REFERENCE_WHOLE"
    return "EXACT_WHOLE"


def occurrence_values(
    surface: str, position: str, kind: str, merge_direction: str, merge_surface: str,
    merge_meaning: str,
) -> tuple[str, str, str]:
    klass = rendering_class(surface, position, kind, merge_direction, merge_surface)
    default = EXACT_BY_SURFACE[surface]["working_meaning_de"]
    if klass == "LABEL_SIGLUM":
        label = LABEL_RENDER.get(surface, f"[{default}-Zeichen]")
        return label, label, klass
    if surface == "l" and merge_direction != "NONE":
        return merge_meaning, merge_meaning, klass
    if klass == "L_FREE_WEIGHT_SIGLUM":
        return default, "ein Pfund", klass
    render = {
        "QOR_TAKE_PORTION": "nimm eine Drogenportion:",
        "QORAIIN_TAKE_PORTION_III": "nimm eine Drogenportion, Menge III:",
        "SHEE_MOISTEN_FULLY": "feuchte vollständig an",
        "QOLY_ADD_AND_CLOSE": "gib Vorstehendes hinzu und schließe die Zugabe ab.",
        "OLYLY_STRAIN_AGAIN": "seihe ein zweites Mal ab.",
        "YLG_PUT_IN_WOODEN_VESSEL": "gib Vorstehendes in ein Holzgefäß.",
        "DEEEESE_REST_TO_FINAL_STAGE": "lasse bis zur letzten Stufe ruhen",
        "QOTEYTYQOKY_COOL_THEN_HEAT": "kühle zunächst bis zur Mittelstufe und setze danach heiß an",
    }.get(klass, default)
    if klass == "REFERENCE_WHOLE" and default.startswith("Eintrag: "):
        render = "hierzu: " + default.removeprefix("Eintrag: ")
    return default, render, klass


def practicalize(text: str) -> str:
    rendered = text
    for source, target in PRACTICAL_REPLACEMENTS:
        rendered = rendered.replace(source, target)
    rendered = re.sub(r"\s+", " ", rendered)
    return re.sub(r"\.{2,}", ".", rendered).replace(".;", ";").replace(":;", ":").strip()


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": len(glossary),
    }


def line_translation(
    locus: str,
    line: list[dict[str, str]],
    glosses: list[str],
    y_occurrence_by_token: dict[tuple[str, int], dict[str, object]],
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]],
    target_by_token: dict[tuple[str, int], dict[str, object]],
) -> str:
    """Render V40 while folding alternate-reader l joins into one phrase."""
    working_glosses = list(glosses)
    # GDT662's renderer only applies its positional action cards to the map it
    # receives as the current layer.  Re-promote the archived G662 rows here;
    # older G660/G661 rows remain the inherited structural layer exactly as in
    # the V39 build.
    inherited = {
        key: row for key, row in inherited_target_by_token.items()
        if not str(row.get("occurrence_id", "")).startswith("G662-")
    }
    current = {
        key: row for key, row in inherited_target_by_token.items()
        if str(row.get("occurrence_id", "")).startswith("G662-")
    }
    current.update(target_by_token)
    suppress: set[tuple[str, int]] = set()
    for key, occurrence in target_by_token.items():
        if key[0] != locus or occurrence["surface"] != "l":
            continue
        direction = str(occurrence["reader_merge_direction"])
        index = int(occurrence["ordinal"]) - 1
        neighbor_index = index - 1 if direction == "LEFT" else index + 1 if direction == "RIGHT" else -1
        if 0 <= neighbor_index < len(line):
            neighbor_key = (locus, int(line[neighbor_index]["token_index"]))
            suppress.add(neighbor_key)
            working_glosses[neighbor_index] = ""
    for key in suppress:
        inherited.pop(key, None)
        current.pop(key, None)
    rendered = g662.line_translation(
        locus, line, working_glosses, y_occurrence_by_token, inherited, current
    )
    return practicalize(rendered)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_art = ROOT / G662 / "artifacts"
    pages = {row["page"] for row in read_tsv(base_art / "PAGE_ALLOWLIST.tsv")}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")
    tokens, token_stats = g662.g661.g659.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = g662.g661.g659.guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    if (len(tokens), len(cross)) != (32339, 4137):
        raise RuntimeError("guarded source census drift")
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    tokens_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
        tokens_by_surface[row["eva"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = {row["locus"]: row for row in cross}
    if len(by_line) != 4128:
        raise RuntimeError("physical-line census drift")
    for locus, line in by_line.items():
        if locus not in cross_by_locus or " ".join(row["eva"] for row in line) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"guarded token/cross mismatch: {locus}")

    base_dictionary = read_tsv(base_art / "WORKING_DICTIONARY_V39.tsv")
    base_glossary_rows = read_tsv(base_art / "V39_WORKING_TOKEN_GLOSSARY.tsv")
    base_coverage = read_tsv(base_art / "ALL_LINE_CONCRETE_COVERAGE_V39.tsv")
    base_complete = read_tsv(base_art / "COMPLETE_PASSAGES_V39.tsv")
    base_one = read_tsv(base_art / "ONE_UNKNOWN_PASSAGES_V39.tsv")
    frontier = read_tsv(base_art / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    dimensions = (
        len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete),
        len(base_one), len(frontier),
    )
    if dimensions != (785, 632, 4128, 331, 302, 105):
        raise RuntimeError(f"V39 base dimensions drift: {dimensions!r}")
    frontier_order = tuple(dict.fromkeys(row["unknown_surface"] for row in frontier))
    if frontier_order != TARGET_ORDER or len(TARGET_SURFACES) != 102:
        raise RuntimeError("the 102-form frontier or fixed order drifted")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    if any(surface in base_glossary for surface in TARGET_SURFACES):
        raise RuntimeError("a GDT663 target unexpectedly already has a V39 glossary row")
    known_meanings = {surface: row["working_meaning_de"] for surface, row in base_glossary.items()}
    known_meanings.update({row["surface"]: row["working_meaning_de"] for row in EXACT_WHOLE_SPECS})

    y_occurrences = read_tsv(
        ROOT / g662.g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv"
    )
    y_occurrence_by_token = {
        (row["locus"], int(row["token_index"])): row for row in y_occurrences
    }
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    inherited_audits = (
        ROOT / g662.g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        ROOT / g662.G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        base_art / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    )
    for path in inherited_audits:
        for row in read_tsv(path):
            inherited_target_by_token[row["locus"], int(row["token_index"])] = row

    surface_counts = Counter(row["eva"] for row in tokens)
    observed_counts = {surface: surface_counts[surface] for surface in TARGET_ORDER}
    if observed_counts != EXPECTED_SURFACE_COUNTS or sum(observed_counts.values()) != 1105:
        raise RuntimeError(f"target surface count drift: {observed_counts!r}")
    exact, normalized = g662.g661.g660.stable_maps(tokens, cross_by_locus)

    occurrence_rows: list[dict[str, object]] = []
    target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    context_counts: Counter[str] = Counter()
    l_merge_counts: Counter[str] = Counter()
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        for index, token in enumerate(line):
            surface = token["eva"]
            if surface not in TARGET_SURFACES:
                continue
            ordinal = index + 1
            position = position_label(ordinal, len(line))
            key = (locus, int(token["token_index"]))
            merge_direction = merge_surface = "NONE"
            merge_meaning = EXACT_BY_SURFACE[surface]["working_meaning_de"]
            if surface == "l" and token["kind"] != "L" and position != "ONLY":
                merge_direction, merge_surface, merge_meaning = l_merge_candidate(
                    line, index, cross_by_locus[locus], known_meanings
                )
                l_merge_counts[
                    f"{merge_direction}:{merge_surface}" if merge_direction != "NONE" else "FREE_NO_ADJACENT_MERGE"
                ] += 1
            working_gloss, working_render, klass = occurrence_values(
                surface, position, token["kind"], merge_direction, merge_surface, merge_meaning
            )
            item: dict[str, object] = {
                "occurrence_id": f"G663-T{len(occurrence_rows) + 1:04d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "token_kind": token["kind"], "position": position, "section": token["section"],
                "language": token["language"], "hand": token["hand"],
                "family": EXACT_BY_SURFACE[surface]["family"], "card_type": card_type(surface),
                "scope_mode": (
                    "OCCURRENCE_SCOPED_READER_MERGE_OR_FREE_SIGLUM" if surface == "l"
                    else "EXACT_WHITESPACE_WHOLE_WITH_OPTIONAL_PRACTICAL_RENDER"
                ),
                "rendering_class": klass,
                "left_surface": words[index - 1] if index else "<BOS>",
                "right_surface": words[index + 1] if index + 1 < len(line) else "<EOS>",
                "reader_merge_direction": merge_direction, "reader_merge_surface": merge_surface,
                "working_gloss_de": working_gloss, "working_render_de": working_render,
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
                "reader_exact": exact[key], "split_normalized": normalized[key],
                "all_three_present": cross_by_locus[locus]["all_three_present"],
                "all_present_exact": cross_by_locus[locus]["all_present_exact"],
                "zl3b_line": cross_by_locus[locus]["zl3b_clean"],
                "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"],
            }
            occurrence_rows.append(item)
            target_by_token[key] = item
            context_counts[klass] += 1
    if len(occurrence_rows) != 1105 or len(target_by_token) != 1105:
        raise RuntimeError("target occurrence census drift")
    l_rows = [row for row in occurrence_rows if row["surface"] == "l"]
    if len(l_rows) != 163 or sum(int(row["reader_exact"]) for row in l_rows) != 38:
        raise RuntimeError("free-l reader census drift")

    base_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_rows: list[dict[str, object]] = []
    non_target_before: list[tuple[object, ...]] = []
    non_target_after: list[tuple[object, ...]] = []
    affected_loci: set[str] = set()
    for base_row in base_coverage:
        locus = base_row["locus"]
        line = by_line[locus]
        glosses = split_pipe(base_row["token_glosses_de"])
        sources = split_pipe(base_row["gloss_sources"])
        states = split_pipe(base_row["scope_states"])
        if not (len(line) == len(glosses) == len(sources) == len(states)):
            raise RuntimeError(f"V39 token columns misalign: {locus}")
        unknown_pairs = list(zip(parse_compact(base_row["unknown_ordinals"]), parse_compact(base_row["unknown_surfaces"])))
        target_ordinals: set[str] = set()
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_by_token:
                non_target_before.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
                continue
            occurrence = target_by_token[key]
            surface = token["eva"]
            if glosses[index] != f"[{surface}:?]" or sources[index] != "OPEN" or states[index] != "UNKNOWN_SURFACE":
                raise RuntimeError(f"V39 target not open at {locus}.{index + 1}: {surface}")
            glosses[index] = str(occurrence["working_gloss_de"])
            if surface == "l":
                sources[index] = f"GDT663:{occurrence['rendering_class']}:{occurrence['reader_merge_surface']}"
                states[index] = "KNOWN_CONTEXT_LICENSED" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            else:
                sources[index] = f"GDT663:EXACT_WHOLE:{surface}"
                states[index] = "KNOWN_EXACT_WHOLE" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            target_ordinals.add(str(index + 1))
            affected_loci.add(locus)
        for index, token in enumerate(line):
            if (locus, int(token["token_index"])) not in target_by_token:
                non_target_after.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
        unknown_pairs = [pair for pair in unknown_pairs if pair[0] not in target_ordinals]
        result = dict(base_row)
        result["known_tokens"] = int(base_row["known_tokens"]) + len(target_ordinals)
        result["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        result["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        result["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        result["unknown_tokens"] = len(unknown_pairs)
        result["coverage_fraction"] = f"{int(result['known_tokens']) / int(result['token_count']):.6f}"
        result["token_glosses_de"] = " | ".join(glosses)
        result["gloss_sources"] = " | ".join(sources)
        result["scope_states"] = " | ".join(states)
        result["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        result["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(target_ordinals) != len(unknown_pairs):
            raise RuntimeError(f"V39->V40 arithmetic drift: {locus}")
        coverage_rows.append(result)
    if non_target_before != non_target_after:
        raise RuntimeError("a non-target token projection changed")
    non_target_sha = canonical_hash(non_target_before)
    coverage_by_locus = {str(row["locus"]): row for row in coverage_rows}

    complete_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) or int(row["token_count"]) < 2:
            continue
        item = dict(row)
        item["strict_complete"] = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        item["working_translation_de"] = line_translation(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]),
            y_occurrence_by_token, inherited_target_by_token, target_by_token,
        )
        complete_rows.append(item)
    complete_rows.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for rank, row in enumerate(complete_rows, 1):
        row["rank"] = rank

    base_one_by_locus = {row["locus"]: row for row in base_one}
    one_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        old = base_one_by_locus.get(str(row["locus"]))
        if old and old["unknown_surface"] == surface and int(old["unknown_ordinal"]) == ordinal:
            proposal, basis, strength = old["proposed_default_de"], old["proposal_basis"], old["proposal_strength"]
        else:
            proposal, basis, strength = f"[{surface}:?]", "NEWLY_EXPOSED_BY_GDT663_NO_NEW_CARD", "OPEN"
        strict = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        score = int(row["known_tokens"]) * 1_000_000 + strict * 10_000 - int(row["token_count"]) * 100
        line = by_line[str(row["locus"])]
        proposed_glosses = split_pipe(row["token_glosses_de"])
        proposed_glosses[ordinal - 1] = proposal
        one_rows.append({
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis, "proposal_strength": strength,
            "proposed_complete_translation_de": line_translation(
                str(row["locus"]), line, proposed_glosses, y_occurrence_by_token,
                inherited_target_by_token, target_by_token,
            ),
        })
    one_rows.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for rank, row in enumerate(one_rows, 1):
        row["rank"] = rank

    glossary_rows: list[dict[str, object]] = [dict(row) for row in base_glossary_rows]
    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for spec_row in EXACT_WHOLE_SPECS:
        surface = spec_row["surface"]
        glossary_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "source": "GDT663:FREE_SIGLUM_DEFAULT" if surface == "l" else "GDT663:EXACT_WHOLE",
            "strength": card_strength(surface),
            "scope_state": "KNOWN_CONTEXT_LICENSED" if surface == "l" else "KNOWN_EXACT_WHOLE",
            "priority": 230,
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT663_DEFAULT", "kind": card_type(surface),
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "context_rule": (
                "free reader-exact token or fallback after alternate-reader merge search" if surface == "l"
                else "only the exact whitespace-delimited surface; no substring inheritance"
            ),
            "status": "NEW_V40_PROVISIONAL_CONCRETE_RECIPE_DEFAULT",
        })
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if len(glossary_rows) != 734:
        raise RuntimeError("V40 glossary dimension drift")

    context_cards: list[dict[str, object]] = []
    context_keys = sorted({
        (str(row["rendering_class"]), str(row["surface"]), str(row["reader_merge_surface"]), str(row["working_render_de"]))
        for row in occurrence_rows if row["rendering_class"] != "EXACT_WHOLE"
    })
    for klass, surface, merge_surface, render in context_keys:
        members = [
            row for row in occurrence_rows
            if row["rendering_class"] == klass and row["surface"] == surface
            and row["reader_merge_surface"] == merge_surface and row["working_render_de"] == render
        ]
        context_cards.append({
            "card_id": f"G663-C{len(context_cards) + 1:03d}", "rendering_class": klass,
            "surface": surface, "reader_merge_surface": merge_surface, "occurrences": len(members),
            "working_render_de": render,
            "selection_rule": "exact token and listed context; l additionally requires the recorded alternate-reader join",
            "semantic_effect": "practical rendering only; the structural composition remains separately visible",
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT663_{klass}_{merge_surface}", "kind": "PRACTICAL_RENDERING_CARD",
            "working_meaning_de": render, "composition": f"{klass}:{merge_surface}",
            "context_rule": "exact occurrence context; reader join where named",
            "status": "NEW_V40_CONTEXT_RENDER",
        })

    architecture_rows: list[dict[str, object]] = []
    for kind in (
        "PRODUCTIVE_COMPOUND", "ENTRY_COMPOSITE", "LEARNED_ACTION_WHOLE", "LEARNED_WHOLE",
        "CONTEXT_SCOPED_LEARNED_SIGLUM",
    ):
        surfaces = [surface for surface in TARGET_ORDER if card_type(surface) == kind]
        architecture_rows.append({
            "card_type": kind, "surface_types": len(surfaces),
            "positions": sum(EXPECTED_SURFACE_COUNTS[surface] for surface in surfaces),
            "surfaces": "|".join(surfaces),
            "dispatch_rule": "exact whole; free l additionally uses alternate-reader boundary cards",
        })

    base_complete_loci = {row["locus"] for row in base_complete}
    newly_completed = [dict(row) for row in complete_rows if row["locus"] not in base_complete_loci]
    newly_completed.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_completed, 1):
        row["rank"] = rank
    base_one_loci = {row["locus"] for row in base_one}
    newly_one = [dict(row) for row in one_rows if row["locus"] not in base_one_loci]
    newly_one.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_one, 1):
        row["rank"] = rank
        row["base_unknown_tokens"] = base_by_locus[str(row["locus"])]["unknown_tokens"]

    audit_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for occurrence in occurrence_rows:
        locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        audit_rows.append({
            **occurrence,
            "v39_gloss_de": split_pipe(base_row["token_glosses_de"])[ordinal - 1],
            "v40_gloss_de": split_pipe(final_row["token_glosses_de"])[ordinal - 1],
            "v39_scope_state": split_pipe(base_row["scope_states"])[ordinal - 1],
            "v40_scope_state": split_pipe(final_row["scope_states"])[ordinal - 1],
            "v40_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "exact_surface_dispatch": int(occurrence["surface"] != "l"),
            "context_or_reader_dispatch": int(occurrence["surface"] == "l"),
            "substring_dispatch": 0,
        })
        reader_rows.append({
            "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"], "locus": locus,
            "ordinal": ordinal, "surface": occurrence["surface"], "position": occurrence["position"],
            "reader_exact": occurrence["reader_exact"], "split_normalized": occurrence["split_normalized"],
            "reader_merge_direction": occurrence["reader_merge_direction"],
            "reader_merge_surface": occurrence["reader_merge_surface"],
            "all_present_exact": occurrence["all_present_exact"], "zl3b_line": occurrence["zl3b_line"],
            "it2a_line": occurrence["it2a_line"], "rf1b_line": occurrence["rf1b_line"],
            "claim_boundary": "reader agreement selects boundary confidence or an l-merge card; it does not identify plaintext",
        })
    if any(str(row["v39_gloss_de"]) != f"[{row['surface']}:?]" for row in audit_rows):
        raise RuntimeError("not every target occurrence was open in V39")
    if any(GENERIC_FILLER.search(str(row["v40_working_translation_de"])) for row in audit_rows):
        raise RuntimeError("generic work filler leaked into GDT663")
    if any("Eigenschafts-/Zustands-/Materialträger" in str(row["v40_working_translation_de"]) for row in audit_rows):
        raise RuntimeError("structural OL meta-gloss leaked into practical V40 prose")

    decision_rows: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    for index, spec_row in enumerate(EXACT_WHOLE_SPECS, 1):
        surface = spec_row["surface"]
        members = [row for row in occurrence_rows if row["surface"] == surface]
        decision_rows.append({
            "decision_id": f"G663-D{index:03d}", "surface": surface, "family": spec_row["family"],
            "card_type": card_type(surface), "working_default_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in members),
            "rendering_classes": "|".join(sorted({str(row["rendering_class"]) for row in members})),
            "strength": card_strength(surface), "status": "ACCEPT_V40_REPLACEABLE",
        })
        accepted_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "card_type": card_type(surface), "strength": card_strength(surface), "occurrences": len(members),
            "scope": "CONTEXT_SCOPED_READER_BOUNDARY" if surface == "l" else "EXACT_WHITESPACE_DELIMITED_WHOLE",
            "status": "ACCEPT_V40_REPLACEABLE",
        })

    family_rows: list[dict[str, object]] = []
    for family in sorted({row["family"] for row in EXACT_WHOLE_SPECS}):
        for surface in [row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == family]:
            members = tokens_by_surface[surface]
            family_rows.append({
                "family": family, "surface": surface, "card_type": card_type(surface),
                "occurrences": len(members), "lines": len({row["locus"] for row in members}),
                "pages": len({row["page"] for row in members}),
                "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "claim_scope": "exact whole; composition predicts relatives only as a future explicit card",
            })

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted(affected_loci):
        members = [row for row in occurrence_rows if row["locus"] == locus]
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        target_line_rows.append({
            "page": final_row["page"], "locus": locus, "section": final_row["section"],
            "target_occurrences": len(members), "target_ordinals": "|".join(str(row["ordinal"]) for row in members),
            "target_surfaces": "|".join(str(row["surface"]) for row in members),
            "rendering_classes": "|".join(str(row["rendering_class"]) for row in members),
            "zl3b_line": final_row["zl3b_line"], "v39_token_glosses_de": base_row["token_glosses_de"],
            "v40_token_glosses_de": final_row["token_glosses_de"],
            "v40_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "v39_unknown_tokens": base_row["unknown_tokens"], "v40_unknown_tokens": final_row["unknown_tokens"],
            "v40_complete": int(int(final_row["unknown_tokens"]) == 0),
        })

    frontier_rows: list[dict[str, object]] = []
    occurrence_by_locus_ordinal = {
        (str(row["locus"]), int(row["ordinal"])): row for row in occurrence_rows
    }
    for row in frontier:
        surface, locus, ordinal = row["unknown_surface"], row["locus"], int(row["unknown_ordinal"])
        final_row = coverage_by_locus[locus]
        occurrence = occurrence_by_locus_ordinal[locus, ordinal]
        frontier_rows.append({
            "rank": row["rank"], "page": row["page"], "locus": locus, "surface": surface,
            "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
            "practical_render_de": occurrence["working_render_de"],
            "card_type": card_type(surface), "composition": EXACT_BY_SURFACE[surface]["composition"],
            "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
            "strength": card_strength(surface), "reader_merge_surface": occurrence["reader_merge_surface"],
            "zl3b_line": row["zl3b_line"], "v39_translation_de": row["proposed_complete_translation_de"],
            "v40_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "status": "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT",
        })
    if len(frontier_rows) != 105 or any(f"[{row['surface']}:?]" in str(row["v40_translation_de"]) for row in frontier_rows):
        raise RuntimeError("a GDT662 frontier slot remained open")

    base_metrics = metrics(base_coverage, base_one, base_complete, base_glossary_rows)
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 19312, "unknown_token_positions": 13027,
        "complete_multi_token_lines": 331, "strict_complete_lines": 125,
        "one_unknown_lines": 302, "strict_one_unknown_lines": 67, "working_glossary_surfaces": 632,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"V39 base metrics drift: {base_metrics!r}")
    round_rows = [
        {"version": "V39", "added_cards": "BASE", "dictionary_entries": len(base_dictionary), **base_metrics},
        {"version": "V40", "added_cards": f"102_DEFAULTS+{len(context_cards)}_RENDERINGS",
         "dictionary_entries": len(dictionary_rows), **final_metrics},
    ]

    coverage_fields, complete_fields, one_fields = list(base_coverage[0]), list(base_complete[0]), list(base_one[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_rows, list(accepted_rows[0]))
    write_tsv(output_dir / "CONTEXT_RENDERING_CARDS.tsv", context_cards, list(context_cards[0]))
    write_tsv(output_dir / "CARD_ARCHITECTURE_SUMMARY.tsv", architecture_rows, list(architecture_rows[0]))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", reader_rows, list(reader_rows[0]))
    write_tsv(output_dir / "FAMILY_COMPOSITION_ATLAS.tsv", family_rows, list(family_rows[0]))
    write_tsv(output_dir / "FRONTIER_102_COMPLETIONS.tsv", frontier_rows, list(frontier_rows[0]))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, list(target_line_rows[0]))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, ["base_unknown_tokens", *one_fields])
    write_tsv(output_dir / "V40_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))
    write_tsv(output_dir / "WORKING_DICTIONARY_V40.tsv", dictionary_rows, list(base_dictionary[0]))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V40.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V40.tsv", complete_rows, complete_fields)
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V40.tsv", one_rows, one_fields)

    input_paths = (
        G662 / "REPORT.md", G662 / "artifacts/RESULT.json", G662 / "artifacts/PAGE_ALLOWLIST.tsv",
        G662 / "artifacts/V39_WORKING_TOKEN_GLOSSARY.tsv", G662 / "artifacts/WORKING_DICTIONARY_V39.tsv",
        G662 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V39.tsv", G662 / "artifacts/COMPLETE_PASSAGES_V39.tsv",
        G662 / "artifacts/ONE_UNKNOWN_PASSAGES_V39.tsv", G662 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        G662 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g662.G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g662.g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g662.g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv", TOKENS_REL, CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT663_ONE_HUNDRED_TWO_RESIDUAL_FAMILY_COMPLETION_RESULT_V1",
        "experiment_id": "GDT663", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST", "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "targets": {
            "surface_types": len(TARGET_SURFACES), "positions": len(occurrence_rows),
            "lines": len(affected_loci), "pages": len({row["page"] for row in occurrence_rows}),
            "surface_counts": observed_counts,
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in occurrence_rows),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in occurrence_rows),
            "rendering_classes": dict(sorted(context_counts.items())), "all_positions_concrete": True,
            "substring_dispatch_positions": 0,
        },
        "free_l": {
            "positions": len(l_rows), "reader_exact_positions": sum(int(row["reader_exact"]) for row in l_rows),
            "alternate_reader_or_contextual_positions": sum(not int(row["reader_exact"]) for row in l_rows),
            "merge_classes": dict(sorted(l_merge_counts.items())),
            "free_default": "Pfund / Gewichtseinheit", "bound_l_stem": "Holzdroge",
        },
        "architecture": {
            row["card_type"]: {"surface_types": row["surface_types"], "positions": row["positions"]}
            for row in architecture_rows
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics, "affected_lines": len(affected_loci),
            "newly_completed_lines": len(newly_completed),
            "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one),
            "newly_exposed_one_hole_loci": sorted(row["locus"] for row in newly_one),
            "non_target_token_positions_unchanged": len(non_target_before),
            "non_target_before_sha256": non_target_sha,
            "non_target_after_sha256": canonical_hash(non_target_after),
            "non_target_exactly_unchanged": True,
        },
        "working_dictionary": {
            "v39_entries": len(base_dictionary), "v40_entries": len(dictionary_rows),
            "added_default_entries": len(EXACT_WHOLE_SPECS), "added_rendering_entries": len(context_cards),
            "v39_glossary_surfaces": len(base_glossary_rows), "v40_glossary_surfaces": len(glossary_rows),
        },
        "frontier": {"source_rows": len(frontier), "completed_rows": len(frontier_rows), "unfilled_target_slots": 0},
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True, "exact_whole_dispatch_requires_token_equality": True,
            "reader_merge_dispatch_requires_attested_alternate_token": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory replaceable concrete defaults for 102 V39 residual surfaces at 1105 inherited positions. "
            "Productive compounds, learned actions and learned wholes coexist. Free l has a pound/weight default only "
            "outside reader-supported joins; bound l remains the inherited wood head. Alkali, salt, wooden vessel, "
            "residue and long rest are deliberately low-confidence but concrete working hypotheses. Practical German "
            "renderers do not alter the structural glossary. No confirmed plaintext, language, phonetics, exact plant "
            "identity, disease, new page, image, f1r, f84 or f84r is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=ART)
    args = parser.parse_args(argv)
    result = build(args.artifact_dir)
    if args.artifact_dir.resolve() == ART.resolve():
        with tempfile.TemporaryDirectory(prefix="gdt663_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        f"GDT663 built: targets={result['targets']['positions']} surfaces=102 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']} "
        f"one_hole={result['coverage']['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
