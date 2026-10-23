#!/usr/bin/env python3
"""Content update from the go-live staff briefing (1 Feb 2027). Edits the content in the two design sources and the defaults.
Run once:  python3 tools/apply-content-update.py     then rebuild with tools/merge-readiness.py (see README)."""
import json, os, re, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

# ======================================================================= Kukua's lists
L = json.load(open(P('seed/before/defaults.json'), encoding='utf8'))
M = {m['Key']: m for m in L['KukuaMessages']}
M['welcome']['Text'] = "Hello! I'm Kukua, your Corbit X guide. Between now and go-live on Monday 1 February 2027, I'll help you discover what Corbit X means for our customers, branches, and teams. Let's get started."
M['chatFallback']['Text'] = "Good question! I don't have an answer for that one yet. Try one of the suggested questions, or check the guide, ask your champion, and log a Command Centre ticket if you are still stuck."
I = {m['Key']: m for m in L['SectionIntros']}
I['highlights']['Text'] = "Look how far we've come together! Our simulation score rose from 51% to 93.4%, and confidence has nearly doubled."
I['next']['Text'] = "So, what's next? Here are the five steps that take us from today to go-live on Monday 1 February 2027."

S = {s['Order']: s for s in L['JourneyStages']}
S[1]['PanelIntro'] = "Old account numbers will continue to be accepted for more than six months after go-live. The new account number has 13 digits, and a customer's CIF gains “00” in front."
S[2]['PanelIntro'] = "Cheques bearing old account numbers are accepted for six months (182 days) after go-live, until 2 August 2027, subject to the usual checks. After that date, these cheques will no longer be accepted."
S[2]['PanelPoints'][0] = ["Accept", "Accept old-number cheques until 2 August 2027, subject to the usual checks."]
S[4]['PanelIntro'] = "On Sunday 31 January 2027, the day before go-live, BOSs will open the branch day. All branch staff will take part in live transaction and channel checks."
S[4]['PanelPoints'] = [
    ["Friday 29 January", "Finish all transactions by the 2:00pm cut-off, balance cash and vault, clear suspense and run the final end of day."],
    ["Test", "On Sunday, test deposits, branch transactions, ATMs, the mobile app and other instructed channels."],
    ["Real funds", "These are real transactions with real funds. Follow controls and report issues promptly."],
    ["Don't close", "Do not close the branch day or run end of day on Sunday."],
    ["Continue", "Continue the same branch day into Monday 1 February. Run end of day at the close of business on Monday."]]
S[6]['PanelIntro'] = "During the static data freeze in the week before go-live and the first three days after go-live (Monday 1 to Wednesday 3 February), account opening is unavailable in Flexcube 11.1 and Corbit X."
S[6]['PanelPoints'][2] = ["Finalise", "Finalise from Thursday 4 February and provide account numbers."]

L['Highlights'] = [
    {"Group": "Overall readiness", "Icon": "sim", "Items": [
        {"Value": 93.4, "Suffix": "%", "Label": "Overall simulation score (95% go-live gate)", "Bar": True},
        {"Value": 85, "Suffix": "%", "Label": "Staff confident in go-live readiness (45% at BSIM 1)", "Bar": True}]},
    {"Group": "System and support", "Icon": "check", "Items": [
        {"Value": 99.8, "Suffix": "%", "Label": "Logged in at BSIM 4"},
        {"Value": 96, "Suffix": "%", "Label": "Tickets fixed the same day"}]},
    {"Group": "Branches", "Icon": "users", "Items": [
        {"Value": 94, "Suffix": "%", "Label": "Branches ready"},
        {"Value": 4, "Suffix": "", "Label": "Business simulations completed"}]}]

