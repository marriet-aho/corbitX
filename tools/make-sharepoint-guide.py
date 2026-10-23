#!/usr/bin/env python3
"""Writes docs/Corbit_X_SharePoint_Setup_Guide.docx and docs/Corbit_X_List_Content.xlsx from schema.json + seed.json."""
import json, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema = json.load(open(os.path.join(ROOT, 'src/webparts/corbitXJourney/portal/schema.json')))['lists']
seed = json.load(open(os.path.join(ROOT, 'seed/seed.json')))
OUT = os.path.join(ROOT, 'docs'); os.makedirs(OUT, exist_ok=True)

PURPOSE = {
 'Kukua Messages': "Kukua's welcome, closing, chat greeting and similar spoken lines.",
 'Section Intros': "Kukua's one-line introduction shown under each section.",
 'Journey Stages': 'The six journey stops (poster, what Kukua says, the Learn More panel).',
 'Highlights': 'The figures that build the dashboard: items with ShowBar = Yes become progress bars, the others become figure tiles.',
 'Customer Changes': '"Big changes are coming" cards for customers.',
 'Staff Changes': '"What\'s in it for staff" cards (Today versus With Corbit X).',
 'Training Media': 'Training videos and pictures shown in the Training section.',
 "What's Next": 'The "What\'s next" steps.',
 'Daily Tips': "Kukua's daily tip card (shown in random order).",
 'FAQs': "Questions and answers for Ask Kukua (the chat).",
 'Featured Guides': 'The guide of the week (rotates weekly in Order).',
 'Announcements': '"Latest updates" panel.',
 'Posters': 'Poster titles. Leave ImageUrl empty to use the posters built into the web part; fill it only to replace a poster image.',
 'Page Settings': 'Go-live date, current phase and the announcement card. One setting per row: Title = setting name, Value = its value.',
 'Guide Categories': 'The groups in the Staff Guides gallery.',
 'Staff Guides': 'The staff-guide posters: pop-up text, steps and key message.',
 'Programme Phases': 'The phases in "The road to go-live" timeline.',
 'Capabilities': 'The "What\'s coming to Corbit X" tiles.',
 'Hub FAQs': 'Knowledge Hub: frequently asked questions.',
 'Training Videos': 'Knowledge Hub: training videos.',
 'Quick Reference Cards': 'Knowledge Hub: quick reference cards (Items: one line each, start with + for a tick or - for a cross).',
 'Project Updates': 'Knowledge Hub: project updates (Date as YYYY-MM-DD).',
 'Key Dates': 'Knowledge Hub: key dates, counted from the go-live date (OffsetDays / OffsetMonths).',
 'Support Contacts': 'Knowledge Hub: who to contact.',
 'Key Messages': 'The scrolling banner of key messages.',
}
NOTES = {
 'lines': 'Multiple lines of text (plain). One item per line.',
 'pairs': 'Multiple lines of text (plain). One per line, written  Heading | text',
 'note': 'Multiple lines of text (plain text, not rich text).',
}
TYPE = {'text': 'Single line of text', 'note': 'Multiple lines of text (plain)', 'lines': 'Multiple lines of text (plain)', 'pairs': 'Multiple lines of text (plain)',
        'number': 'Number', 'bool': 'Yes/No', 'choice': 'Choice'}
EXTRA = {
 ('Journey Stages', 'PanelPoints'): 'One per line: Heading | text',
 ('Staff Guides', 'Steps'): 'One per line: Heading | text',
 ('Programme Phases', 'Focus'): 'One bullet per line',
 ('Programme Phases', 'Materials'): 'One per line: p | p1 (a poster) or h | faq (a Knowledge Hub tab)',
 ('Quick Reference Cards', 'Items'): 'One line each. Start with + (tick) or - (cross)',
 ('Customer Changes', 'Points'): 'One bullet per line',
 ('Key Dates', 'Format'): 'Choices: Week, Day, Full',
 ('Training Media', 'Type'): 'Choices: Video, Picture',
 ('Project Updates', 'Date'): 'Write as YYYY-MM-DD, e.g. 2026-10-19',
 ('Customer Changes', 'Alt'): 'Yes gives the card the alternate (darker) style',
 ('Customer Changes', 'Viz'): 'Yes adds the small "00 + your CIF" picture (used on the Account Numbers card only)',
 ('Page Settings', 'Value'): 'Examples: GoLive = 2027-02-01T00:00:00+00:00; CurrentPhase = 1 (0 to 5)',
}

