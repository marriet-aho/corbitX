# Corbit X Readiness Centre with Kukua: SharePoint web part (SPFx 1.18)

One page section containing the Readiness Centre (hero, countdown to go-live, staff guides, timeline, Knowledge Hub, what's coming)
and Kukua's journey (the dashboard is built from the "Highlights so far" figures), with Kukua reading the page section by section. **Every piece of content comes from SharePoint lists, and the
lists are locked so only owners can edit them.**

> **Creating the lists by hand?** See `docs/Corbit_X_SharePoint_Setup_Guide.docx` (step by step) and `docs/Corbit_X_List_Content.xlsx` (the starting content for every list).

## Set-up (4 steps)
1. **Install the app.** Upload `package/corbit-x-journey.sppkg` to the App Catalog, Deploy, then add **Corbit X Journey** to your site (Site contents > New > App).
2. **Create and lock the content.** In PowerShell with PnP.PowerShell installed:
   `.\seed\Provision-CorbitXPortal.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<site> -OwnerEmail you@yourbank.com`
   This creates 25 lists, fills them with the current content, uploads the 6 posters and 205 voice clips to `SiteAssets/CorbitX`, and makes
   **Owners = Full Control, everyone else = Read-only** on every list and on that folder. (`-SkipLock` skips the locking.)
3. **Add it to a page.** Edit a page, add a **full-width section** (or one-column), add the **Corbit X Journey** web part, Publish.
4. **Lock the page itself.** Site Pages > the page > Manage access > Stop inheriting permissions, then give Owners Edit and everyone else Read, so only owners can change the page layout.

Until the lists exist, or if a list is empty, the web part shows its built-in content, so it is never blank.

## Editing (owners only)
Open a list, edit an item. **Order** sorts items and **IsActive** (untick) hides an item without deleting it. Changes appear on the page straight away.

| Part of the page | List | Main columns |
|---|---|---|
| Go-live date, current phase, announcement card | Page Settings | Title = `GoLive` (e.g. `2027-02-01T00:00:00+00:00`), `CurrentPhase` (0 to 5), `AnnouncementTitle`, `AnnouncementBody`, `AnnouncementDate`, `FiguresAreIllustrative` (Yes/No); Value |
| Staff-guide gallery and posters' detail pop-up | Staff Guides, Guide Categories | Title, PosterId, CatId, Short, Intro, Steps (one per line: `Heading \| text`), Key, Say, Note |
| Timeline phases | Programme Phases | Title, Icon, When, Description, Focus (one per line), Materials (`p \| p1` poster, `h \| faq` hub tab) |
| Knowledge Hub | Hub FAQs, Training Videos, Quick Reference Cards (`+` ok / `-` not), Project Updates, Key Dates (offset from go-live), Support Contacts | see each list |
| "What's coming" tiles | Capabilities | Title, Icon, Text, Wide |
| Scrolling key-message banner | Key Messages | Title |
| Kukua's welcome, intros, closing, chat greeting | Kukua Messages, Section Intros | Title = key, Text, AudioUrl |
| Kukua's six journey stops and panels | Journey Stages | Title, RailLabel, PosterId, KukuaSays, SecondaryLabel, PanelKukua, PanelIntro, PanelPoints, PanelNote, KeyMessage |
| Highlights so far (drives the dashboard: bars for items with ShowBar, tiles for the rest), big changes, staff changes, training, what's next | Highlights, Customer Changes, Staff Changes, Training Media, What's Next | see each list |
| Daily tip, featured guide, latest updates | Daily Tips, Featured Guides, Announcements | Title, ... |
| Ask Kukua answers | FAQs | Title = question, Answer, Keywords, Suggested |
| Poster images | Posters | PosterId (p1 to p6), Title, ImageUrl |

## Sound and browsers (so Kukua starts without a click)
Kukua tries to start reading the first section as soon as the page opens, then reads each new section as a visitor scrolls to it.
Browsers only allow sound after a visitor has touched the page once, so on a browser that blocks sound she waits for one tap, click or key press
anywhere (she says so in her player), then starts at the section the visitor is on.
**To make her start with no click for everyone:** ask IT to allow sound for your SharePoint site in Microsoft Edge and Chrome with the
`AutoplayAllowlist` policy (Edge: "Allow media autoplay on a specific list of sites"), for example `https://yourtenant.sharepoint.com`,
deployed by Group Policy or Intune. Individual users can also set Site settings > Sound/Media autoplay > Allow for the site.
If a visitor mutes Kukua, the browser remembers it and she stays quiet on their next visits.

## Go-live celebration
When the countdown reaches zero a full-screen **"We are live!"** pop-up appears (confetti, Kukua, her voice) once per visitor. To preview it, add `?cxlive` to the page address.

## Kukua's voice
Kukua reads each section **when the visitor gets to it** (once per section; she stops if they scroll on). Every section also has a **Hear this section** button that reads all of it, and her player has previous/next section buttons. Timeline phases, Knowledge Hub tabs and FAQs are read when opened. **With a mouse, resting the pointer on an item** (menu items, cards, figure tiles, buttons, tabs, timeline phases and so on) for half a second makes Kukua read it; she stops if the pointer moves away, and stays quiet if she is muted.
The voice is a set of pre-recorded clips in `SiteAssets/CorbitX/voice/emily/`, matched to the **exact on-screen wording**.
If you reword something, that line has no recording and Kukua skips it silently (the text still shows). To get new recordings, re-run
`node tools/list-clips.js && python3 tools/make-page-voice.py` (needs kokoro-onnx, see the script), or ask for them to be re-recorded.
For Kukua's own lines you can also put an MP3 link in the item's **AudioUrl** column.

## Changing the design
The look is generated from `preview/Corbit-X-Readiness-Centre.html` (the Readiness Centre) and `preview/Corbit_X_Journey_standalone.html` (Kukua).
`python3 tools/merge-readiness.py` rebuilds both the single-file preview and the web part sources. Files marked GENERATED are overwritten.
List definitions live in `src/webparts/corbitXJourney/portal/schema.json`.

## Notes
* Fonts (Barlow) load from Google Fonts; if blocked the page falls back to Arial.
* The preview file `preview/Corbit_X_Readiness_Centre_Kukua.html` is a standalone copy with the voice embedded. It is not editable and is only for review.
* Not yet tested inside a real SharePoint tenant. Test on a page first.