C = {c['Title']: c for c in L['CustomerChanges']}
C['At the Counter']['Points'] = ["Quicker service at the counter", "360-degree customer view at the teller point", "Faster credit and salary processing"]
C['Account Numbers']['Points'] = ["New 13-digit account numbers", "Customer CIF gains “00” in front", "Old numbers still work for more than six months"]
C['Cheque Books']['Points'] = ["Reorder within the first 182 days", "Current leaves accepted in the meantime", "Books over 5 years old are not migrated"]
C['Statements']['Points'] = ["0–12 months: straight from Corbit X", "Older statements, back to account opening: from stored backup"]

for m in L['TrainingMedia']:
    if m['Title'] == 'Account opening during the freeze': m['Description'] = 'Start in Newgen, finalise from Thursday 4 February'

L['WhatsNext'] = [
    {"Label": "26 Oct – 23 Dec", "Title": "Keep your skills sharp", "Text": "Practise twice a week. Branches 7:15 – 8:15 am; departments one hour, two days a week.", "Icon": "cap"},
    {"Label": "24 Dec – 3 Jan", "Title": "Rest and recharge", "Text": "No scheduled sessions. The Corbit X portal stays open if you want a refresher.", "Icon": "heart"},
    {"Label": "4 – 22 Jan", "Title": "Get go-live ready", "Text": "One hour every working day, then certification for your role.", "Icon": "check"},
    {"Label": "11 – 17 Jan", "Title": "Final systems check", "Text": "Data migration and validation, then the business simulation on Sunday 17 January.", "Icon": "sim"},
    {"Label": "Mon 1 Feb 2027", "Title": "Lift-off!", "Text": "Corbit X goes live. Arrive early, log in and welcome every customer.", "Icon": "rocket"}]

L['DailyTips'] += ["Stuck? Check the guide, ask your champion, log a Command Centre ticket, then update the customer.",
                   "The bank never asks for a PIN, password or OTP. Never share your login."]

F = {f['Question']: f for f in L['FAQs']}
F['How will customers benefit?']['Answer'] = "Quicker service at the counter, a 360-degree customer view at the teller point, faster credit and salary processing, statements for the last 12 months straight from Corbit X and a more secure 13-digit account number. While we transition, old account numbers keep working for more than six months after go-live, and cheques with old numbers are accepted until 2 August 2027."
F['What changes for branches?']['Answer'] = "A few things to know: new account numbers (look them up in Corbit X and share them), cheque and chequebook changes, a short pause in account opening around go-live, and live checks on Sunday 31 January 2027. Each one has a stop on the journey."
F['Where can I find guides?']['Answer'] = "Right here! There are six guides on my journey. Tap 'View Guide' on any stop to see the full poster. You will also find guides, staff FAQs and how-to videos on the Corbit X portal on the info portal."
F['Who can I contact for support?']['Answer'] = "Check the guide or FAQ first, then ask your champion or team lead. If you are still stuck, log a Command Centre ticket with a screenshot, and keep the customer updated while you wait. Contact details for the Command Centre will be listed here."
F['Will old account numbers still work?']['Answer'] = "Yes. Old account numbers will continue to be accepted for more than six months after go-live. The new account number has 13 digits, and the CIF keeps the same number with “00” added in front. Look up the new number in Corbit X and share it with the customer."
F['Can we open accounts during the upgrade?']['Answer'] = "Account opening pauses during the static data freeze and the first three days after go-live (Monday 1 to Wednesday 3 February). Start the application in Newgen, receive deposits through the designated GL, and finalise from Thursday 4 February."
F['How do statements work in Corbit X?']['Answer'] = "Statements for the last 12 months come straight from Corbit X. Older statements, back to when the account was opened, come from stored backup."
F['What about cheques?']['Answer'] = "Cheques with old account numbers are accepted for six months (182 days) after go-live, until 2 August 2027, subject to the usual checks. Chequebooks recorded more than five years ago won't be migrated, so help those customers find an approved alternative. Encourage everyone to reorder early."
F['What happens on the Sunday before go-live?']['Answer'] = "On Sunday 31 January 2027, BOSs open the branch day and all branch staff run live transaction and channel checks with real funds. Don't close the branch day or run end of day on Sunday; continue into Monday and run end of day at close of business."
L['FAQs'] += [
    {"Question": "When does Corbit X go live?", "Keywords": "when date go-live golive live start monday february 2027 cut-off", "Suggested": False, "Answer": "Corbit X goes live on Monday 1 February 2027, in every branch and department at the same time. The final cut-off on the current system is Friday 29 January at 2:00pm.", "ActionLabel": "See the guide", "ActionTarget": "stop:4"},
    {"Question": "How do I read the new account number?", "Keywords": "account number new 13 digit digits currency customer type format read cif", "Suggested": False, "Answer": "It has 13 digits. Digits 1 and 2 are the currency (00 cedi, 01 dollar, 02 pound, 03 euro). Digit 3 is the customer type (1 individual, 2 non-individual, 3 banks and others). Digits 4 to 11 are a serial number, and digits 12 and 13 are check digits."},
    {"Question": "What if someone asks a customer for their OTP?", "Keywords": "otp pin password fraud scam suspicious login share", "Suggested": False, "Answer": "The bank never asks for a PIN, password or OTP, and you must never share your login. Tell the customer, and report anything suspicious to Fraud and Risk."}]