def cols(d):
    c = []
    title = d.get('titleLabel') or d.get('titleProp') or 'Title'
    c.append(('Title', 'Title (already exists)', 'Rename its display label to "%s" if you like (optional). Do not delete it.' % title))
    for f in d['fields']:
        if d['kind'] == 'posters' and f['n'] == 'ImageFile': continue
        t = TYPE[f['t']]
        note = EXTRA.get((d['list'], f['n']), NOTES.get(f['t'], ''))
        if f['n'] == 'Icon' and not note: note = 'Name of a built-in icon (copy the one in the example row, e.g. users, heart, eye)'
        if f['t'] == 'choice': note = 'Choices: ' + ', '.join(f['choices'])
        c.append((f['n'], t, note))
    c.append(('Order', 'Number', 'Sort position (1, 2, 3 ...). Smaller shows first.'))
    c.append(('IsActive', 'Yes/No', 'Default value: Yes. Set to No to hide an item without deleting it.'))
    return c

def rowvals(d, r):
    out = [r.get('Title', '')]
    for f in d['fields']:
        if d['kind'] == 'posters' and f['n'] == 'ImageFile': continue
        v = r.get(f['n'], '')
        if f['n'] == 'ImageUrl': v = ''
        out.append(('Yes' if v else 'No') if f['t'] == 'bool' else v)
    out += [r.get('Order', ''), 'Yes' if r.get('IsActive', True) else 'No']
    return out

# ---------------------------------------------------------------- Excel
wb = openpyxl.Workbook(); ws0 = wb.active; ws0.title = 'READ ME'
for i, line in enumerate([
    'Corbit X list content',
    'One sheet per SharePoint list. Row 1 is the column name (type it exactly like this when you create the column).',
    'To fill a list: open it in SharePoint, click "Edit in grid view", then copy the rows (without row 1) from the sheet and paste into the grid.',
    'The sheet name is the exact list name. Column "Title" is the list\'s built-in Title column.',
    'Yes/No columns are written Yes or No. Leave the Posters list\'s ImageUrl empty unless you are replacing a poster image.',
]): ws0.cell(i + 1, 1, line)
ws0['A1'].font = Font(bold=True, size=14); ws0.column_dimensions['A'].width = 140
hdr_fill = PatternFill('solid', fgColor='F26A1B')
for d in schema:
    ws = wb.create_sheet(d['list'][:31])
    header = [c[0] for c in cols(d)]
    ws.append(header)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr_fill
    for r in seed.get(d['list'], []): ws.append(rowvals(d, r))
    for i, h in enumerate(header, 1):
        mx = max([len(str(ws.cell(rr, i).value or '')) for rr in range(1, ws.max_row + 1)] + [8])
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = min(60, mx + 2)
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
wb.save(os.path.join(OUT, 'Corbit_X_List_Content.xlsx'))

# ---------------------------------------------------------------- Word
doc = Document()
sec = doc.sections[0]; sec.left_margin = sec.right_margin = Cm(2); sec.top_margin = sec.bottom_margin = Cm(2)
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)
for n, sz in (('Heading 1', 18), ('Heading 2', 14), ('Heading 3', 12)):
    s = doc.styles[n]; s.font.name = 'Calibri'; s.font.size = Pt(sz); s.font.color.rgb = RGBColor(0xD4, 0x54, 0x0A)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color); tcPr.append(sh)
def table(rows, header, widths=None):
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(c, 'F26A1B')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            p = cells[i].paragraphs[0]; run = p.add_run(str(v)); run.font.size = Pt(9.5)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph()
def steps(items):
    for it in items: doc.add_paragraph(it, style='List Number')
def bullets(items):
    for it in items: doc.add_paragraph(it, style='List Bullet')

t = doc.add_heading('Corbit X Readiness Centre', 0)
doc.add_paragraph('SharePoint set-up guide: the library and the 25 lists, step by step').runs[0].font.size = Pt(14)
doc.add_paragraph('Use this guide to create everything by hand in SharePoint (no PowerShell). Two companion files come with it: the web part package and Corbit_X_List_Content.xlsx, which holds the starting content for every list so you can paste it in instead of typing it.')

