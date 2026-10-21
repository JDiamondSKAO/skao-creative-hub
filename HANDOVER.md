# Creative Hub handover (21 October 2026)

For whoever picks this up next, whether a person or another AI. **This repository is public.** Nothing internal goes in Git: no internal document links, credentials, personal names or staff photos. Those live in local files on the owner's Mac, listed at the end.

## Where things stand

- **Live.** Theme **2.23.0** is uploaded (the newest, **2.24.0**, adds the guided tour, Share your presentation and the new quick links, and is packaged in `release/go-live/theme/`. Before that, 2.23.3 It adds even homepage cards, Hub names in Just added, the Canto slideshow reading Photography Media directly (working on the live site since 2.23.2), side-menu links to the newer pages found through the site tree, and drawn slideshow icons. Upload its 9 files over the old ones.) to the Scroll Viewport site for the Confluence space `CRH` (21 October 2026).
  - Its code is on branch `claude/creative-hub-v2.23`.
  - Each release from 2.17 to 2.23 sits on its own branch, built on the one before.
  - None is merged into `main`, which is still at 2.16. Merge 2.23 into `main` once the owner is happy with the live site.
- **Files.** The brand files are attached to their pages (75 files) by `scripts/upload_kit.py --upload`.
- **Events is hidden for now.** `HIDDEN_SECTIONS` in `scripts/polish.py` keeps it out of the menus, homepage, All files and search. Its pages and code are kept for a later review.
- **The Canto staff portal link** is called **Staff Resources Portal** across the Hub. That's the owner's choice, so keep it.
- `CHANGELOG.md` has the detail of every release.

## Open now: the Photos and video slideshow isn't showing

The slideshow on Photos and video, and the video strips on Video and animation, are built from attachments on the **Photography Media** page (ID 381891718): `canto-showcase.json` plus about 75 `canto-*.jpg` images. Nothing appears until they're there, which is by design.

1. **Publish the saved snapshot.** Run `python3 scripts/canto_sync.py --publish` from the repo folder.
   - It uploads `build/canto`, a snapshot from 20 October: 75 images in 8 collections.
   - It asks for a Confluence personal access token (Profile → Settings → Personal Access Tokens). The token is typed into the terminal and never stored.
   - It prints progress every 15 images and ends with "Published 75 images and canto-showcase.json … to page 381891718".
2. **Status, 21 October.** The publish succeeded (75 images), but theme 2.23.1 still showed nothing, because it found the manifest only through Confluence search. Theme 2.23.2 reads the page's attachments directly and should fix it.
3. **If 2.23.2 still shows nothing**, open the browser console on Photos and video and look for a message starting "Creative Hub:". Then work through these in order:
   - Open Photography Media → ••• → Attachments in Confluence. The json and the images should be there.
   - Wait a minute. The theme finds the json through Confluence search (`loadCanto` in `js/main.js`, which searches for `title="canto-showcase.json"` in space CRH), so search has to index it first.
   - Check that another live feature that uses the same REST search works. For example, Letterheads should list 10 files. If it doesn't, the problem is REST from the site, not Canto.
   - Open the browser's developer tools on Photos and video and look at the Network tab. Check the `/rest/api/content/search` request for the json, then the json download. Look for errors in the Console.
4. **Keep it fresh with the scheduled sync.** `python3 scripts/canto_sync.py` with Canto credentials and a Confluence token (see the README) fetches the newest pictures and replaces the snapshot. Run it daily from a scheduler that keeps both as secrets. Rotate the Canto App Secret before setting this up.

## Still to do

- **Set up the Confluence side** (for staff who use "View in Confluence"). Not done as of 21 October.
  - `python3 scripts/confluence_text.py --apply` covers all of it:
    - creates the 3 newer pages (Partner templates, Construction overview, Partner logos), which don't exist yet; until they do, theme 2.23.3 hides links to them;
    - replaces the March placeholder text on the Hub's 35 pages, home page included, with the Hub's text and Attachments lists;
    - makes the 16 page-tree moves.
  - Review first with `python3 scripts/confluence_text.py`.
  - Then `python3 scripts/confluence_cleanup.py --apply` moves 29 pages to the space trash, children first: the 24 old pages, whose content is on other Hub pages, and the 5 Events pages. It keeps any page that still has a Hub page under it, and never purges the trash. The owner asked for this on 21 October: only what's on the Hub is approved.
  - Then run `python3 scripts/upload_kit.py --upload "Partner templates" "Partner logos"`. Reruns skip files that are already up.
  - Optional: set `HUB_SITE` in `dev/links.json` to the Hub's address, so each page opens with a note pointing to the Hub.

