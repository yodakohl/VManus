#!/usr/bin/env python3
"""Exact displayed source extraction; no Voynich input or inferred restoration."""
from pathlib import Path
import collections
import hashlib
import html
import json
import re
import unicodedata

BASE=Path(__file__).resolve().parent
URL='https://geniza.princeton.edu/en/documents/40129/'
HTML=BASE/'semitic_cache/PGP40129.html'

def extract(data):
    blocks=[]
    for name,ol in re.findall(r'<h3>([^<]*)</h3>\s*<ol>(.*?)</ol>',data.decode(),re.S):
        lines=[html.unescape(re.sub('<[^>]+>','',x)) for x in re.findall(r'<li>(.*?)</li>',ol,re.S)]
        if lines and any('\u0590'<=c<='\u05ff' for c in ''.join(lines)):
            blocks.append({'face':name.strip(),'lines':[{'n':i+1,'text':x} for i,x in enumerate(lines)]})
    assert [(b['face'],len(b['lines'])) for b in blocks]==[('recto',21),('verso',21),('verso, right margin',4)]
    return blocks

def graphemes(word):
    units=[]
    for c in unicodedata.normalize('NFD',word):
        if unicodedata.combining(c):
            assert units
            units[-1]+=c
        else:units.append(c)
    return units

def compile_records(blocks):
    r=[x['text'] for x in blocks[0]['lines']];v=[x['text'] for x in blocks[1]['lines']]
    assert r[4].startswith('אלכוך.') and r[12].endswith('אלרמֹאן')
    assert v[4].endswith('אלספרגֹל') and v[14].startswith('אלתֹפאחֹ')
    split_r=r[12].rfind('אלרמֹאן');split_v=v[4].rfind('אלספרגֹל')
    records=[
      {'id':'PEACH','source_scope':'recto5 through recto13 before the pomegranate head','lines':r[4:12]+[r[12][:split_r].rstrip()]},
      {'id':'POMEGRANATE','source_scope':'pomegranate head recto13 through verso5 before the quince head; includes cross-face Hippocrates story','lines':[r[12][split_r:]]+r[13:]+v[:4]+[v[4][:split_v].rstrip()]},
      {'id':'QUINCE','source_scope':'quince head verso5 through verso14; apple head excluded','lines':[v[4][split_v:]]+v[5:14]},
    ]
    for record in records:
        raw=' '.join(record['lines'])
        assert all(c.isspace() or '\u05d0'<=c<='\u05ea' or c in 'ֹ.;' for c in raw)
        # Printed punctuation is not lexical. Every written letter and mark remains.
        words=raw.translate(str.maketrans({'.':'',';':''})).split()
        record.update(words=words,grapheme_words=[graphemes(w) for w in words])
        units=[u for w in record['grapheme_words'] for u in w]
        record.update(word_count=len(words),grapheme_count=len(units),unit_counts=dict(sorted(collections.Counter(units).items())),word_type_count=len(set(words)))
    return records

if __name__=='__main__':
    data=HTML.read_bytes();blocks=extract(data);records=compile_records(blocks)
    out={'source_url':URL,'html_sha256':hashlib.sha256(data).hexdigest(),'editor':'Ani Avetisyan, 2022; displayed Princeton Geniza Project transcription',
         'date_limit':'Institutional catalogue infers post-tenth-century; no secure pre-1420 date established here.',
         'source_layers':'Exact displayed letters and marks, not a new critical edition. Full fragment transcription retained; no English translation compiled.',
         'transcription':blocks,'records':records,
         'excluded_complete_entries':[{'id':'APRICOT','reason':'Begins before preserved face; lines1-4 are a continuation.'},{'id':'APPLE','reason':'Continues after verso21; margin also has uncertain missing text.'}],
         'projection':'NFD base-plus-combining-mark clusters; final Hebrew letter forms remain distinct; period and semicolon omitted; all letters/marks and word order preserved. No phonetic normalization or word-gloss adoption.'}
    (BASE/'PGP40129_SOURCE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    (BASE/'semitic_cache/PGP40129_TRANSCRIPTION.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'id':r['id'],'words':r['word_count'],'types':r['word_type_count'],'graphemes':r['grapheme_count'],'units':len(r['unit_counts'])} for r in records],ensure_ascii=False))