doc.add_heading('1. What you need', 1)
bullets(['You are an owner of the SharePoint site (Site Owners group).',
         'The web part package corbit-x-journey.sppkg, already uploaded to the App Catalog and added to the site (Site contents > New > App).',
         'The folder "setup" from the package: it contains the poster images (posters) and the voice recordings (voice\\emily).',
         'Corbit_X_List_Content.xlsx (the starting content).',
         'About 2 to 3 hours the first time. Each list takes 5 to 10 minutes.'])
doc.add_paragraph('Important rule: list names and column names must be typed exactly as written in this guide (capital letters, no spaces in column names). The web part finds the lists by name. If a list is missing or empty, the page simply shows its built-in content for that part, so you can build the lists one at a time and nothing breaks.').runs[0].bold = True

doc.add_heading('2. The library (Site Assets): posters and voice', 1)
doc.add_paragraph('You do not create a new library. The page uses the Site Assets library that every SharePoint site already has. You only add folders and files to it.')
steps(['Open your SharePoint site. In the left menu or the gear menu choose Site contents, then open the library called Site assets.',
       'Click New > Folder. Name it exactly: CorbitX. Click Create. Open the CorbitX folder.',
       'Inside CorbitX, click New > Folder, name it posters, Create.',
       'Inside CorbitX, click New > Folder, name it voice, Create. Open voice, click New > Folder, name it emily, Create.',
       'Open the posters folder. Click Upload > Files, select the 6 image files from setup\\posters (p1.jpg to p6.jpg), Open. (You can also drag them into the page.)',
       'Open CorbitX > voice > emily. Click Upload > Files. In the setup\\voice\\emily folder press Ctrl+A to select all the .mp3 files (about 205), click Open. Wait until the upload finishes.',
       'Check: posters has 6 files, emily has about 205 files. The folder path is SiteAssets/CorbitX/voice/emily.'])
doc.add_paragraph('Why the voice files matter: Kukua reads out loud by playing these recordings. If the folder is empty the page still works, but Kukua stays silent. The recordings are matched to the exact wording on the page; if you reword a line, that line has no recording.')

doc.add_heading('3. How to create one list (do this 25 times)', 1)
doc.add_paragraph('Every list is made the same way. Follow these steps once, then repeat for each list in Part 4, using that list\'s own column table.')
doc.add_heading('3.1 Create the list', 2)
steps(['On the site, click New (or the + New button) > List.',
       'Choose Blank list.',
       'Name: type the list name exactly (for example Journey Stages). Leave "Show in site navigation" ticked. Click Create.'])
doc.add_heading('3.2 Add the columns', 2)
steps(['In the new list click + Add column and choose the column type shown in the guide.',
       'Name: type the column name exactly as in the guide, with no spaces, for example KukuaSays. The name you type now becomes the permanent internal name, so get it right first time. (You can change how it is displayed later, but not the internal name.)',
       'For Multiple lines of text: click More options and make sure "Use rich text" is OFF (plain text). Click Save.',
       'For Number: leave the defaults. Click Save.',
       'For Yes/No: click More options, set "Default value" to Yes (for IsActive), Save.',
       'For Choice: type each choice on its own line (for example Video and Picture), Save.',
       'Repeat for every column in that list\'s table, including the two columns every list has: Order (Number) and IsActive (Yes/No, default Yes).'])
doc.add_paragraph('The built-in Title column already exists. You do not add it. Each list\'s table says what to put in Title.')
doc.add_heading('3.3 Add the content', 2)
steps(['Open the Excel file Corbit_X_List_Content.xlsx and open the sheet with the same name as the list.',
       'Select the cells under the header row (Ctrl+A, then deselect row 1) and copy (Ctrl+C).',
       'In SharePoint open the list and click Edit in grid view. Click the first empty cell of the Title column and paste (Ctrl+V). Click Exit grid view.',
       'Check that every row shows the right text and that IsActive says Yes. If a multi-line cell pasted badly, open the item and paste it into the field directly.',
       'Alternative: click + New and type each item by hand using the sample row shown for the list.'])
doc.add_heading('3.4 Showing and hiding items', 2)
doc.add_paragraph('To hide an item without deleting it set IsActive to No. To change the order change the Order number (smaller shows first). Changes appear on the page the next time it loads; no republishing is needed.')

