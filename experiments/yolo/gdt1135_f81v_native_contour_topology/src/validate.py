#!/usr/bin/env python3
"""Registration check; independent post-observation review is still pending."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
def main():
    lock=json.loads((P/'artifacts/PREREG_LOCK.json').read_text())
    for path,digest in lock['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    print(json.dumps({'status':'REGISTRATION_BYTES_MATCH_POST_OBSERVATION_REVIEW_PENDING','visual_truth_certified':False}))
if __name__=='__main__':main()
