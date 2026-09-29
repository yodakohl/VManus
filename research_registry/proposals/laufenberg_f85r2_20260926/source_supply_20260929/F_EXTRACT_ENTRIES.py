"""Extract three complete named entries from the public CAMENA transcription.
All source files are historical comparators. No Voynich data is accessed.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
source = BASE / 'F_SOURCE_LONITZER_TYPED_TOM1.html'
raw = source.read_text(encoding='utf-8')

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
    def handle_starttag(self, name, attrs):
        if name in ('p', 'h2', 'br', 'div'):
            self.items.append('\n')
    def handle_endtag(self, name):
        if name in ('p', 'h2', 'div'):
            self.items.append('\n')
    def handle_data(self, value):
        self.items.append(value)

def flatten(html, illustration_owners):
    parser = Text()
    parser.feed(html)
    text = ''.join(parser.items)
    text = re.sub(r'\[Orig:.*?\]', '', text, flags=re.S)
    owners = iter(illustration_owners)
    text = re.sub(r'\[Illustration:.*?\]',
                  lambda match: '[woodcut: '+next(owners)+'; see full page image]',
                  text, flags=re.S)
    lines = [re.sub(r'\s+', ' ', x).strip() for x in text.splitlines()]
    return '\n'.join(x for x in lines if x)

spans = [('DIPSACUS', 'CHAMAELEON', ['066B','067A'], 'ff66v–67r'),
         ('ATRACTYLIS', 'ACANTHIUM', ['068A','068B'], 'ff68r–68v'),
         ('CARDUUS', 'ANONIS', ['071A','071B','072A'], 'ff71r–72r')]
entries = []
illustration_owners = {
    'DIPSACUS': ['Dipsacus, 66v'],
    'ATRACTYLIS': ['Atractylis, upper image on 68v',
                  'ACANTHIUM, lower image on 68v; following entry, placed before its heading in the HTML'],
    'CARDUUS': ['Carduus, 71r', 'wild Carduus, lower image on 71v; not a certified picture of the spineless counterpart']}
for title, following, images, locus in spans:
    start = raw.index('<h2>' + title + '.</h2>')
    end = raw.index('<h2>' + following + '.</h2>', start)
    html = raw[start:end]
    entries.append({'id': title, 'locus': locus, 'first_source_line': raw.count('\n', 0, start)+1,
                    'following_entry_boundary': following, 'complete_local_entry': True,
                    'source_html': html, 'typed_plain_text': flatten(html, illustration_owners[title]),
                    'html_window_scope': 'Heading-to-heading source bytes; includes any illustration marker placed before the next heading. Such placement does not determine visual ownership.',
                    'illustration_owners_in_html_order': illustration_owners[title],
                    'native_full_page_images': ['F_LONITZER_' + n + '.jpg' for n in images]})
packet = {'status': 'THREE_COMPLETE_SOURCE_ENTRIES_NOT_TARGET_READINGS',
          'author': 'Adam Lonitzer', 'work': 'Naturalis historiae opus novum, Tomus I',
          'print_date': '1551',
          'date_basis': 'Institutional CAMENA catalogue dates Tomus I from its colophon; its supplied 1565 title leaf is a later replacement, not the date of the body used here.',
          'catalogue_url': 'https://mateo.uni-mannheim.de/camenaref/lonitzer.html',
          'transcription_url': 'https://mateo.uni-mannheim.de/camenaref/lonitzer/loni1/books/lonitzer1_1.html',
          'source_file': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'transcription_layer': 'CAMENA human-typed text, with acknowledged uncorrected errors. Full entry bytes preserved; selected claim-bearing wording checked against full native print pages. Not a new fully diplomatic edition.',
          'modern_species_assignments': [],
          'entries': entries}
(BASE/'F_COMPLETE_ENTRIES.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
md=['# Three complete Lonitzer entries (1551)','',
    'The text below is the preserved CAMENA typed edition, not a fully corrected diplomatic transcription. Original-accent annotations are omitted only from this readable display; source HTML is retained in JSON. Marginal-note markers and page transitions remain distinguishable. Illustration markers are editorially labelled by visual ownership, which does not follow HTML heading position automatically: the final marker within the Atractylis HTML window depicts the following Acanthium entry. Read F_NATIVE_COLLATION.json for material checked corrections and image observations.','']
for entry in entries:
    md += ['## '+entry['id']+' — '+entry['locus'], '', entry['typed_plain_text'], '']
(BASE/'F_COMPLETE_ENTRIES.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'status':'PASS','entries':len(entries),'complete_entries':[e['id'] for e in entries],
                  'native_full_pages':7,'source_sha256':packet['source_sha256']},indent=2))
