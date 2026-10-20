#!/usr/bin/env python3
"""Turns seed/defaults.json (the approved content) into seed/seed.json: one row per SharePoint list item, using schema.json."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema = json.load(open(os.path.join(ROOT, 'src/webparts/corbitXJourney/portal/schema.json')))
D = json.load(open(os.path.join(ROOT, 'seed/defaults.json')))
seed = {}
def val(t, v):
    if t == 'lines': return '\n'.join(v)
    if t == 'pairs': return '\n'.join(a + ' | ' + b for a, b in v)
    return v
for d in schema['lists']:
    rows = []
    if d['kind'] == 'strings':
        rows = [{'Title': t, 'Order': i + 1, 'IsActive': True} for i, t in enumerate(D[d['key']])]
    elif d['kind'] == 'highlights':
        n = 0
        for g in D['Highlights']:
            for it in g['Items']:
                n += 1; rows.append({'Title': it['Label'], 'Group': g['Group'], 'Icon': g['Icon'], 'Value': it['Value'], 'Suffix': it.get('Suffix', ''), 'ShowBar': bool(it.get('Bar')), 'Order': n, 'IsActive': True})
    elif d['kind'] == 'posters':
        P = json.load(open(os.path.join(ROOT, 'seed/posters.json')))
        seed['Posters'] = [{'Title': v['title'], 'PosterId': k, 'ImageFile': v['file'], 'Order': i + 1, 'IsActive': True} for i, (k, v) in enumerate(sorted(P.items()))]
        continue
    else:
        for i, it in enumerate(D[d['key']]):
            r = {'Title': it.get(d['titleProp'], '')}
            for f in d['fields']: r[f['n']] = val(f['t'], it.get(f['n'], '' if f['t'] not in ('bool',) else False))
            r['Order'] = it.get('Order', i + 1); r['IsActive'] = True; rows.append(r)
    seed[d['list']] = rows
json.dump(seed, open(os.path.join(ROOT, 'seed/seed.json'), 'w'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in seed.items()})
