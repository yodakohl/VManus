#!/usr/bin/env python3
"""Exploratory owner-bound name defaults used by GDT585.

The keys are GDT581 analysis keys, not proposed pronunciations or portable
Voynich lexemes.  Concrete German values are replaceable house readings.
"""

from __future__ import annotations

from typing import Any


DRUG_TYPES: dict[str, dict[str, str]] = {
    "yd": {
        "default_de": "Honigvorrat",
        "semantic_family": "APOTHECARY_CONTAINER_DEFAULT",
        "name_role": "CONTAINER_CONTENT_HEAD",
        "substance_head_de": "Honig",
        "plant_part_de": "NONE",
        "composition_atom_de": "Bindemittelvorrat",
        "legacy_house_alias_de": "Honig",
        "working_basis": "IMAGE_CONTAINER__LEGACY_ALIAS_RETAINED",
        "strongest_rival_de": "anderer Arzneivorrat im Gefäß",
    },
    "cheo": {
        "default_de": "dunkle Faserwurzeldroge",
        "semantic_family": "CHEO_FIBRE_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "CHEO-Pflanzendroge",
        "plant_part_de": "Faserwurzel",
        "composition_atom_de": "Faserwurzeltyp CHEO",
        "legacy_house_alias_de": "Essig",
        "working_basis": "IMAGE_PLANT_FRAGMENT__FORMAL_CHEO_FAMILY",
        "strongest_rival_de": "Essig als alter Werkstattalias",
    },
    "cphe": {
        "default_de": "knollige Wurzeldroge mit Blatttrieb",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "CPHE-Pflanzendroge",
        "plant_part_de": "Knollenwurzel mit Blatttrieb",
        "composition_atom_de": "Knollenwurzel",
        "legacy_house_alias_de": "Milch",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Milch als alter Werkstattalias",
    },
    "ody": {
        "default_de": "blühende Knollenwurzel",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "ODY-Pflanzendroge",
        "plant_part_de": "Ring- oder Knollenwurzel",
        "composition_atom_de": "blühende Knollenwurzel",
        "legacy_house_alias_de": "Bienenwachs",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Bienenwachs als alter Werkstattalias",
    },
    "or": {
        "default_de": "helle Wurzeldroge",
        "semantic_family": "OTORA_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_OR_STOCK_HEAD",
        "substance_head_de": "helle OR-Wurzeldroge",
        "plant_part_de": "Wurzel",
        "composition_atom_de": "helle Wurzeldroge",
        "legacy_house_alias_de": "Olivenöl",
        "working_basis": "IMAGE_ROOT_AND_CONTAINER__CROSS_PAGE_REPEAT",
        "strongest_rival_de": "Olivenöl als alter Werkstattalias",
    },
    "ora": {
        "default_de": "mehrfingrige Blütenwurzel",
        "semantic_family": "OTORA_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "ORA-Wurzeldroge",
        "plant_part_de": "mehrfingrige Blütenwurzel",
        "composition_atom_de": "OTORA-Wurzelvariante",
        "legacy_house_alias_de": "Eiweiß",
        "working_basis": "IMAGE_PLANT_FRAGMENT__FORMAL_OTORA_FAMILY",
        "strongest_rival_de": "Eiweiß als alter Werkstattalias",
    },
    "cheosdy": {
        "default_de": "gebänderte Faserwurzel der CHEO-Familie",
        "semantic_family": "CHEO_FIBRE_ROOT_FAMILY",
        "name_role": "BOTANICAL_FAMILY_VARIANT",
        "substance_head_de": "CHEO-Pflanzendroge",
        "plant_part_de": "gebänderte Faserwurzel",
        "composition_atom_de": "CHEO-Wurzelvariante",
        "legacy_house_alias_de": "Eigelb",
        "working_basis": "IMAGE_PLANT_FRAGMENT__FORMAL_CHEO_FAMILY",
        "strongest_rival_de": "Eigelb als alter Werkstattalias",
    },
    "d": {
        "default_de": "Wurzeldroge",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "ROOT_PART_ATOM",
        "substance_head_de": "ownerlokale Pflanzendroge",
        "plant_part_de": "Wurzel",
        "composition_atom_de": "Wurzel",
        "legacy_house_alias_de": "Wasser",
        "working_basis": "FOUR_ROOT_IMAGES__TWO_CONTAINER_OCCURRENCES__COMPOUND_GRAPH",
        "strongest_rival_de": "Wasser als alter Werkstattanker",
    },
    "am": {
        "default_de": "Salbengrundlage",
        "semantic_family": "PREPARATION_BASE",
        "name_role": "COMPOUND_BASE_ATOM",
        "substance_head_de": "Fettgrundlage",
        "plant_part_de": "NONE",
        "composition_atom_de": "Salbengrundlage",
        "legacy_house_alias_de": "Schmalz",
        "working_basis": "D_PLUS_AM_COMPOUND__LEGACY_BASE_ALIAS",
        "strongest_rival_de": "Schmalz",
    },
    "y": {
        "default_de": "Krautdroge",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "AERIAL_PLANT_ATOM",
        "substance_head_de": "ownerlokale Pflanzendroge",
        "plant_part_de": "Kraut oder oberirdischer Teil",
        "composition_atom_de": "Kraut- oder Pflanzenform",
        "legacy_house_alias_de": "Wein",
        "working_basis": "THREE_PLANT_IMAGES__REPEATED_COMPOUNDS",
        "strongest_rival_de": "Wein als alter Werkstattanker",
    },
    "dordy": {
        "default_de": "große Speicherwurzel",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "DORDY-Pflanzendroge",
        "plant_part_de": "Speicherwurzel",
        "composition_atom_de": "Speicherwurzel",
        "legacy_house_alias_de": "Butter",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Butter als alter Werkstattalias",
    },
    "da": {
        "default_de": "langblättrige Mutterpflanze DA",
        "semantic_family": "LEARNED_PLANT_HEAD",
        "name_role": "PLANT_TAXON_ATOM",
        "substance_head_de": "Pflanzenkern DA",
        "plant_part_de": "ganze Mutterpflanze",
        "composition_atom_de": "Pflanzenname DA",
        "legacy_house_alias_de": "Mehl",
        "working_basis": "D_PLUS_DA_PART_OF_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Mehl als alter Werkstattalias",
    },
    "qk": {
        "default_de": "große helle Speicherwurzel",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "QK-Pflanzendroge",
        "plant_part_de": "Speicherwurzel",
        "composition_atom_de": "helle Speicherwurzel",
        "legacy_house_alias_de": "Asche",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Asche als alter Werkstattalias",
    },
    "dy": {
        "default_de": "blühende Wurzeldroge",
        "semantic_family": "D_Y_ROOT_HERB_FAMILY",
        "name_role": "ROOT_WITH_AERIAL_FORM",
        "substance_head_de": "DY-Pflanzendroge",
        "plant_part_de": "blühende Wurzelpflanze",
        "composition_atom_de": "Wurzel mit Krautform",
        "legacy_house_alias_de": "Kalk",
        "working_basis": "OTOLD_VS_OTOLDY_MINIMAL_PAIR__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Kalk als alter Werkstattalias",
    },
    "cho": {
        "default_de": "zweifarbige Langwurzel",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "CHO-Pflanzendroge",
        "plant_part_de": "Langwurzel",
        "composition_atom_de": "zweifarbige Langwurzel",
        "legacy_house_alias_de": "Schwefel",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Schwefel als alter Werkstattalias",
    },
    "yko": {
        "default_de": "Arzneivorrat",
        "semantic_family": "APOTHECARY_CONTAINER_DEFAULT",
        "name_role": "CONTAINER_CONTENT_HEAD",
        "substance_head_de": "Alaun oder anderer Arzneivorrat",
        "plant_part_de": "NONE",
        "composition_atom_de": "Gefäßvorrat",
        "legacy_house_alias_de": "Alaun",
        "working_basis": "IMAGE_CONTAINER__LEGACY_ALIAS_RETAINED_AS_CANDIDATE",
        "strongest_rival_de": "Alaunvorrat",
    },
    "s": {
        "default_de": "Blattdroge",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "LEAF_PART_ATOM",
        "substance_head_de": "ownerlokale Pflanzendroge",
        "plant_part_de": "Blatt oder Kraut",
        "composition_atom_de": "Blatt oder Kraut",
        "legacy_house_alias_de": "Salz",
        "working_basis": "TWO_PLANT_IMAGES__MULTI_PART_COMPOUNDS",
        "strongest_rival_de": "Salz als alter Werkstattanker",
    },
    "sy": {
        "default_de": "Blütenstand",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "INFLORESCENCE_PART_ATOM",
        "substance_head_de": "Y-Krautdroge",
        "plant_part_de": "Blüten- oder Fruchtstand",
        "composition_atom_de": "Blütenstand",
        "legacy_house_alias_de": "Vitriol",
        "working_basis": "SY_PLUS_Y_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Vitriol als alter Werkstattalias",
    },
    "od": {
        "default_de": "Harzvorrat",
        "semantic_family": "APOTHECARY_CONTAINER_DEFAULT",
        "name_role": "CONTAINER_CONTENT_HEAD",
        "substance_head_de": "Harz",
        "plant_part_de": "NONE",
        "composition_atom_de": "Harzvorrat",
        "legacy_house_alias_de": "Harz",
        "working_basis": "IMAGE_CONTAINER__LEGACY_ALIAS_RETAINED",
        "strongest_rival_de": "anderer Trockenvorrat im Gefäß",
    },
    "opchos": {
        "default_de": "lange Faserwurzel",
        "semantic_family": "CHOS_CHOR_FIBRE_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "OPCHOS-Pflanzendroge",
        "plant_part_de": "lange Faserwurzel",
        "composition_atom_de": "CHOS-Faserwurzel",
        "legacy_house_alias_de": "Gummi arabicum",
        "working_basis": "IMAGE_ROOT__FORMAL_CHOS_CHOR_FAMILY",
        "strongest_rival_de": "Gummi arabicum als alter Werkstattalias",
    },
    "oiin": {
        "default_de": "Wurzelstock",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "RHIZOME_PART_ATOM",
        "substance_head_de": "E-Pflanzendroge",
        "plant_part_de": "Wurzelstock",
        "composition_atom_de": "Wurzelstock",
        "legacy_house_alias_de": "Myrrhe",
        "working_basis": "S_PLUS_OIIN_PLUS_E_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Myrrhe als alter Werkstattalias",
    },
    "e": {
        "default_de": "breitblättrige Mutterpflanze E",
        "semantic_family": "LEARNED_PLANT_HEAD",
        "name_role": "PLANT_TAXON_ATOM",
        "substance_head_de": "Pflanzenkern E",
        "plant_part_de": "ganze Mutterpflanze",
        "composition_atom_de": "Pflanzenname E",
        "legacy_house_alias_de": "Weihrauch",
        "working_basis": "S_PLUS_OIIN_PLUS_E_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Weihrauch als alter Werkstattalias",
    },
    "opchor": {
        "default_de": "haarige Faserwurzel",
        "semantic_family": "CHOS_CHOR_FIBRE_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "OPCHOR-Pflanzendroge",
        "plant_part_de": "haarige Faserwurzel",
        "composition_atom_de": "CHOR-Faserwurzel",
        "legacy_house_alias_de": "Safranblüte",
        "working_basis": "IMAGE_ROOT__FORMAL_CHOS_CHOR_FAMILY",
        "strongest_rival_de": "Safranblüte als alter Werkstattalias",
    },
    "opor": {
        "default_de": "helle Fingerwurzel",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "OPOR-Pflanzendroge",
        "plant_part_de": "Fingerwurzel",
        "composition_atom_de": "helle Fingerwurzel",
        "legacy_house_alias_de": "Pfefferkorn oder Samen",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Pfefferkorn oder Samen als alter Werkstattalias",
    },
    "dchos": {
        "default_de": "rote Fingerwurzel",
        "semantic_family": "CHOS_CHOR_FIBRE_ROOT_FAMILY",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "DCHOS-Pflanzendroge",
        "plant_part_de": "rote Fingerwurzel",
        "composition_atom_de": "CHOS-Fingerwurzel",
        "legacy_house_alias_de": "Ingwerwurzel",
        "working_basis": "TWO_LINE_BOUNDARY_LABEL__FORMAL_CHOS_CHOR_FAMILY",
        "strongest_rival_de": "Ingwerwurzel",
    },
    "yor": {
        "default_de": "Trockendroge",
        "semantic_family": "APOTHECARY_BOUNDARY_DEFAULT",
        "name_role": "CONTAINER_OR_DRUG_HEAD",
        "substance_head_de": "YOR-Trockendroge",
        "plant_part_de": "Rinde möglich",
        "composition_atom_de": "Rinden- oder Trockenvorrat",
        "legacy_house_alias_de": "Zimtrinde",
        "working_basis": "TWO_LINE_BOUNDARY_LABEL__LEGACY_ALIAS_RETAINED_AS_CANDIDATE",
        "strongest_rival_de": "Zimtrinde",
    },
    "ak": {
        "default_de": "rundblättrige Knollendroge",
        "semantic_family": "ROOT_DRUG",
        "name_role": "BOTANICAL_DRUG_HEAD",
        "substance_head_de": "AK-Pflanzendroge",
        "plant_part_de": "Knolle mit Rundblättern",
        "composition_atom_de": "Knollendroge",
        "legacy_house_alias_de": "Gewürznelkenknospe",
        "working_basis": "IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Gewürznelkenknospe als alter Werkstattalias",
    },
    "yt": {
        "default_de": "Blattdroge",
        "semantic_family": "COMPOSITIONAL_PLANT_PART",
        "name_role": "LEAF_PART_ATOM",
        "substance_head_de": "EM-Pflanzendroge",
        "plant_part_de": "Blatt",
        "composition_atom_de": "Blatt",
        "legacy_house_alias_de": "Salbeiblatt",
        "working_basis": "YT_PLUS_EM_PART_OF_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Salbeiblatt",
    },
    "em": {
        "default_de": "grauwurzelige Mutterpflanze EM",
        "semantic_family": "LEARNED_PLANT_HEAD",
        "name_role": "PLANT_TAXON_ATOM",
        "substance_head_de": "Pflanzenkern EM",
        "plant_part_de": "ganze Mutterpflanze",
        "composition_atom_de": "Pflanzenname EM",
        "legacy_house_alias_de": "Rautenblatt",
        "working_basis": "YT_PLUS_EM_PART_OF_COMPOSITION__IMAGE_PLANT_FRAGMENT",
        "strongest_rival_de": "Raute als Pflanzenidentität",
    },
}