- **The page buttons.** "Open the Canto library" buttons on the media pages could become "Open the Staff Resources Portal". This is waiting for the owner's decision.
- **IT service desk link.** It's the only link still missing (`IT_SERVICE_DESK` in `scripts/links.py`). Add its address to the local `dev/links.json`, then package and upload the theme again.
- **Approved slide decks.**
  - Talk decks need lighter copies under 100 MB, named `YYYY-MM Title.pptx`, labelled `approved`.
  - Put the details in the attachment comment: `Speaker: … · Event: …`.
  - A JPG with the same name becomes the deck's cover.
- **Events pages in Confluence** go to the trash with the clean-up. When Events comes back, restore them first (Space tools → Content Tools → Trash), so they keep the page IDs in `scripts/interiors.py`. If they were purged, create them again and update those IDs.
- **Events.** Review it, then bring it back. Restore its 5 Confluence pages from the trash, take `'Events'` out of `HIDDEN_SECTIONS`, and upload its files (`build/kit`, `build/event-files`).
- **Brand bank flags.**
  - The Brand Book file is called v2 but its cover says v1.2.
  - On the colour sheet, `#9B6017` has the wrong RGB values (they should be 155, 96, 23).

## Share your presentation form (to finish)

The page (2.24.0) is ready, and its button opens the Comms helpdesk until the form exists.

1. In Airtable, open the **Creative Hub feedback** base, table **Shared presentations** (already set up).
2. Make a form for it, an interface form like the feedback one. Include every field except Status and Review notes.
3. Copy the form's share link into the local `dev/links.json` as `"SHARE_DECK_FORM"`.
4. Run `python3 scripts/package.py` and upload the theme again.

## How to work on it

- **Edit the sources only:** `scripts/*.py`, `js/main.js` and `css/style.css`. `docs/` and `page.vm` are generated, so never edit them by hand.
- **Build:** `python3 scripts/build.py`.
- **Test:** `node scripts/test.cjs`. It must exit 0, so check the exit code rather than the last line of output.
- **Package:**
  1. Bump the version in `scripts/package.py`, then run `python3 scripts/package.py`.
  2. Upload the 9 files from `release/skao-creative-hub-v<version>-flat-upload.zip` in the Scroll Viewport theme editor, replacing the files there.
  3. The zip carries the internal links from `dev/links.json`. The committed files never do, and the build checks this.
- **Test locally:**
  - Run `python3 scripts/dev_fixtures.py`, then `python3 scripts/dev_server.py`, and open http://127.0.0.1:8767.
  - Add `?fresh` to see the Hub as a first-time visitor would.
- **Attach files:** `python3 scripts/upload_kit.py` gathers them into `release/go-live/files/<page>/`, and `--upload` attaches and labels them. Neither ever deletes anything.
- **House rules:**
  - Staff never see placeholders.
  - Use plain described steps, not tick-list checklists.
  - Don't leave empty gaps in grids.
  - Use the house style: no "master deck" (it's the SKAO slide deck) and "Square Kilometre Array Observatory" in full where it fits.
  - Brand source folders in Dropbox are read only.

## Local-only files on the owner's Mac (not in Git, on purpose)

- `GO-LIVE.md`: the step-by-step go-live guide (pages, moves, files, theme, checks).
- `UPLOAD-PLAN.md`: the fuller Confluence plan, including the list of old pages.
- `dev/links.json`: internal document links that `package.py` builds into the release.
- `dev/brandbank-map.json`: where the brand files sit on the Mac.
- `dev/canto.env`: Canto and Confluence credentials. Never print, copy or commit them.
- `build/`: generated pictures and the Canto snapshot (`build/canto`).
- `release/`: the packaged themes, and `release/go-live/`, which holds the theme files and the files per page.