doc.add_heading('4. The 25 lists', 1)
doc.add_paragraph('Each list below shows its purpose, the columns to create, and the first row as an example. The complete rows are in the Excel file.')
for i, d in enumerate(schema, 1):
    doc.add_heading('List %d: %s' % (i, d['list']), 2)
    doc.add_paragraph('Purpose: ' + PURPOSE[d['list']])
    rows = [(a, b, c) for a, b, c in cols(d)]
    table(rows, ['Column (type this name)', 'Type', 'Notes'], [4.2, 4.8, 8.0])
    sd = seed.get(d['list'], [])
    doc.add_paragraph('Items to start with: %d.' % len(sd)).runs[0].italic = True
    if sd:
        vals = rowvals(d, sd[0]); names = [c[0] for c in cols(d)]
        ex = [(n, (str(v)[:160] + ('…' if len(str(v)) > 160 else '')).replace('\n', ' / ')) for n, v in zip(names, vals) if str(v) != '']
        doc.add_paragraph('Example (first row):').runs[0].bold = True
        table(ex, ['Column', 'Value'], [4.2, 12.8])

doc.add_heading('5. Lock the lists so only owners can edit', 1)
doc.add_paragraph('Do this for each of the 25 lists, and once for the CorbitX folder.')
doc.add_heading('5.1 Each list', 2)
steps(['Open the list. Click the gear (Settings) at the top right > List settings.',
       'Click Permissions for this list.',
       'Click Stop Inheriting Permissions, then OK.',
       'Tick the group Visitors and the group Members (names look like "<Site name> Visitors" and "<Site name> Members"). Click Edit User Permissions.',
       'Choose Read (not Edit, not Contribute). Click OK.',
       'Leave the Owners group as Full Control. To also give one named person control, click Grant Permissions, type their name, choose Full Control.'])
doc.add_heading('5.2 The CorbitX folder in Site Assets', 2)
steps(['Open Site assets. Tick the CorbitX folder, then click the ... menu > Manage access (or Details > Manage access).',
       'Click Advanced (or Stop inheriting permissions), then remove edit rights from Members and give them Read only. Owners stay Full Control.'])
doc.add_heading('5.3 The page itself', 2)
steps(['Open Site Pages and find your page. Click ... > Manage access (or Page details > Permissions).',
       'Stop inheriting permissions. Give Owners Edit, everyone else Read.'])
doc.add_paragraph('Visitors must be able to read the lists, otherwise the page falls back to its built-in text. That is why they get Read, not "no access".')

doc.add_heading('6. Put the web part on a page', 1)
steps(['Site contents > Site pages > New > Site page > Blank. Name it, for example Corbit X Readiness Centre.',
       'Click the + at the top left of the page, choose Layout and add a Full-width section (or One column).',
       'Click the + inside the section, search for "Corbit X Journey" and add it.',
       'Click Publish.',
       'Open the page. Kukua\'s player appears at the bottom left. In a browser that blocks sound, click once anywhere on the page and she starts reading.'])

doc.add_heading('7. Quick checks and problems', 1)
table([
 ('A part of the page still shows old/built-in text', 'The list name or a column name has a typo, or the list has no active items. Check the spelling against this guide.'),
 ('Kukua is silent', 'The voice folder is empty or the path is not SiteAssets/CorbitX/voice/emily. Or you reworded a line (its recording no longer matches).'),
 ('A column shows odd characters or all text on one line', 'The column is rich text, or the line breaks did not paste. Recreate it as plain multiple lines of text.'),
 ('Changes do not show', 'Refresh the page (Ctrl+F5). Check IsActive is Yes.'),
 ('Visitors see nothing from the lists', 'They need Read on the lists (see Part 5).'),
 ('The go-live date is wrong', 'Open Page Settings, row GoLive. Use the format 2027-02-01T00:00:00+00:00.'),
], ['Problem', 'What to do'], [6.0, 11.0])

doc.add_heading('8. The faster way (optional)', 1)
doc.add_paragraph('If you have PowerShell and the PnP.PowerShell module, one command creates all 25 lists, fills them, uploads the posters and voice, and locks everything:')
doc.add_paragraph('.\\Provision-CorbitXPortal.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<site> -OwnerEmail you@yourbank.com').runs[0].font.name = 'Consolas'
doc.save(os.path.join(OUT, 'Corbit_X_SharePoint_Setup_Guide.docx'))
print('written', os.listdir(OUT))