BATH_TYPES: dict[str, dict[str, str]] = {
    "d": {
        "default_de": "Endfigur",
        "semantic_family": "SYMMETRIC_HUMAN_TERMINAL",
        "name_role": "COMMON_END_STATION_CLASS",
        "composition_atom_de": "Endfigur d",
        "legacy_house_alias_de": "Ablauf",
        "working_basis": "TWO_SYMMETRIC_HUMAN_END_LABELS",
        "strongest_rival_de": "Ablauf oder Endstelle",
    },
    "chd": {
        "default_de": "linker Speiseanschluss",
        "semantic_family": "LEFT_SOURCE_CONNECTION",
        "name_role": "LEFT_TERMINAL_SUBCLASS",
        "composition_atom_de": "linker Speiseanschluss",
        "legacy_house_alias_de": "erwärmtes Becken",
        "working_basis": "LEFT_SOURCE_SIDE_IN_D_PLUS_CHD_END_LABEL",
        "strongest_rival_de": "erwärmtes Becken",
    },
    "kchs": {
        "default_de": "linker Anschlusskopf",
        "semantic_family": "LEFT_INNER_CONNECTION_HEAD",
        "name_role": "INNER_CONNECTION_HEAD",
        "composition_atom_de": "linker Anschlusskopf",
        "legacy_house_alias_de": "Zulaufrohr",
        "working_basis": "FIRST_INNER_HEAD_AFTER_LEFT_TERMINAL",
        "strongest_rival_de": "Zulaufrohr",
    },
    "ork": {
        "default_de": "mittlerer Tropfkopf",
        "semantic_family": "CENTRAL_DRIP_OUTLET_HEAD",
        "name_role": "INNER_OUTLET_HEAD",
        "composition_atom_de": "mittlerer Tropfkopf",
        "legacy_house_alias_de": "Badebecken",
        "working_basis": "TEXT_BELOW_DARK_BLUE_DRIPPING_HEAD__NO_BASIN",
        "strongest_rival_de": "Badebecken",
    },
    "sor": {
        "default_de": "rechter Sprühkopf",
        "semantic_family": "RIGHT_TARGET_SPRAY_HEAD",
        "name_role": "INNER_TARGET_HEAD",
        "composition_atom_de": "rechter Sprühkopf",
        "legacy_house_alias_de": "Sitz- oder Behandlungsstation",
        "working_basis": "RIGHT_INNER_HEAD_WITH_AL_TARGET_FRAME__NO_VISIBLE_SEAT",
        "strongest_rival_de": "Sitz- oder Behandlungsstation",
    },
    "edy": {
        "default_de": "rechter Endanschluss",
        "semantic_family": "RIGHT_EXTRACTION_TERMINAL",
        "name_role": "RIGHT_TERMINAL_SUBCLASS",
        "composition_atom_de": "rechter Endanschluss",
        "legacy_house_alias_de": "Kühlablauf",
        "working_basis": "RIGHT_HUMAN_ENDPOINT_IN_D_PLUS_EDY_LABEL__NO_COOLING_MARK",
        "strongest_rival_de": "Kühlablauf",
    },
}


