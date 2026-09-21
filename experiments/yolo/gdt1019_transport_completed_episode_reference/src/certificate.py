"""Two independent evaluations of the same pure completed-event anaphor."""
TRIPS={'WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP'}

def inspect_certificate(parsed,independent=False):
    rows=[]
    if not independent:
        count=0;certified=0
        for i,cl in enumerate(parsed):
            if cl['kind'] in TRIPS:count+=1
            elif cl['kind']=='THEN':
                rows.append(dict(clause=f'S{i+1:02d}',start=cl['start'],end=cl['end'],previously_certified=certified,completed=count,interval=list(range(certified+1,count+1)),valid=count>certified));certified=count
    else:
        moves=[i for i,c in enumerate(parsed) if c['kind'] in TRIPS]
        previous_marker=-1
        for i,cl in enumerate(parsed):
            if cl['kind']!='THEN':continue
            before=sum(j<previous_marker for j in moves);through=sum(j<i for j in moves)
            interval=[k+1 for k,j in enumerate(moves) if previous_marker<j<i]
            rows.append(dict(clause=f'S{i+1:02d}',start=cl['start'],end=cl['end'],previously_certified=before,completed=through,interval=interval,valid=bool(interval)));previous_marker=i
    return dict(valid=all(r['valid'] for r in rows),markers=rows)
