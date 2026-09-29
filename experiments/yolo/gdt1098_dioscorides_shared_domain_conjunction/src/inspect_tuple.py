"""Display any registered complete tuple and ALL its conditional common domains."""
import argparse
import gzip
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('indices',nargs=4,type=int,help='original case indices in I.1,I.2,I.3,IV.20 order')
    args=parser.parse_args()
    inp=json.loads(gzip.decompress((E/'artifacts/INPUT_DOMAINS.json.gz').read_bytes()))
    chosen=[next(c for c in role if c['index']==i) for role,i in zip(inp['roles'],args.indices)]
    common={a:sorted(set.intersection(*(set(c['domains'][a]) for c in chosen if a in c['domains']))) for a in inp['atoms']}
    distinct=len({c['leaf'] for c in chosen})==4
    print(json.dumps(dict(case_indices=args.indices,pages=[c['page'] for c in chosen],distinct_leaves=distinct,
                         passes_necessary_projection=distinct and all(common.values()),common_domains=common,
                         full_prefix_free_code=False,meaning_confirmation=False),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