PLANT_TYPES: dict[str, dict[str, str]] = {
    "eeeon": {
        "default_de": "rechte Blütenform",
        "semantic_family": "ONE_PICTURED_PLANT_TWO_FLOWER_FORMS",
        "name_role": "OT_MARKED_RIGHT_FLOWER_FORM",
        "composition_atom_de": "rechte Blütenform B",
        "legacy_house_alias_de": "ganze blühende Heilpflanze",
        "working_basis": "ONE_ROOT_ONE_STEM__LABEL_NEXT_TO_RIGHT_SIDE_FLOWER",
        "strongest_rival_de": "weiterer Pflanzenname oder Beiname derselben Art",
    },
    "oiil": {
        "default_de": "linke Blütenform",
        "semantic_family": "ONE_PICTURED_PLANT_TWO_FLOWER_FORMS",
        "name_role": "PLAIN_LEFT_FLOWER_FORM",
        "composition_atom_de": "linke Blütenform A",
        "legacy_house_alias_de": "ganze Heilpflanze B",
        "working_basis": "ONE_ROOT_ONE_STEM__LABEL_NEXT_TO_LEFT_SIDE_FLOWER",
        "strongest_rival_de": "Hauptname derselben Pflanze",
    },
}


LOCAL_X_TYPES: dict[str, dict[str, str]] = {
    "RUNNING:G515-E0410@2": {
        "default_de": "Beschwerde",
        "semantic_family": "INDICATION_OR_ILLNESS",
        "name_role": "OWNER_BOUND_INDICATION",
        "strongest_rival_de": "Indikation oder Krankheit",
        "composition_atom_de": "Beschwerdestichwort",
        "legacy_house_alias_de": "Krankheit oder Beschwerde",
        "working_basis": "OWNER_LOCAL_F66R_TEXT_BLOCK_02",
    },
    "RUNNING:G515-E0438@2": {
        "default_de": "Heilmittel",
        "semantic_family": "REMEDY_OR_HEALING",
        "name_role": "OWNER_BOUND_REMEDY",
        "strongest_rival_de": "Heilwirkung",
        "composition_atom_de": "Heilmittelstichwort",
        "legacy_house_alias_de": "Heilmittel oder Heilwirkung",
        "working_basis": "OWNER_LOCAL_F66R_TEXT_BLOCK_03",
    },
}


