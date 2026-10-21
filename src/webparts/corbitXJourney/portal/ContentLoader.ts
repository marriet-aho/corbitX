import { SPHttpClient } from '@microsoft/sp-http';
import schema from './schema.json';
import { DEFAULT_LISTS } from './defaultLists';
import { RC_DEFAULTS } from './defaultRc';

/* eslint-disable @typescript-eslint/no-explicit-any */
interface IField { n: string; t: string; p?: string; }
interface IListDef { list: string; key: string; kind: string; titleProp: string; target?: string; tuple?: string[]; fields: IField[]; }

export interface ILoaded {
  lists: any;                                   // Kukua's content
  posters: { [id: string]: { title?: string; img?: string } };
  rc: any;                                      // Readiness Centre content
  fromSharePoint: string[];
}

const num = (v: any): number => (v === null || v === undefined || v === '' ? 0 : Number(v));
const text = (v: any): string => (v === null || v === undefined ? '' : (typeof v === 'object' && v.Url ? v.Url : String(v)).trim());
const lines = (v: any): string[] => text(v).split(/\r?\n/).map(x => x.trim()).filter(x => !!x);
const pairs = (v: any): string[][] => lines(v).map(x => { const i = x.indexOf('|'); return i < 0 ? [x, ''] : [x.slice(0, i).trim(), x.slice(i + 1).trim()]; });

function coerce(f: IField, v: any): any {
  switch (f.t) {
    case 'number': return num(v);
    case 'bool': return v === true || v === 1;
    case 'lines': return lines(v);
    case 'pairs': return pairs(v);
    default: return String(v === null || v === undefined ? '' : v);
  }
}
const isoDate = (v: any): string => { const t = text(v); const d = /^\d{4}-\d{2}-\d{2}/.exec(t); return d ? d[0] : t; };

/** Reads every list. A list that is missing, empty or unreachable falls back to the built-in default content. */
export async function loadContent(http: SPHttpClient, webUrl: string): Promise<ILoaded> {
  const lists: any = JSON.parse(JSON.stringify(DEFAULT_LISTS));
  const rc: any = JSON.parse(JSON.stringify(RC_DEFAULTS));
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
    const props = (r: any): any => {
      const o: any = {};
      if (def.titleProp) o[def.titleProp] = text(r.Title);
      def.fields.forEach(f => { o[f.p || f.n] = coerce(f, r[f.n]); });
      return o;
    };
    const out: any = def.target === 'rc' ? rc : lists;

    switch (def.kind) {
      case 'strings': out[def.key] = rows.map(r => text(r.Title)).filter(x => !!x); break;
      case 'posters':
        rows.forEach(r => {
          const id = text(r.PosterId); if (!id) return;
          posters[id] = { title: text(r.Title) || undefined, img: text(r.ImageUrl) || undefined };
          if (text(r.ImageUrl)) { (rc.IMG = rc.IMG || {})[id] = text(r.ImageUrl); }
        });
        break;
      case 'highlights': {
        const groups: any[] = [];
        rows.forEach(r => {
          const name = text(r.Group) || 'Highlights';
          let g = groups.filter(x => x.Group === name)[0];
          if (!g) { g = { Group: name, Icon: text(r.Icon) || 'users', Items: [] }; groups.push(g); }
          const item: any = { Value: num(r.Value), Suffix: text(r.Suffix), Label: text(r.Title) };
          if (r.ShowBar === true) item.Bar = true;
          g.Items.push(item);
        });
        out[def.key] = groups; break;
      }
      case 'settings': {
        const s: any = {}; rows.forEach(r => { s[text(r.Title)] = text(r.Value); }); out.SETTINGS = s; break;
      }
      case 'tuples':
        out[def.key] = rows.map(r => (def.tuple as string[]).map(c => {
          if (c === 'Title') return text(r.Title);
          if (c === 'Date') return isoDate(r.Date);
          const f = def.fields.filter(x => x.n === c)[0]; return f ? coerce(f, r[c]) : text(r[c]);
        }));
        break;
      case 'qrc':
        out[def.key] = rows.map(r => [text(r.Title), lines(r.Items).map(l => (l.charAt(0) === '-' ? ['x', l.slice(1).trim()] : ['tick', l.replace(/^\+/, '').trim()]))]);
        break;
      case 'dates':
        out[def.key] = rows.map(r => ({ Title: text(r.Title), Body: text(r.Body), Days: num(r.OffsetDays), Months: num(r.OffsetMonths), Fmt: text(r.Format) || 'Day', Big: r.Big === true }));
        break;
      default: out[def.key] = rows.map(props);
        if (def.key === 'JourneyStages') out[def.key].forEach((o: any, i: number) => { o.Order = num(rows[i].Order) || 0; });
    }
    fromSharePoint.push(def.list);
  }));
  return { lists, posters, rc, fromSharePoint };
}
