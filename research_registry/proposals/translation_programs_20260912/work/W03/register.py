"""Write the finite authored specification before evaluating its consequences."""
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parent
P = E.parent / 'W02'
# These are features of our German hypotheses, not decoded Voynich components.
bare = {
    'chodaiin': 'moisture:dry', 'choldar': 'moisture:dry',
    'chshoty': 'thermal:cold moisture:wet', 'kchol': 'moisture:dry',
    'kchor': 'moisture:dry', 'ocholy': 'moisture:dry',
    'okeol': 'thermal:warm', 'okeor': 'thermal:warm',
    'otaiin': 'thermal:cold', 'otal': 'thermal:cold',
    'oteol': 'thermal:cold', 'otor': 'thermal:cold',
    'qokchol': 'moisture:dry', 'qotol': 'thermal:cold',
    'sham': 'moisture:wet', 'sheo': 'moisture:wet',
    'sheol': 'moisture:wet', 'shodaiin': 'moisture:wet',
    'tod': 'thermal:cold', 'tol': 'thermal:cold',
    'ytaiin': 'thermal:cold',
}
processed = {
    'chody': 'moisture:dry', 'qokain': 'thermal:warm',
    'qokar': 'thermal:warm', 'qokchol': 'thermal:warm',
    'qokeol': 'thermal:hot', 'qokol': 'thermal:warm',
    'shocthol': 'moisture:wet', 'shody': 'moisture:wet',
    'tchol': 'moisture:dry', 'ykaiin': 'thermal:warm',
    'ytchocthol': 'moisture:wet',
}
standalone = {
    'chol': 'moisture:dry', 'chy': 'thermal:hot',
    'okey': 'thermal:warm', 'oky': 'thermal:warm',
    'oty': 'thermal:cold', 'qoteedy': 'thermal:cold',
    'shol': 'moisture:wet', 'shy': 'moisture:wet',
    'teody': 'thermal:cold',
}
features = []
for kind, table in [('BARE_NOMINAL', bare), ('PROCESSED_NOMINAL', processed), ('STANDALONE', standalone)]:
    for word, values in table.items():
        for pair in values.split():
            axis, value = pair.split(':')
            features.append(dict(form=word, axis=axis, value=value, kind=kind))

lex = list(csv.DictReader((P / 'LEXICON.tsv').open(), delimiter='\t'))
assert set(x['form'] for x in features) <= set(x['form'] for x in lex)
files = [P / x for x in ['SOURCE.json', 'LEXICON.tsv', 'ARGUMENTS.tsv', 'ALTERNATE_LINES.json', 'MODEL.md', 'REPORT.md']]
files += [E / 'DECISION.md', E / 'register.py']
root = next(p for p in E.parents if (p / 'vmanus-work').exists())
spec = {
    'registered_utc': datetime.now(timezone.utc).isoformat(),
    'mode': 'EXPOSED_AUTHORED_GLOBAL_REVISION',
    'features': features,
    'quality_models': ['Q0_PHYSICAL', 'Q1_NOMINAL_CONSTITUTION'],
    'relation_models': {'T': 'trenne … von …', 'V': 'verbinde … mit …'},
    'opposed': {'thermal': [['cold', 'warm'], ['cold', 'hot']], 'moisture': [['dry', 'wet']]},
    'interpretive_limits': [
        'NO_MEANING_SELECTION', 'NO_NEW_WORD_VALUES_EXCEPT_QOTCHY_VARIANTS',
        'NO_HELD_ACCESS', 'NO_SIGNIFICANCE', 'NO_INDEPENDENT_CONFIRMATION',
        'LINE_AND_ACTION_BARRIERS_ASSUMED_NOT_DECODED_SYNTAX',
        'OTHER_STATES_NOT_TESTED_FOR_THERMAL_MOISTURE_CONTRADICTIONS',
        'WATER_OR_LIQUID_NOT_AUTOMATICALLY_CONSTITUTIONALLY_WET',
        'FRESH_NOT_AUTOMATICALLY_MOIST',
    ],
    'inputs': [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
}
out = E / 'SPEC.json'
assert not out.exists(), 'Do not silently re-register after inspecting results.'
out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n')
print('Registered finite feature list and source hashes; no consequence evaluation.')
