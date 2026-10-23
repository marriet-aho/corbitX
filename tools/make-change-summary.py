#!/usr/bin/env python3
"""Compares the content before and after the briefing update and writes:
   docs/Corbit_X_Content_Update_Summary.docx  (every change, before -> after)
   docs/Corbit_X_List_Updates.xlsx            (the SharePoint list rows to change)"""
import json, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema = json.load(open(os.path.join(ROOT, 'src/webparts/corbitXJourney/portal/schema.json')))['lists']
A = json.load(open(os.path.join(ROOT, 'seed/seed.json'), encoding='utf8'))
B = json.load(open(os.path.join(ROOT, 'seed/before/seed.json'), encoding='utf8'))

def cols(d):
    c = ['Title']
    for f in d['fields']:
        if d['kind'] == 'posters' and f['n'] == 'ImageFile': continue
        c.append(f['n'])
    return c + ['Order', 'IsActive']
def norm(v):
    if isinstance(v, bool): return 'Yes' if v else 'No'
    return '' if v is None else str(v)

changes = []   # (list, status, order, title, [(field, before, after)])
for d in schema:
    name = d['list']; a_rows = A.get(name, []); b_rows = B.get(name, [])
    fields = cols(d)
    for i, a in enumerate(a_rows):
        b = b_rows[i] if i < len(b_rows) else None
        if b is None:
            changes.append((name, 'NEW', a.get('Order', i + 1), a.get('Title', ''), [(f, '', norm(a.get(f, ''))) for f in fields if f not in ('Order', 'IsActive') and norm(a.get(f, ''))]))
            continue
        diffs = [(f, norm(b.get(f, '')), norm(a.get(f, ''))) for f in fields if f not in ('Order',) and norm(b.get(f, '')) != norm(a.get(f, ''))]
        if diffs: changes.append((name, 'UPDATED', a.get('Order', i + 1), b.get('Title', ''), diffs))
    for j in range(len(a_rows), len(b_rows)):
        changes.append((name, 'REMOVED', b_rows[j].get('Order', j + 1), b_rows[j].get('Title', ''), []))
print(len(changes), 'row changes across', len(set(c[0] for c in changes)), 'lists')

# ------------------------------------------------------------------ Excel: rows to change in SharePoint
wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'READ ME'
for i, t in enumerate([
    'Corbit X: SharePoint list updates after the go-live briefing (1 February 2027)',
    'Your lists keep working as they are: no list or column names changed and no columns were added.',
    'A list that has items overrides the page\'s built-in wording, so the corrected wording appears on your page only once these rows are updated.',
    'Each sheet is named like the list. Only rows that changed are shown. Column ACTION (last) says what to do:',
    '   UPDATE: open the item with the same Order number (or the same Title) and paste the new values.',
    '   ADD: create a new item with these values (Order is the position it should take).',
    '   REMOVE: set IsActive to No on the item with this Order (or delete it).',
    'Do not forget Page Settings: GoLive must become 2027-02-01T00:00:00+00:00.',
    'The sheet CHANGES lists every change in words.']): ws.cell(i + 1, 1, t)
