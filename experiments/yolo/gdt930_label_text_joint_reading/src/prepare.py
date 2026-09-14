"""Freeze only the admitted development projection and an already admitted image."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import urllib.request

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
RANGES = {'f17r': (4, 6), 'f21r': (8, 12), 'f32v': (7, 11), 'f29v': (1, 4)}
SOURCE = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
COLUMNS = ['source_group_id','edition','locus','page','kind','source_group_index','source_group_count',
           'paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
URL = 'https://collections.library.yale.edu/iiif/2/1006212/full/2000,/0/default.jpg'
IMAGE_HASH = '6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df'


def selected(row):
    if row['page'] == 'f77r':
        return True
    low, high = RANGES[row['page']]
    return low <= int(row['locus'].split('.')[1]) <= high


def main():
    command = ['./vmanus-exp','query-tsv',SOURCE,'--selector','page']
    for page in ['f77r', *RANGES]:
        command += ['--allow',page]
    command += ['--columns',','.join(COLUMNS),'--forbid-prefix','f84','--forbid-prefix','f84r']
    queried = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True)
    stats = [json.loads(line[12:]) for line in queried.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    assert len(stats) == 1
    rows = [row for row in csv.DictReader(io.StringIO(queried.stdout),delimiter='\t') if selected(row)]
    image_path = EXP/'artifacts/f77r.jpg'
    if not image_path.exists():
        with urllib.request.urlopen(URL,timeout=30) as response:
            image_bytes = response.read()
        assert hashlib.sha256(image_bytes).hexdigest() == IMAGE_HASH, 'Image differs; do not view'
        image_path.write_bytes(image_bytes)
    assert hashlib.sha256(image_path.read_bytes()).hexdigest() == IMAGE_HASH
    result = {'scope':'Exposed development material only; all f77r, four fixed HERB4 ranges',
              'ranges':RANGES,'groups':rows}
    text = json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    target = EXP/'artifacts/SOURCE.json'
    if target.exists():
        assert target.read_text() == text, 'Frozen projection changed'
    else:
        target.write_text(text)
    provenance = {'command':command,'guard':stats[0], 'projection_sha256':hashlib.sha256(text.encode()).hexdigest(),
                  'image_url':URL,'image_sha256':IMAGE_HASH,'new_image_admissions':0,
                  'sealed_data':{'f84':'FORBIDDEN','f84r':'FORBIDDEN'},'prior_exposure':True}
    (EXP/'src/SOURCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({'selected_groups':len(rows),'editions':sorted({r['edition'] for r in rows}),
                      'pages':sorted({r['page'] for r in rows}),'image_sha256':IMAGE_HASH}))


if __name__ == '__main__':
    main()
