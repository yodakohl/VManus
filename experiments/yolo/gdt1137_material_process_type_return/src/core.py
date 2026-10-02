"""GDT1137 finite LOCAL C0 core. No parser, corpus, or physical execution."""
from copy import deepcopy

MATERIALS = {
    "che": {"kind": "powder-form feedstock", "form": "granular"},
    "she": {"kind": "sheet-form feedstock", "form": "laminar"},
}
STATES = {
    "ey": {"stage": "source preparation", "operations": []},
    "dy": {"stage": "converted preparation", "operations": ["surface-convert"]},
}
LICENSES = {"cheey": ("che", "ey"), "chedy": ("che", "dy"),
            "sheey": ("she", "ey"), "shedy": ("she", "dy")}


def nominal(root, state, *, materials=None, states=None):
    """One shared material/state constructor for exactly four licensed forms."""
    material = deepcopy((MATERIALS if materials is None else materials)[root])
    transform = deepcopy((STATES if states is None else states)[state])
    return {"surface": root + state, "sort": "preparation recipe",
            "material": material, "stage": transform["stage"],
            "operations": transform["operations"],
            "prepared_form": material["form"] + ":" + transform["stage"]}


def lexical_nominal(surface, **kwargs):
    root, state = LICENSES[surface]
    return nominal(root, state, **kwargs)


def qokedy(recipe, producer_id):
    """Specify a product TYPE from the supplied converted recipe, never a batch."""
    if recipe["sort"] != "preparation recipe" or recipe["stage"] != "converted preparation":
        raise ValueError("QOKEDY requires a converted preparation recipe")
    material = deepcopy(recipe["material"])
    operations = list(recipe["operations"])
    if not operations:
        raise ValueError("converted recipe has no declared operation")
    return {"sort": "product type", "producer_id": producer_id,
            "material": material, "operations": operations,
            "prepared_form": material["form"] + ":" + "+".join(operations),
            "genealogy": {"source_material": deepcopy(material),
                          "recipe_operations": list(operations)},
            "ontological_status": "prescribed type; no production or batch asserted"}


def sol(product_types, embedded_recipe, policy):
    """Literal SOL + CHEDY; reference to actual generated objects, no reseeding."""
    if not product_types:
        raise ValueError("SOL has no previously generated type")
    if policy == "explicit-earlier-type":
        matches = [t for t in product_types[:-1]
                   if t["material"] == embedded_recipe["material"]
                   and t["operations"] == embedded_recipe["operations"]]
        if not matches:
            raise ValueError("SOL's written earlier recipe has no matching generated type")
        selected = matches[0]
    elif policy == "latest-product-only":
        selected = product_types[-1]
    else:
        raise ValueError("unknown fixed reference policy")
    return {"surface": "sol" + embedded_recipe["surface"], "selected_type": selected,
            "policy": policy, "written_type_matches":
                selected["material"] == embedded_recipe["material"]
                and selected["operations"] == embedded_recipe["operations"]}


def source_predicate(selected_type, source_recipe):
    """Late CHEEY asserts the returned patient's source, reading its actual field."""
    if source_recipe["stage"] != "source preparation":
        raise ValueError("source predicate needs EY source recipe")
    return {"predicate": "has-source-preparation", "patient_producer": selected_type["producer_id"],
            "actual_material": deepcopy(selected_type["material"]),
            "written_material": deepcopy(source_recipe["material"]),
            "satisfied": selected_type["material"] == source_recipe["material"]}


def qody(selected_type):
    """Emit a further dry-setting prescription from the actual returned type."""
    return {"sort": "further preparation prescription",
            "parent_producer": selected_type["producer_id"],
            "material": deepcopy(selected_type["material"]),
            "operations": list(selected_type["operations"]) + ["dry-set"],
            "prepared_form": selected_type["material"]["form"] + ":"
                             + "+".join(selected_type["operations"] + ["dry-set"]),
            "ontological_status": "prescription; no event or same-batch identity asserted"}