ws['A1'].font = Font(bold=True, size=14); ws.column_dimensions['A'].width = 150
ch = wb.create_sheet('CHANGES'); ch.append(['List', 'Order', 'Action', 'Item (title before)', 'What changed (column: before => after)'])
fill = {'UPDATED': 'FFF2CC', 'NEW': 'E2EFDA', 'REMOVED': 'E7E6E6'}
hdr = PatternFill('solid', fgColor='F26A1B')
for c in ch[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
for name, st, order, title, diffs in changes:
    txt = '\n'.join('%s: %s => %s' % (f, (b[:140] + '…') if len(b) > 140 else b, (a[:140] + '…') if len(a) > 140 else a) for f, b, a in diffs) if diffs else ('(removed in the new content)' if st == 'REMOVED' else '')
    ch.append([name, order, {'UPDATED': 'UPDATE', 'NEW': 'ADD', 'REMOVED': 'REMOVE'}[st], title, txt])
    for c in ch[ch.max_row]: c.fill = PatternFill('solid', fgColor=fill[st]); c.alignment = Alignment(wrap_text=True, vertical='top')
for col, w in zip('ABCDE', (24, 8, 10, 44, 120)): ch.column_dimensions[col].width = w
for d in schema:
    rows = [c for c in changes if c[0] == d['list']]
    if not rows: continue
    sh = wb.create_sheet(d['list'][:31]); header = cols(d) + ['ACTION']
    sh.append(header)
    for c in sh[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
    for name, st, order, title, diffs in rows:
        src = (A if st != 'REMOVED' else B)[name]
        r = next((x for x in src if x.get('Order') == order), None) or {}
        sh.append([r.get(f, '') if not isinstance(r.get(f, ''), bool) else ('Yes' if r.get(f) else 'No') for f in cols(d)] + [{'UPDATED': 'UPDATE', 'NEW': 'ADD', 'REMOVED': 'REMOVE'}[st]])
        for c in sh[sh.max_row]: c.fill = PatternFill('solid', fgColor=fill[st]); c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, h in enumerate(header, 1):
        mx = max([len(str(sh.cell(rr, i).value or '')) for rr in range(1, sh.max_row + 1)] + [8])
        sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = min(60, mx + 2)
wb.save(os.path.join(ROOT, 'docs/Corbit_X_List_Updates.xlsx'))
json.dump([list(c) for c in changes], open('/tmp/_changes.json', 'w'), ensure_ascii=False)

# ------------------------------------------------------------------ Word summary
doc = Document()
sec = doc.sections[0]; sec.left_margin = sec.right_margin = Cm(2); sec.top_margin = sec.bottom_margin = Cm(2)
doc.styles['Normal'].font.name = 'Calibri'; doc.styles['Normal'].font.size = Pt(10.5)
for n, sz in (('Heading 1', 17), ('Heading 2', 13), ('Heading 3', 11.5)):
    s = doc.styles[n]; s.font.name = 'Calibri'; s.font.size = Pt(sz); s.font.color.rgb = RGBColor(0xD4, 0x54, 0x0A)
def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color); tcPr.append(sh)
def table(rows, header, widths):
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(c, 'F26A1B')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''; cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph()
def bullets(items):
    for it in items: doc.add_paragraph(it, style='List Bullet')

doc.add_heading('Corbit X page: content update summary', 0)
doc.add_paragraph('Source of truth: "Corbit X Go-Live Staff Briefing, 1 Feb 2027" (22 slides). Scope: content only. Design, branding, layout and behaviour are unchanged, except where noted in section 5.')
doc.add_heading('1. The main corrections', 1)
bullets([
 'Go-live date: the page counted down to Monday 8 February 2027. The briefing says Corbit X goes live on Monday 1 February 2027 (moved to accommodate other important Bank transactions). The countdown, key dates and all wording now use 1 February 2027.',
 'Dashboard figures: the page showed 2,500+ staff, 94% project completion, 30+ champions, 2 roadshows, 3 simulations and 68% confidence. None of these match the briefing. The dashboard now shows the briefing\'s results: overall simulation score 93.4% (95% go-live gate, up from 51%), 85% confident (45% at BSIM 1), 99.8% logged in at BSIM 4, 96% of tickets fixed the same day, 94% of branches ready and 4 business simulations completed.',
 'Timeline: the old six generic phases (Awareness to Stabilization) are replaced by the briefing\'s calendar: Step 1 Keep your skills sharp (26 Oct to 23 Dec), Step 2 Rest and recharge (24 Dec to 3 Jan), Step 3 Get go-live ready (4 to 22 Jan), Step 4 Final systems check (11 to 17 Jan), Step 5 Lift-off weekend (29 Jan to 1 Feb), then After go-live.',
 '"What\'s next": now the same five steps with their dates (it previously listed 30+ champions and simulations that are already complete).',
 'Key dates: now a full calendar from the briefing: data migration 11 Jan, data validation 13 to 15 Jan, financial validation 16 Jan, business simulation 17 Jan, final cut-off Fri 29 Jan at 2:00pm, live checks Sun 31 Jan, go-live Mon 1 Feb, accounts finalised Thu 4 Feb, and old-number cheques end 2 Aug 2027. The vague "static data freeze begins" row was removed because the briefing gives no freeze date.',
 'Cheques: "six months after go-live" is now stated as six months (182 days), until 2 August 2027, everywhere it appears.',
 'Account opening: "from Thursday after go-live" is now "from Thursday 4 February", and "the first three days" is now Monday 1 to Wednesday 3 February.',
 'Sunday checks: "the Sunday before go-live" is now Sunday 31 January 2027, and the Friday 29 January 2:00pm cut-off was added.',
 'Account numbers: the new 13-digit format is now explained (digits 1 to 2 currency, digit 3 customer type, digits 4 to 11 serial, digits 12 to 13 check digits; "00" added before an existing CIF). The inconsistent wording "usable during the transition" was replaced by "still work for more than six months".',
 'Statements: removed the unsupported claim "cleaner, faster request process". Statements for the last 12 months come straight from Corbit X; older statements, back to account opening, come from stored backup.',
 'Support route: replaced generic contacts with the briefing\'s route: check the guide or FAQ, ask your champion or team lead, log a Command Centre ticket with a screenshot, and update the customer. Added the fraud reminder (the bank never asks for a PIN, password or OTP; never share your login).',
 'Added from the briefing: quick guide card for BOS authorisers (KYC first, then CIF, then cheque book request), the go-live "arrive by 7:00am" guidance, and new FAQs (when does Corbit X go live, how to read the new account number, what to do if you are stuck, and what to do about OTP and fraud).',
 'Headings and labels made consistent: the timeline now uses "Step 1 to 5" and "After go-live" everywhere (heading, labels, panel and narration), and the old "Phase" wording and "Six phases" sentence were removed.'])

doc.add_heading('2. Consistency checks made across the whole page', 1)
bullets(['One go-live date everywhere: hero countdown, announcement, timeline, key dates, journey stops, FAQs, Kukua\'s welcome and "What\'s next".',
         'One cheque rule everywhere: six months (182 days), until 2 August 2027, with the usual checks; books over five years old do not migrate.',
         'One account-opening rule everywhere: start in Newgen during the freeze and the first three days; finalise from Thursday 4 February; never turn a customer away.',
         'Duplicate "Sunday checks" and "account opening" explanations now say the same thing in the poster pop-ups, journey panels, FAQs, quick cards, timeline and key dates.',
         'Clarity: vague timing such as "the Sunday before go-live", "Thursday after go-live", "during the transition" and "six months after go-live" was replaced with the actual dates; dates are written in one format (Monday 1 February 2027 in full text, Mon 1 Feb in labels); and the "Phase" and "Step" wording was unified.'])

doc.add_heading('3. Image', 1)
bullets(['Kukua is unchanged everywhere she appears.',
         'The new character (a colleague in a white and orange flight suit, thumbs up, holding a helmet) was added, cut out from its grey backdrop, in three sections only: the dark "Preparing today for tomorrow\'s banking experience" banner, "What\'s next", and the closing "Together we are ready for Corbit X" section. He is hidden on small screens, so phones and narrow windows look exactly as before.'])

doc.add_heading('4. Every change, row by row', 1)
doc.add_paragraph('"Order" is the row position in the SharePoint list. Long text is shortened here; the full new text is in Corbit_X_List_Updates.xlsx.')
from itertools import groupby
for name, grp in groupby(changes, key=lambda c: c[0]):
    rows = list(grp)
    doc.add_heading('%s (%d rows)' % (name, len(rows)), 3)
    out = []
    for _, st, order, title, diffs in rows:
        if st == 'REMOVED': what = 'Removed from the new content.'
        else:
            parts = []
            for f, b, a in diffs:
                if f in ('IsActive',): continue
                bb = (b[:150] + '…') if len(b) > 150 else b; aa = (a[:150] + '…') if len(a) > 150 else a
                parts.append('%s: %s' % (f, aa if st == 'NEW' else '"%s" now "%s"' % (bb, aa)))
            what = '\n'.join(parts)
        out.append((order, {'UPDATED': 'Update', 'NEW': 'Add', 'REMOVED': 'Remove'}[st], title[:60], what))
    table(out, ['Order', 'Action', 'Item', 'What changed'], [1.2, 1.6, 4.0, 10.2])

doc.add_heading('5. Small design touches (only where they help understanding)', 1)
bullets(['Dashboard numbers can now show one decimal (93.4%, 99.8%); before, they were rounded to whole numbers.',
         'The timeline labels read "Step 1" to "Step 5" and "After go-live" instead of "Phase 1" to "Phase 6".',
         'The "At a glance" box beside the staff guides now shows the four key dates (29 Jan, 31 Jan, 1 Feb, 4 Feb).'])

doc.add_heading('6. Please confirm (open points in the briefing)', 1)
table([
 ('Go-live date', 'The page previously showed 8 February 2027 (as you asked earlier). It now shows 1 February 2027 from the briefing. Tell me if 8 February is still correct.'),
 ('Old-number cheque end date', 'Briefing says 2 August 2027 should be confirmed and announced.'),
 ('Hypercare', 'Length, daily check-in times and Command Centre hours are still to be confirmed.'),
 ('Contacts', 'Command Centre, champion names and Fraud and Risk contact are placeholders in the briefing, so the page still shows "[Add contact]".'),
 ('Statement wording', 'The briefing says "Over 12 months, back to account opening: from stored backup". The page reads this as statements going back to when the account was opened. Confirm the turnaround time for older statements.'),
 ('Static data freeze', 'The briefing gives no freeze start date, so the page says "the week before go-live" (as on the posters) and no longer lists a freeze date.'),
 ('"Kukwa bot"', 'The briefing spells the bot "Kukwa". The page keeps "Kukua", the character\'s name.'),
 ('Poster images', 'The six posters are pictures and were not edited. They say "the Sunday before go-live" and "Thursday after go-live" without dates, which agrees with the dated text around them.'),
 ('Training videos', 'Still marked "coming soon"; no links in the briefing.'),
 ('Removed figures', '2,500+ staff, 30+ champions, 2 roadshows and 3 simulations were removed because the briefing does not support them (it shows 4 simulations and 2 roadshows in its history slide). Tell me if you want any of them back.')],
 ['Topic', 'Note'], [4.0, 13.0])

doc.add_heading('7. Voice', 1)
doc.add_paragraph('Kukua reads from recordings that match the on-screen wording. Every line whose wording changed was re-recorded in the same voice. The new recordings are in the folder voice_new; upload them to SiteAssets/CorbitX/voice/emily (older files can stay). Lines you edit yourself in the lists have no recording until one is made.')
doc.save(os.path.join(ROOT, 'docs/Corbit_X_Content_Update_Summary.docx'))
print('summary written')
