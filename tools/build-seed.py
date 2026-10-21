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
    if d.get('target') == 'rc': continue
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

# ---------- Readiness Centre lists
RC = json.load(open(os.path.join(ROOT, 'seed/rc-defaults.json')))
def addrc(name, rows): seed[name] = [dict(r, Order=i + 1, IsActive=True) for i, r in enumerate(rows)]
addrc('Page Settings', [{'Title': k, 'Value': v} for k, v in RC['SETTINGS'].items()])
addrc('Guide Categories', [{'Title': c['name'], 'CatId': c['id'], 'Description': c['desc']} for c in RC['CATS']])
addrc('Staff Guides', [{'Title': p['title'], 'PosterId': p['id'], 'CatId': p['cat'], 'Short': p['short'], 'Intro': p['intro'], 'Steps': '\n'.join(a + ' | ' + b for a, b in p['steps']), 'Key': p.get('key', ''), 'Say': p.get('say', ''), 'Note': p.get('note', '')} for p in RC['POSTERS']])
addrc('Programme Phases', [{'Title': p['n'], 'Icon': p['ic'], 'When': p['when'], 'Description': p['d'], 'Focus': '\n'.join(p['f']), 'Materials': '\n'.join(a + ' | ' + b for a, b in p['m'])} for p in RC['PHASES']])
addrc('Capabilities', [{'Title': c[1], 'Icon': c[0], 'Text': c[2], 'Wide': bool(c[3])} for c in RC['CAPS']])
addrc('Hub FAQs', [{'Title': f[0], 'Answer': f[1], 'PosterId': f[2]} for f in RC['FAQS']])
addrc('Training Videos', [{'Title': v[0], 'Description': v[1]} for v in RC['VIDEOS']])
addrc('Quick Reference Cards', [{'Title': q[0], 'Items': '\n'.join(('- ' if t == 'x' else '+ ') + l for t, l in q[1])} for q in RC['QRC']])
addrc('Project Updates', [{'Title': u[1], 'Date': u[0], 'Body': u[2]} for u in RC['UPDATES']])
addrc('Key Dates', [{'Title': d['Title'], 'Body': d['Body'], 'OffsetDays': d['Days'], 'OffsetMonths': d['Months'], 'Format': d['Fmt'], 'Big': d['Big']} for d in RC['DATES']])
addrc('Support Contacts', [{'Title': c[1], 'Icon': c[0], 'Purpose': c[2], 'Contact': c[3]} for c in RC['CONTACTS']])
addrc('Key Messages', [{'Title': m} for m in RC['mq']])

json.dump(seed, open(os.path.join(ROOT, 'seed/seed.json'), 'w'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in seed.items()})
