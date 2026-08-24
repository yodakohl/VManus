#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    articles=read('FIVE_HUNDRED_EIGHTY_EIGHTH_FIVE_COMPLETE_HERBAL_ARTICLES.tsv');statements=read('FIVE_HUNDRED_EIGHTY_EIGHTH_NINETEEN_HERBAL_STATEMENTS.tsv');events=read('FIVE_HUNDRED_EIGHTY_EIGHTH_ONE_HUNDRED_HERBAL_EVENT_BINDING.tsv')
    checks={
        'articles5':len(articles)==5 and {r['record'] for r in articles}=={'H1','H2','H3','H4','H5'},
        'statements19':len(statements)==19 and len({r['statement_id'] for r in statements})==19,
        'events100':len(events)==100 and len({r['event_id'] for r in events})==100,
        'event_sum100':sum(int(r['events']) for r in articles)==100 and sum(int(r['event_total']) for r in statements)==100,
        'all_bound':all(r['all_source_actions_and_arguments_bound']=='YES' for r in statements) and all(r['bound_once']=='YES' for r in events),
        'open5':all(r['article_ends_open']=='YES' for r in articles),
        'complete':all(r['complete']=='YES' and r['continuous_article_de'] for r in articles),
        'pages':{r['page'] for r in events}<={'f10r','f11r','f55v','f56r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_EIGHTY_EIGHTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