FAMILY_RECONCILIATIONS: tuple[dict[str, str], ...] = (
    {
        "family_id": "GDT585-F01",
        "lead_kind": "FORMAL_FAMILY",
        "surface_family": "otora",
        "member_raw_cores": "or|ora",
        "source_surfaces": "otoram|otora|otorain",
        "old_defaults_de": "Olivenöl|Eiweiß",
        "new_defaults_de": "helle Wurzeldroge|mehrfingrige Blütenwurzel",
        "decision": "ONE_VISIBLE_ROOT_DRUG_FAMILY_WITH_STOCK_AND_VARIANT",
        "reason_de": (
            "OR wiederholt sich an Gefäß und heller Wurzel; ORA sitzt an einer "
            "mehrfingrigen Blütenwurzel. Die exakte OTORA-Serie bleibt damit botanisch zusammen."
        ),
        "prediction_de": "Weitere OTORA-Mitglieder sollten Wurzelmaterial oder dessen Vorrat benennen.",
    },
    {
        "family_id": "GDT585-F02",
        "lead_kind": "FORMAL_FAMILY",
        "surface_family": "cheo",
        "member_raw_cores": "cheo|cheosdy",
        "source_surfaces": "cheocthy|cheody|cheosdy|opcheor",
        "old_defaults_de": "Essig|Eigelb",
        "new_defaults_de": "dunkle Faserwurzeldroge|gebänderte Faserwurzel der CHEO-Familie",
        "decision": "ONE_VISIBLE_FIBRE_ROOT_FAMILY",
        "reason_de": (
            "Beide Namenskerne stehen an sichtbaren Wurzelfragmenten und teilen CHEO; "
            "Essig und Eigelb werden als alte Werkstattaliase bewahrt, aber nicht mehr primär."
        ),
        "prediction_de": "Weitere CHEO-Mitglieder sollten Faserwurzelvarianten oder deren Vorrat tragen.",
    },
    {
        "family_id": "GDT585-F03",
        "lead_kind": "FORMAL_FAMILY",
        "surface_family": "chos_or_chor",
        "member_raw_cores": "cho|opchos|opchor|dchos",
        "source_surfaces": "ararchodaiin|opchosam|opchoroiin|okshdchos",
        "old_defaults_de": "Schwefel|Gummi arabicum|Safranblüte|Ingwerwurzel",
        "new_defaults_de": "zweifarbige Langwurzel|lange Faserwurzel|haarige Faserwurzel|rote Fingerwurzel",
        "decision": "VISIBLE_FIBRE_OR_FINGER_ROOT_SERIES",
        "reason_de": (
            "Die formal verwandten CHOS/CHOR-Kerne stehen sämtlich an langen, haarigen "
            "oder fingerartigen Wurzelformen; OP und D bleiben mögliche Unterserienmarker."
        ),
        "prediction_de": "CHOS/CHOR in neuen Namensslots sollte bevorzugt an faserigen Wurzelteilen stehen.",
    },
    {
        "family_id": "GDT585-F04",
        "lead_kind": "COMPOSITION_HYPOTHESIS",
        "surface_family": "otold_minimal_pair",
        "member_raw_cores": "d|dy",
        "source_surfaces": "otold|otoldy",
        "old_defaults_de": "Wasser|Kalk",
        "new_defaults_de": "Wurzeldroge|blühende Wurzeldroge",
        "decision": "WHOLE_CORE_MINIMAL_PAIR_CONTRAST__NO_D_PLUS_Y_SEGMENTATION_CLAIM",
        "reason_de": (
            "Das minimale Schalenpaar OTOLD/OTOLDY trennt den Ganzkern D von einer sichtbar "
            "blühenden DY-Form; DY wird dabei nicht automatisch als D+Y segmentiert."
        ),
        "prediction_de": "Weitere D/DY-Ganzkernpaare sollten Wurzel- und blühende Pflanzenform kontrastieren.",
    },
    {
        "family_id": "GDT585-F05",
        "lead_kind": "COMPOSITION_HYPOTHESIS",
        "surface_family": "part_of_plant_packages",
        "member_raw_cores": "d|da|s|sy|y|oiin|e|yt|em",
        "source_surfaces": "dararda|saldam|sydarary|saloiinsheol|ytarem",
        "old_defaults_de": "Wasser+Mehl|Salz+Wasser|Vitriol+Wein|Salz+Myrrhe+Weihrauch|Salbei+Raute",
        "new_defaults_de": "Wurzel-von-Pflanze|Blatt-und-Wurzel|Blütenstand-von-Kraut|Blatt-Wurzelstock-Pflanze|Blatt-von-Pflanze",
        "decision": "OCCURRENCE_LEVEL_PLANT_PART_MICROPACKAGES__NO_STRING_SEGMENTATION",
        "reason_de": (
            "Die Mehrkernlabels sitzen jeweils an einem Pflanzenfragment. Technische Hüllen "
            "bleiben erhalten, während die gelernten Kerne als Organ plus Pflanzenreferent komponieren."
        ),
        "prediction_de": "Neue Mehrkernlabels an Pflanzenfragmenten sollten wieder Organ und Mutterpflanze koppeln.",
    },
)


