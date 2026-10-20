# Corbit X Journey: SPFx portal with SharePoint lists as the CMS

The approved design (`preview/Corbit_X_Journey.html`) as an SPFx 1.18 web part. **Every piece of text, tip, FAQ, poster,
number and link comes from SharePoint lists**, so you change the portal by editing list items, with no code and no redeploy.

## One-time setup
```
npm install
gulp bundle --ship && gulp package-solution --ship        # -> sharepoint/solution/corbit-x-journey.sppkg
```
1. Upload the `.sppkg` to the App Catalog and add the app to your site. Node 18.17+ is required.
2. Create the lists and posters (PnP.PowerShell):
   `.\seed\Provision-CorbitXPortal.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<site>`
   This creates the 13 lists, fills them with the current content, and uploads the six posters to `SiteAssets/CorbitX/posters`.
3. Edit a page, add the **Corbit X Journey** web part in a full-width section, publish.

Until the lists exist, or while a list is empty, the web part shows its built-in content, so it never appears blank.

## What you edit, and where
Every list also has **Order** (sort position) and **IsActive** (untick to hide an item without deleting it). Add, remove, reorder or hide items freely.

| Page section | List | Key columns |
|---|---|---|
| Kukua's spoken/bubble lines | Kukua Messages | Title = key (`welcome`, `journeyIntro`, `start`, `finish`, `closing`, `chatGreeting`, `chatFallback`), Text, AudioUrl |
| Intro line under each section heading | Section Intros | Title = key, Text |
| The six journey stops and their guide panels | Journey Stages | Title, RailLabel, PosterId, KukuaSays, SecondaryLabel, PanelKukua, PanelIntro, PanelPoints (one per line: `Heading \| text`), PanelNote, KeyMessage |
| Poster images and titles | Posters | PosterId (p1 to p6), Title, ImageUrl. Replace the image file in `SiteAssets/CorbitX/posters`, or point ImageUrl elsewhere |
| Highlights so far (the animated numbers) | Highlights | Title = label, Group, Icon, Value, Suffix, ShowBar |
| Big Changes for customers | Customer Changes | Title, Points (one per line) |
| What's in it for staff (Today vs Corbit X) | Staff Changes | Title, Icon, Today, CX, Gain |
| Training videos and pictures | Training Media | Title, Type (Video/Picture), Description, Url |
| What's next | What's Next | Title, Label, Text, Icon |
| Daily tip card (random each visit) | Daily Tips | Title = the tip |
| Ask Kukua answers and suggested questions | FAQs | Title = question, Answer, Keywords, Suggested, ActionLabel, ActionTarget |
| Featured guide (rotates weekly in Order) | Featured Guides | Title, PosterId, KukuaCommentary |
| Latest updates | Announcements | Title, Body, Icon |

`PosterId` links a stop or featured guide to its poster. To add a seventh stop, add a poster (p7) and a Journey Stages item that uses it.

## Kukua's voiceover
Narration plays one fixed recording for every visitor; nothing depends on voices installed on the visitor's device.
The 31 MP3s (every spoken line: messages, stops, section intros, stop panels, featured guides) (neural voice `af_heart`, American female) are in `seed/voice/emily/`, and the provisioning script uploads them to
`SiteAssets/CorbitX/voice/emily/`: `welcome`, `journeyIntro`, `start`, `finish`, `closing`, `chatGreeting`, `chatFallback`, `stage1` to `stage6`.
A recording is matched to the on-screen text, so if you reword a line the old recording stops matching: put the new MP3 URL in that item's
AudioUrl column (or re-record). To use another folder, set the web part's *Voice files folder URL*. If a file is missing the text still shows and Kukua is silent.

## Changing the design itself
The look is `preview/Corbit_X_Journey.html`. After editing it, regenerate the web part sources:
```
cd tools && npm i && cd ..
python3 tools/extract-portal.py && python3 tools/build-seed.py
```
Files under `src/webparts/corbitXJourney/portal/` marked GENERATED are overwritten by that command. The list definitions live in `portal/schema.json`.

## Notes
* Fonts (Barlow) load from Google Fonts. If your tenant blocks that, the page falls back to Arial.
* Lists are read with the visitor's own permissions, so give visitors read access to the Corbit X lists and let only your editors have edit rights.
