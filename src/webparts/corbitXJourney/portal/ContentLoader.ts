import { SPHttpClient } from '@microsoft/sp-http';
import schema from './schema.json';
import { DEFAULT_LISTS } from './defaultLists';

/* eslint-disable @typescript-eslint/no-explicit-any */
interface IField { n: string; t: string; }
interface IListDef { list: string; key: string; kind: string; titleProp: string; fields: IField[]; }

export interface ILoaded { lists: any; posters: { [id: string]: { title?: string; img?: string } }; fromSharePoint: string[]; }

const num = (v: any): number => (v === null || v === undefined || v === '' ? 0 : Number(v));
const text = (v: any): string => (v === null || v === undefined ? '' : (typeof v === 'object' && v.Url ? v.Url : String(v)).trim());

function coerce(f: IField, v: any): any {
  switch (f.t) {
    case 'number': return num(v);
    case 'bool': return v === true || v === 1;
    case 'lines': return text(v).split(/\r?\n/).map(x => x.trim()).filter(x => !!x);
    case 'pairs': return text(v).split(/\r?\n/).map(x => x.trim()).filter(x => !!x).map(x => {
      const i = x.indexOf('|');
      return i < 0 ? [x, ''] : [x.slice(0, i).trim(), x.slice(i + 1).trim()];
    });
    default: return String(v === null || v === undefined ? '' : v);
  }
}

/** Reads every list. A list that is missing, empty or unreachable falls back to the built-in default content. */
export async function loadContent(http: SPHttpClient, webUrl: string): Promise<ILoaded> {
  const lists: any = JSON.parse(JSON.stringify(DEFAULT_LISTS));
  const posters: ILoaded['posters'] = {};
  const fromSharePoint: string[] = [];

  await Promise.all((schema.lists as IListDef[]).map(async def => {
    let rows: any[];
    try {
      const url = `${webUrl}/_api/web/lists/getbytitle('${encodeURIComponent(def.list).replace(/'/g, "''")}')/items?$top=500`;
      const res = await http.get(url, SPHttpClient.configurations.v1);
      if (!res.ok) return;
      rows = ((await res.json()).value as any[]).filter(r => r.IsActive !== false);
    } catch (e) { return; }
    if (!rows.length) return;
    rows.sort((a, b) => (num(a.Order) || 1e6) - (num(b.Order) || 1e6) || a.Id - b.Id);

    if (def.kind === 'strings') { lists[def.key] = rows.map(r => text(r.Title)).filter(x => !!x); }
    else if (def.kind === 'posters') {
      rows.forEach(r => { const id = text(r.PosterId); if (id) posters[id] = { title: text(r.Title) || undefined, img: text(r.ImageUrl) || undefined }; });
    } else if (def.kind === 'highlights') {
      const groups: any[] = [];
      rows.forEach(r => {
        const name = text(r.Group) || 'Highlights';
        let g = groups.filter(x => x.Group === name)[0];
        if (!g) { g = { Group: name, Icon: text(r.Icon) || 'users', Items: [] }; groups.push(g); }
        const item: any = { Value: num(r.Value), Suffix: text(r.Suffix), Label: text(r.Title) };
        if (r.ShowBar === true) item.Bar = true;
        g.Items.push(item);
      });
      lists[def.key] = groups;
    } else {
      lists[def.key] = rows.map(r => {
        const o: any = {};
        if (def.titleProp) o[def.titleProp] = text(r.Title);
        def.fields.forEach(f => { o[f.n] = coerce(f, r[f.n]); });
        if (def.key === 'JourneyStages') o.Order = num(r.Order) || 0;
        return o;
      });
    }
    fromSharePoint.push(def.list);
  }));
  return { lists, posters, fromSharePoint };
}