COMPOUND_OVERRIDES: dict[str, dict[str, str]] = {
    "G474-B001": {
        "source_kind": "TWO_LABEL_SAME_OWNER_BUNDLE",
        "semantic_mode": "TWO_FLOWER_FORMS_ONE_PICTURED_PLANT",
        "primary_reading_de": (
            "Linke Blütenform oiil; daneben als nächste die rechte Blütenform eeeon "
            "derselben einzigen Pflanze."
        ),
        "strongest_rival_de": "Hauptname und weiterer Name oder Beiname derselben Pflanzenart",
        "reason_de": (
            "Eine Wurzel, ein Stängel und eine Pflanze; die Labels stehen symmetrisch bei "
            "den beiden Seitenblütenköpfen."
        ),
    },
    "P1003-E0081": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "LEFT_HUMAN_TERMINAL_PACKAGE",
        "primary_reading_de": (
            "Am linken Quellende steht die Bedien- oder Badendenfigur d beim "
            "Quell- oder Speiseanschluss chd."
        ),
        "strongest_rival_de": "Ablauf plus erwärmtes Becken",
        "reason_de": "D und CHD teilen das linke menschliche Endlabel; kein Wärmemarker ist sichtbar.",
    },
    "P1003-E0088": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "RIGHT_HUMAN_TERMINAL_PACKAGE",
        "primary_reading_de": (
            "Am anderen Ende folgt bei der Bedien- oder Badendenfigur d der rechte "
            "Entnahme- oder Endanschluss edy."
        ),
        "strongest_rival_de": "Ablauf gefolgt von Kühlablauf",
        "reason_de": "D und EDY teilen das rechte menschliche Endlabel; kein Kühlmarker ist sichtbar.",
    },
    "P1003-E0554": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "ROOT_DRUG_IN_PREPARATION_BASE",
        "primary_reading_de": "Wurzeldroge d in oder mit Salben- oder Fettgrundlage am.",
        "strongest_rival_de": "Wasser-Schmalz-Paar nach der alten Werkstattpalette",
        "reason_de": "Das Label sitzt am Pflanzen- oder Gefäßobjekt; D ist im Bilddeck überwiegend Wurzel.",
    },
    "P1003-E0555": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "REPEATED_SAME_PLANT_REFERENCE",
        "primary_reading_de": "Derselbe Kraut- oder Pflanzenreferent y wird zweimal aufgenommen.",
        "strongest_rival_de": "zweistufige Weinzubereitung nach der alten Werkstattpalette",
        "reason_de": "Beide Slots sind Y und stehen an demselben Pflanzenfragment.",
    },
    "P1003-E0557": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "ROOT_PART_OF_NAMED_PLANT",
        "primary_reading_de": "Wurzel d der langblättrigen Mutterpflanze oder Art DA.",
        "strongest_rival_de": "Wasser-Mehl-Paste nach der alten Werkstattpalette",
        "reason_de": "Ein einziges Pflanzenfragment trägt D und DA beidseits der AR-Bezüge.",
    },
    "P1008-E1176": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "LEAF_AND_ROOT_PACKAGE",
        "primary_reading_de": "Blatt- oder Krautteil s zusammen mit der Wurzel d derselben Pflanzendroge.",
        "strongest_rival_de": "Sole oder Salzlösung nach der alten Werkstattpalette",
        "reason_de": "Das Mehrkernlabel sitzt an einem Pflanzenfragment, nicht an einer sichtbaren Flüssigkeit.",
    },
    "P1008-E1177": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "INFLORESCENCE_OF_HERB_PACKAGE",
        "primary_reading_de": "Blüten- oder Fruchtstand sy der Kraut- oder Pflanzenform y.",
        "strongest_rival_de": "vitriolhaltige Weinlösung nach der alten Werkstattpalette",
        "reason_de": "SY und Y stehen gemeinsam an einem sichtbaren Blüten- oder Fruchtstand.",
    },
    "P1008-E1182": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "THREE_PART_PLANT_INSTRUCTION",
        "primary_reading_de": (
            "Halte Blattdroge s, Wurzelstock oiin und Pflanzenkern e desselben "
            "Pflanzenfragments zum Zielgefäß und fahre fort."
        ),
        "strongest_rival_de": "Salz, Myrrhe und Weihrauch als dreiteilige Arzneimischung",
        "reason_de": "GDT474s SH+OL-Anweisung bleibt; nur die drei sichtbaren Pflanzenrollen ersetzen die Hausaliase.",
    },
    "P1008-E1412": {
        "source_kind": "MULTI_NAME_LABEL",
        "semantic_mode": "LEAF_PART_OF_NAMED_PLANT",
        "primary_reading_de": "Blattdroge yt der grauwurzligen Mutterpflanze oder Art EM.",
        "strongest_rival_de": "Salbei- und Rautenblatt als Kräutermischung",
        "reason_de": "YT und EM stehen am selben Pflanzenfragment mit AR-Teil-von-Bezug.",
    },
    "GDT585-CONTEXT-F89R-DCHOS-YOR": {
        "source_kind": "TWO_LINE_VISUAL_BOUNDARY_PAIR",
        "semantic_mode": "ROOT_AND_DRY_STOCK_BOUNDARY_PACKAGE",
        "primary_reading_de": "Rote Fingerwurzel dchos mit benachbartem Rinden- oder Trockenvorrat yor.",
        "strongest_rival_de": "Ingwerwurzel und Zimtrinde als altes Alias-Paar",
        "reason_de": "Zwei Zeilen bilden optisch ein Grenzlabel zwischen unterem Gefäß und Pflanzenfragment.",
    },
}