G = {g['Title']: g for g in L['FeaturedGuides']}
G['Keep the Welcome. Start the Process.']['KukuaCommentary'] = "Account opening pauses briefly, but our welcome never does. Start in Newgen and finalise from Thursday 4 February."

L['Announcements'] = [
    {"Title": "Go-live is now Monday 1 February 2027", "Body": "Go-live has moved to accommodate other important transactions the Bank is undertaking. The extra weeks help us go live with even greater confidence.", "Icon": "spark"},
    {"Title": "Six Corbit X staff guides are now available", "Body": "Explore them all on Kukua's journey, from account numbers to go-live readiness.", "Icon": "cap"},
    {"Title": "Look-up process included in training", "Body": "Training covers how to find a customer's new account number in Corbit X.", "Icon": "print"}]

json.dump(L, open(P('seed/defaults.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
open(P('src/webparts/corbitXJourney/portal/defaultLists.ts'), 'w', encoding='utf8').write(
    '// GENERATED by tools/apply-content-update.py. Do not edit.\n/* eslint-disable */\nexport const DEFAULT_LISTS: any = ' + json.dumps(L, ensure_ascii=False, indent=1) + ';\n')
block = 'const LISTS = ' + json.dumps(L, ensure_ascii=False, indent=1) + ';\n'
for f in ('preview/Corbit_X_Journey_standalone.html', 'preview/Corbit_X_Journey.html'):
    s = open(P(f), encoding='utf8').read()
    a, b = s.index('const LISTS = {'), s.index('const POSTERS = {')
    s = s[:a] + block + s[b:]
    open(P(f), 'w', encoding='utf8').write(s)

# ======================================================================= Readiness Centre
R = json.load(open(P('seed/before/rc-defaults.json'), encoding='utf8'))
PO = {p['id']: p for p in R['POSTERS']}
PO['p2']['intro'] = "During the static data freeze in the week before go-live and the first three days after go-live (Monday 1 to Wednesday 3 February 2027), account opening is unavailable in Flexcube 11.1 and Corbit X."
PO['p2']['steps'][2] = ["Finalise", "Finalise from Thursday 4 February 2027 and provide account numbers."]
PO['p3']['intro'] = "Old account numbers will continue to be accepted for more than six months after go-live. The new account number has 13 digits, and a customer's CIF gains “00” in front."
PO['p4']['intro'] = "Accept cheques bearing old account numbers for six months (182 days) after go-live, until 2 August 2027, subject to the usual checks. After that date, these cheques will no longer be accepted."
PO['p4']['steps'][0] = ["Accept", "Accept old-number cheques until 2 August 2027, subject to the usual checks."]
PO['p6']['intro'] = "On Sunday 31 January 2027, the day before go-live, BOSs will open the branch day. All branch staff will participate in live transaction and channel checks."
PO['p6']['steps'][3] = ["Continue", "Continue the same branch day into Monday 1 February. Run end of day at the close of business on Monday."]

R['PHASES'] = [
 {"n": "Keep your skills sharp", "ic": "cap", "when": "26 Oct – 23 Dec 2026", "d": "Regular practice, so everyone is confident on Corbit X before go-live.",
  "f": ["Practise twice a week, every week", "Branches: 7:15 – 8:15 am. Departments: one hour, two days a week", "Final session: Wednesday 23 December"], "m": [["h", "videos"], ["h", "qrc"], ["p", "p3"]]},
 {"n": "Rest and recharge", "ic": "heart", "when": "24 Dec 2026 – 3 Jan 2027", "d": "A break to celebrate with your loved ones. There are no scheduled sessions.",
  "f": ["No scheduled sessions", "Celebrate with your loved ones", "The Corbit X portal stays open if you want a refresher"], "m": [["h", "faq"], ["h", "videos"]]},
 {"n": "Get go-live ready", "ic": "check", "when": "4 – 22 Jan 2027", "d": "One hour every working day (15 days): a refresher, then certification for your role.",
  "f": ["Branches: 7:15 – 8:15 am. Departments: time set by your HoD", "Complete your refresher, then get certified by 22 January", "Champions check in on your practice; BOSs, BSSMs and HoDs make sure every session happens"], "m": [["h", "videos"], ["h", "qrc"], ["p", "p3"], ["p", "p2"]]},
 {"n": "Final systems check", "ic": "chart", "when": "11 – 17 Jan 2027", "d": "Before lift-off, we make sure every record lands safely in Corbit X. Then we fly a full practice mission together on Sunday 17 January.",
  "f": ["Mon 11 Jan: static data migration", "Wed 13 – Fri 15 Jan: data validation. Sat 16 Jan: financial validation", "Sun 17 Jan: business simulation (migration plus a full day of business replay)"], "m": [["h", "dates"], ["h", "contacts"]]},
 {"n": "Lift-off weekend", "ic": "rocket", "when": "Fri 29 Jan – Mon 1 Feb 2027", "d": "Friday 29 January is the last day on the current system, with a 2:00pm cut-off. Sunday 31 January is the live-check day. Monday 1 February is go-live.",
  "f": ["Fri 29 Jan: finish all transactions by 2:00pm, balance cash and vault, run the final end of day", "Sun 31 Jan: BOSs open the branch day and all staff run live checks with real funds. Do not close the day or run end of day", "Mon 1 Feb: arrive by 7:00am, log in, check printers and apps, welcome every customer and run end of day at close of business"], "m": [["p", "p6"], ["p", "p1"], ["h", "dates"]]},
 {"n": "After go-live", "ic": "heart", "when": "From Mon 1 Feb 2027", "d": "Support for customers and colleagues through the first days, weeks and months.",
  "f": ["Mon 1 – Wed 3 Feb: start account openings in Newgen. Accounts are finalised from Thu 4 Feb", "First weeks: hypercare, with daily check-ins, the Command Centre on call and champions on the floor", "Old-number cheques are accepted until 2 August 2027, and old account numbers are still accepted"], "m": [["p", "p2"], ["p", "p3"], ["p", "p4"], ["p", "p5"], ["h", "contacts"]]}]

FQ = {f[0]: f for f in R['FAQS']}
FQ["Will customers' old account numbers still work after go-live?"][1] = "Yes. Old account numbers will continue to be accepted for more than six months after go-live. The new account number has 13 digits, and the CIF gains “00” in front. Look up the new number in Corbit X using the process covered in training, serve the customer, and share the new number so they use it next time."
FQ["Can customers still use cheques that show their old account number?"][1] = "Yes, for six months (182 days) after go-live, until 2 August 2027, subject to the usual checks. After that date these cheques will no longer be accepted, so encourage customers to request new chequebooks early."
FQ["Can we open new accounts during the upgrade?"][1] = "Account opening is unavailable in Flexcube 11.1 and Corbit X during the static data freeze (the week before go-live) and for the first three days after go-live (Monday 1 to Wednesday 3 February). Start the application in Newgen, receive deposits through the designated GL, and finalise from Thursday 4 February. Never turn a customer away."
FQ["What happens on the Sunday before go-live?"][1] = "On Sunday 31 January 2027, BOSs will open the branch day and all branch staff take part in live transaction and channel checks: deposits, branch transactions, ATMs, the mobile app and other instructed channels. These are real transactions with real funds. Do not close the branch day or run end of day on Sunday; continue into Monday and run end of day at close of business."
R['FAQS'] = [
 ["When does Corbit X go live?", "Corbit X goes live on Monday 1 February 2027, in every branch and department at the same time. The final cut-off on the current system is Friday 29 January at 2:00pm.", "p6"]] + R['FAQS'] + [
 ["How do I read the new account number?", "It has 13 digits. Digits 1 and 2 are the currency (00 cedi, 01 dollar, 02 pound, 03 euro). Digit 3 is the customer type (1 individual, 2 non-individual, 3 banks and others). Digits 4 to 11 are a serial number, and digits 12 and 13 are check digits. Always add “00” in front of an existing CIF.", "p3"],
 ["What should I do if I'm stuck?", "Check the repository guide or FAQ, then ask your champion or team lead. If you are still stuck, log a Command Centre ticket with a screenshot, and update the customer while you wait.", "p1"],
 ["What if someone asks a customer for their OTP?", "The bank never asks for a PIN, password or OTP, and you must never share your login. Tell the customer, and report anything suspicious to Fraud and Risk.", "p1"]]

R['VIDEOS'][2][1] = "Start in Newgen, finalise from Thursday 4 February"
Q = {q[0]: q for q in R['QRC']}
Q['Account numbers'][1] = [["tick", "13 digits: currency (2), customer type (1), serial (8), check (2)"], ["tick", "Add “00” before an old CIF"], ["tick", "Old numbers accepted for more than six months"], ["tick", "Look up and share the new number every time"]]
Q['Cheques'][1] = [["tick", "Old-number cheques: six months (182 days), until 2 August 2027, usual checks"], ["tick", "Encourage new chequebook requests early"], ["x", "Books recorded 5+ years ago can't be used"]]
Q['Account opening'][1] = [["tick", "Start in Newgen, collect all documents"], ["tick", "Deposits via the designated GL"], ["tick", "Finalise from Thursday 4 February"]]
Q['Go-live weekend'][1] = [["tick", "Fri 29 Jan: finish transactions by the 2:00pm cut-off"], ["tick", "Sun 31 Jan: live checks with real funds"], ["x", "No branch-day close or EOD on Sunday"], ["tick", "Mon 1 Feb: arrive by 7:00am; EOD at close of business"]]
Q['Every customer'][1] = [["tick", "Smile & serve. Keep customers informed"], ["tick", "Listen calmly; pause and check if unsure"], ["x", "Never turn a customer away"], ["x", "Never share your login, PIN or OTP"]]
R['QRC'].append(["BOS authorisers", [["tick", "KYC first (STSKYCMN): search by KYC Reference, not by status"], ["tick", "Then CIF (STSCIF): authorise only after the KYC is done"], ["tick", "Cheque book request (CASCHBOO): the account must already be open"]]])

R['UPDATES'] = [
 ["2026-10-23", "Go-live moves to Monday 1 February 2027", "Go-live has moved to accommodate other important transactions the Bank is undertaking. The extra weeks help us go live with even greater confidence."],
 ["2026-10-19", "Staff Guide series complete", "All six Corbit X Staff Guide posters are now available in the gallery, covering customer experience, account and chequebook transition, and go-live operations."],
 ["2026-10-19", "Account-number look-up included in training", "Training covers how to look up a customer's new account number in Corbit X. Complete your modules before go-live."],
 ["2026-09-20", "Business simulation 4: 93.4%", "Our overall simulation score rose from 51% to 93.4% across four simulations, 1.6 points from the 95% go-live gate."],
 ["2026-10-19", "Printing new account numbers", "Guidance on printing new account numbers for customers will follow. Watch this space."]]
R['DATES'] = [
 {"Title": "Static data migration", "Body": "Customer and account data moves to Corbit X.", "Big": False, "Days": -21, "Months": 0, "Fmt": "Day"},
 {"Title": "Data validation begins", "Body": "Every record checked and confirmed, Wednesday 13 to Friday 15 January.", "Big": False, "Days": -19, "Months": 0, "Fmt": "Day"},
 {"Title": "Financial validation", "Body": "Balances checked to the last pesewa.", "Big": False, "Days": -16, "Months": 0, "Fmt": "Day"},
 {"Title": "Business simulation", "Body": "Migration plus a full day of business replay.", "Big": True, "Days": -15, "Months": 0, "Fmt": "Day"},
 {"Title": "Final cut-off, 2:00pm", "Body": "Last day on the current system. Balance cash and vault, clear suspense and run the final end of day.", "Big": False, "Days": -3, "Months": 0, "Fmt": "Day"},
 {"Title": "Sunday live checks", "Body": "BOSs open the branch day; all staff run live transaction and channel checks. Do not close the day or run end of day.", "Big": False, "Days": -1, "Months": 0, "Fmt": "Day"},
 {"Title": "Corbit X go-live", "Body": "Arrive by 7:00am. Continue Sunday's branch day; run end of day at close of business.", "Big": True, "Days": 0, "Months": 0, "Fmt": "Day"},
 {"Title": "Account opening resumes", "Body": "Finalise pending applications and provide account numbers.", "Big": False, "Days": 3, "Months": 0, "Fmt": "Day"},
 {"Title": "Old-number cheques end", "Body": "Six months (182 days) after go-live: cheques bearing old account numbers are no longer accepted.", "Big": True, "Days": 182, "Months": 0, "Fmt": "Full"}]
R['CONTACTS'] = [
 ["user", "Your champion", "First line of help: local support and floor-walking", "[Add name]"],
 ["phoneapp", "Command Centre", "Log a ticket with a screenshot: issues, fixes and coordination", "[Add contact]"],
 ["shield", "Branch Operations Support", "Go-live weekend and branch-day issues", "[Add contact]"],
 ["cap", "Learning & Development", "Training access and completion", "[Add contact]"],
 ["heart", "Customer Experience Team", "Escalated customer concerns", "[Add contact]"],
 ["building", "Fraud and Risk", "Report anything suspicious. The bank never asks for a PIN, password or OTP", "[Add contact]"]]
R['mq'] = ["One Journey. One Platform. One Corbit X.", "Same warm welcome. New system. One team.", "Smile. Check. Serve.", "Look it up. Share it. Keep banking moving.", "Check together. Start strong.", "Never turn a customer away.", "Give customers a head start!", "Here for your journey"]
R['SETTINGS'].update({"GoLive": "2027-02-01T00:00:00+00:00", "CurrentPhase": "0",
    "AnnouncementTitle": "Go-live is now Monday 1 February 2027",
    "AnnouncementBody": "Go-live has moved to accommodate other important transactions the Bank is undertaking. The extra weeks help us go live with even greater confidence. See the new calendar in the timeline below.",
    "AnnouncementDate": "2026-10-23", "FiguresAreIllustrative": "No"})

# ---- write into the Readiness Centre source
def scan_end(src, i):
    depth, q = 0, None
    while i < len(src):
        c = src[i]
        if q:
            if c == '\\': i += 1
            elif c == q: q = None
        elif c in '"\'`': q = c
        elif c in '([{': depth += 1
        elif c in ')]}':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    raise ValueError
def swap(src, name, new):
    m = re.search(r'\bconst ' + re.escape(name) + r'\s*=\s*', src); assert m, name
    e = scan_end(src, m.end()); e += 1 if src[e] == ';' else 0
    return src[:m.start()] + new + src[e:]
J = lambda o: json.dumps(o, ensure_ascii=False, indent=1)
f = P('preview/Corbit-X-Readiness-Centre.html'); s = open(f, encoding='utf8').read()
for name, key in (('POSTERS', 'POSTERS'), ('PHASES', 'PHASES'), ('FAQS', 'FAQS'), ('VIDEOS', 'VIDEOS'), ('QRC', 'QRC'), ('UPDATES', 'UPDATES'), ('CONTACTS', 'CONTACTS'), ('mq', 'mq')):
    s = swap(s, name, 'const %s=%s;' % (name, J(R[key])))
s = swap(s, 'DATES', 'const DATES=' + J(R['DATES']) + '.map(d=>{const t=addMonths(addDays(GO,d.Days),d.Months);const label=d.Fmt==="Week"?fmt(t,{day:"numeric",month:"short"})+" week":d.Fmt==="Full"?fmt(t,{day:"numeric",month:"short",year:"numeric"}):fmt(t,{weekday:"short",day:"numeric",month:"short"});return [label,d.Title,d.Body,!!d.Big]});')
s = re.sub(r'goLive: "[^"]*"', 'goLive: "2027-02-01T00:00:00+00:00"', s, count=1)
s = re.sub(r'currentPhase: \d+', 'currentPhase: 0', s, count=1)
s = re.sub(r'(announcement: \{\s*title: )"[^"]*"(,\s*body: )"[^"]*"(,\s*date: )"[^"]*"',
           lambda m: m.group(1) + json.dumps(R['SETTINGS']['AnnouncementTitle'], ensure_ascii=False) + m.group(2) + json.dumps(R['SETTINGS']['AnnouncementBody'], ensure_ascii=False) + m.group(3) + '"2026-10-23"', s, count=1)
s = s.replace('dataIsIllustrative: true', 'dataIsIllustrative: false')
# timeline wording: steps, not phases
s = s.replace('"Phase "+(i+1)', '(i<5?"Step "+(i+1):"After go-live")').replace('Phase ${i+1} · ${p.when}', '${i<5?"Step "+(i+1):"After go-live"} · ${p.when}')
old = 'Six phases take us from awareness to a stable new platform. Select a phase to see what it means for you and the materials that support it.'
assert old in s
s = s.replace(old, 'Five steps take us to lift-off on Monday 1 February 2027, with support continuing after go-live. Select a step to see what it means for you and the materials that support it.')
# "At a glance" box with the new calendar
a = s.index('<div class="wk">'); b = s.index('</div>\n  <p style="position:relative;margin-top:22px', a)
s = s[:a] + '''<div class="wk">
    <div><small>Fri 29 Jan</small><b>Final cut-off</b><p>Finish all transactions by 2:00pm. Run the final end of day on the current system.</p></div>
    <div><small>Sun 31 Jan</small><b>Live checks</b><p>Real transactions, real funds. No branch-day close or EOD.</p></div>
    <div class="hl"><small>Mon 1 Feb</small><b>Go-live</b><p>Arrive by 7:00am. Same branch day continues. New accounts start in Newgen until Wed 3 Feb. EOD at close of business.</p></div>
    <div><small>Thu 4 Feb</small><b>Finalise</b><p>Complete pending account openings and share new account numbers.</p></div>
  ''' + s[b:]
open(f, 'w', encoding='utf8').write(s)
json.dump(R, open(P('seed/rc-defaults.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('content updated')
