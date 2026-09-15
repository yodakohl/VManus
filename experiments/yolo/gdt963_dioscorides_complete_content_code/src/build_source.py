"""Freeze four complete printed-text lexical/concept streams, without target access."""
import collections
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

E = Path(__file__).resolve().parents[1]
NS = {'t': 'http://www.tei-c.org/ns/1.0'}

def norm(s):
    return unicodedata.normalize('NFC', s.lower())

def maintext(e):
    if e.tag.rsplit('}', 1)[-1] in ('note', 'head'):
        return ''
    return (e.text or '') + ''.join(maintext(c) + (c.tail or '') for c in e)

def build():
    aliases = json.loads((E/'src/ALIASES.json').read_text())
    mapping = {}
    for atom, variants in aliases['single_atom_forms'].items():
        for word in variants:
            w = norm(word)
            assert w not in mapping or mapping[w] == [atom], (w, atom)
            mapping[w] = [atom]
    for word, atoms in aliases['expanded_forms'].items():
        assert norm(word) not in mapping
        mapping[norm(word)] = atoms
    source = ET.parse(E/'src/SOURCE_EXCERPTS.xml').getroot()
    records = []
    for entry in source:
        rid = entry.attrib['id']
        raw = ' '.join(maintext(entry).split())
        # One independently observed editorial letter insertion splits a word.
        replacements = []
        for old, new in aliases['source_orthographic_joins'].get(rid, {}).items():
            assert raw.count(old) == 1, (rid, old)
            raw = raw.replace(old, new)
            replacements.append([old, new])
        words = re.findall(r'[^\W\d_]+', raw, flags=re.UNICODE)
        events = []
        for i, word in enumerate(words):
            w = norm(word)
            atoms = mapping.get(w, ['LEX:'+w])
            # This Iris is the celestial comparison, not the plant referent.
            if rid == 'I.1' and word == 'Ἴριδι':
                atoms = ['CELESTIAL_IRIS']
            events.append({'index': i, 'printed_form': word, 'atoms': atoms})
        stream = [a for event in events for a in event['atoms']]
        records.append(dict(id=rid, raw_printed_projection=raw,
                            orthographic_joins=replacements, tokens=events,
                            atoms=stream, counts=dict(collections.Counter(stream)),
                            editorial_deletion_text=[maintext(x) for x in entry.findall('.//t:del', NS)],
                            editorial_addition_text=[maintext(x) for x in entry.findall('.//t:add', NS)]))
    allcounts = collections.Counter(a for r in records for a in r['atoms'])
    result = dict(schema='GDT963_COMPLETE_PRINTED_CONTENT_STREAM_V1', records=records,
                  atom_count=len(allcounts), counts=dict(allcounts),
                  global_singletons=sorted(a for a,c in allcounts.items() if c == 1),
                  semantics='Selected explicitly listed lexical/concept identifications; all other individual printed lexical forms stay opaque, not free clause IDs.',
                  printed_projection='Footnotes and heads excluded; printed add/del content retained and flagged; punctuation and numeric section markers omitted. This is the specified diplomatic printed projection, not a new critical edition.',
                  source_order='Original printed lexical order; expanded semantic atoms in the listed order. Not a language-independent universal serializer.',
                  confirmed_words=0)
    (E/'src/SOURCE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    rows = ['record\ttokens\tatoms\tdistinct_atoms\tglobal_singleton_occurrences\tshared_with_other_records']
    for r in records:
        others=set(a for x in records if x['id']!=r['id'] for a in x['atoms'])
        rows.append('\t'.join(map(str,[r['id'],len(r['tokens']),len(r['atoms']),len(r['counts']),sum(allcounts[a]==1 for a in r['atoms']),sum(a in others for a in r['atoms'])])))
    (E/'artifacts/SOURCE_CAPACITY.tsv').write_text('\n'.join(rows)+'\n')
    print('\n'.join(rows))
    return result

if __name__ == '__main__':
    build()