HISTORICAL_SOURCES: tuple[dict[str, str], ...] = (
    {
        "source_id": "GDT585-H01",
        "repository": "Wellcome Collection",
        "manuscript": "MS.5262",
        "date": "first quarter of the 15th century",
        "region": "Worcestershire, England",
        "url": "https://wellcomecollection.org/works/nuckbt25",
        "observed_practice": "129-item medical recipe collection with compound herbal remedies",
        "model_use": "supports recipe/catalogue coexistence and learned ingredient lists",
        "does_not_support": "no Voynich name or ingredient identity",
    },
    {
        "source_id": "GDT585-H02",
        "repository": "Wellcome Collection",
        "manuscript": "MS.683",
        "date": "mid 15th century",
        "region": "north-east Italy",
        "url": "https://wellcomecollection.org/works/w6ne7k4t",
        "observed_practice": "recipes explicitly combine strong vinegar, medicinal oil and wax in preparations",
        "model_use": "supports vinegar/oil/wax as one plausible workshop palette",
        "does_not_support": "no mapping to cheo, or, ora or ody",
    },
    {
        "source_id": "GDT585-H03",
        "repository": "Wellcome Collection",
        "manuscript": "MS.140",
        "date": "early 15th century",
        "region": "Italy",
        "url": "https://wellcomecollection.org/works/actgjagb",
        "observed_practice": "compilation treats medicinal waters, oils and salts beside technical operations",
        "model_use": "supports separate liquid, oil and mineral families in a technical codebook",
        "does_not_support": "no Voynich family identification",
    },
    {
        "source_id": "GDT585-H04",
        "repository": "Wellcome Collection",
        "manuscript": "MS.117",
        "date": "1462",
        "region": "Italy",
        "url": "https://wellcomecollection.org/works/abjb4cfh",
        "observed_practice": "recipe inventory names sage leaves, incense and mastic as concrete materia",
        "model_use": "supports explicit plant-part and resin/aromatic catalogue heads",
        "does_not_support": "no mapping to yt, e, oiin or another Voynich core",
    },
    {
        "source_id": "GDT585-H05",
        "repository": "Wellcome Collection",
        "manuscript": "MS.418",
        "date": "mid 15th century",
        "region": "France",
        "url": "https://wellcomecollection.org/works/f6nzyzh4",
        "observed_practice": "indexed recipes for medicinal waters made from plants",
        "model_use": "supports a learned plant name inside a reusable preparation frame",
        "does_not_support": "no Voynich plaintext or plant identity",
    },
    {
        "source_id": "GDT585-H06",
        "repository": "British Library",
        "manuscript": "Sloane MS 4016",
        "date": "about 1440",
        "region": "northern Italy",
        "url": "https://searcharchives.bl.uk/catalog/040-002116409",
        "observed_practice": "illustrated herbal with learned plant captions and synonym-like naming",
        "model_use": "supports learned whole names and alternate names beside one pictured plant",
        "does_not_support": "no identity for eeeon, oiil or a pharmaceutical core",
    },
    {
        "source_id": "GDT585-H07",
        "repository": "Wellcome Collection",
        "manuscript": "MS.574",
        "date": "early 15th century",
        "region": "northern Italy",
        "url": "https://wellcomecollection.org/works/yuykkdvs",
        "observed_practice": "illustrated herbal organized around pictured medicinal plants",
        "model_use": "supports plant-image labels as plant or plant-part nomenclature",
        "does_not_support": "no specific Voynich plant or root identification",
    },
    {
        "source_id": "GDT585-H08",
        "repository": "British Library",
        "manuscript": "Royal MS 17 A XVI",
        "date": "about 1420",
        "region": "England",
        "url": "https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Royal_MS_17_A_XVI",
        "observed_practice": "calendar layout combines positions, pictorial entries and repeating short values",
        "model_use": "supports short reusable ring values beside longer learned figure values",
        "does_not_support": "no equation of a Voynich ring core with a calendar field",
    },
    {
        "source_id": "GDT585-H09",
        "repository": "British Library",
        "manuscript": "Add MS 46143",
        "date": "1408",
        "region": "western Europe",
        "url": "https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Add_MS_46143",
        "observed_practice": "calendar entries reuse compact values inside a position-bearing page structure",
        "model_use": "supports separating a ring value from the position supplied by panel and locus",
        "does_not_support": "no recovered Voynich calendar, star name or date",
    },
    {
        "source_id": "GDT585-H10",
        "repository": "Yale University Library",
        "manuscript": "Beinecke MS 408 official scan",
        "date": "15th century manuscript; modern digital surrogate",
        "region": "Beinecke Library",
        "url": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006233",
        "observed_practice": "f88v and f89r visibly juxtapose containers and many detached plant fragments",
        "model_use": "anchors the primary image-conditioned name roles used in this atlas",
        "does_not_support": "no species or substance identification by image alone",
    },
)


def star_type_default(
    raw_core: str,
    occurrence_count: int,
    first_slot_count: int,
    later_slot_count: int,
) -> dict[str, str]:
    """Return a role-bearing catalogue value without inventing an identity."""

    display = raw_core.upper()
    if occurrence_count > 1:
        family = "SHORT_REPEATED_RING_VALUE"
        default = f"wiederkehrender Ring- oder Kalenderwert {display}"
    else:
        family = "LONG_LEARNED_RING_VALUE"
        default = f"gelernter Ringfiguren- oder Sternwert {display}"
    if first_slot_count and later_slot_count:
        slot_profile = "PRIMARY_AND_CARRIED_VALUE"
        role = "REPEATED_PRIMARY_AND_CARRIED_RING_VALUE"
    elif later_slot_count:
        slot_profile = "CARRIED_OR_ATTRIBUTE_VALUE"
        role = "CARRIED_OR_ATTRIBUTE_RING_VALUE"
    elif occurrence_count > 1:
        slot_profile = "PRIMARY_RECORD_VALUE"
        role = "REPEATED_PRIMARY_RING_VALUE"
    else:
        slot_profile = "PRIMARY_RECORD_VALUE"
        role = "LEARNED_PRIMARY_RING_VALUE"
    return {
        "default_de": default,
        "semantic_family": family,
        "name_role": role,
        "substance_head_de": "NONE",
        "plant_part_de": "NONE",
        "composition_atom_de": f"Ringwert {display}",
        "legacy_house_alias_de": "NONE",
        "working_basis": (
            f"{occurrence_count}_OCCURRENCES__{slot_profile}__POSITION_FROM_PANEL_RING_LOCUS"
        ),
        "strongest_rival_de": f"gelernter Figuren- oder Sternname {display}",
    }


def fixed_type_default(content_class: str, raw_core: str) -> dict[str, str]:
    if content_class == "DRUG_OR_INGREDIENT_OBJECT":
        return dict(DRUG_TYPES[raw_core])
    if content_class == "BATH_OR_OUTLET_STATION":
        row = dict(BATH_TYPES[raw_core])
        row.update({"substance_head_de": "NONE", "plant_part_de": "NONE"})
        return row
    if content_class == "PICTURED_PLANT":
        row = dict(PLANT_TYPES[raw_core])
        row.update(
            {
                "substance_head_de": "dieselbe abgebildete Pflanze",
                "plant_part_de": "Seitenblütenstand",
            }
        )
        return row
    raise KeyError((content_class, raw_core))


def serializable_model() -> dict[str, Any]:
    return {
        "drug_types": DRUG_TYPES,
        "bath_types": BATH_TYPES,
        "plant_types": PLANT_TYPES,
        "local_x_types": LOCAL_X_TYPES,
        "family_reconciliations": FAMILY_RECONCILIATIONS,
        "compound_overrides": COMPOUND_OVERRIDES,
        "historical_sources": HISTORICAL_SOURCES,
    }
