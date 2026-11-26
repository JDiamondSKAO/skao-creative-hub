# Creative Hub handover

Updated 26 November 2026, for whoever picks this up next, whether a person or another AI. Read [AGENTS.md](AGENTS.md) for the working rules and [README.md](README.md) for how the project fits together.

**This repository is public.** Internal links, credentials and working notes live in local files on the owner's Mac, listed at the end.

## Where things stand

- **Live.** Theme **2.25.1** runs on the Scroll Viewport site for the Confluence space `CRH`. It was uploaded and checked on 26 November.
  - **2.25.2 is packaged and ready to upload.** It keeps Just added and All files in the Hub.
  - Only two files differ from what's live: `page.vm` and `main.js`.
  - Branch `main` holds the latest release, and each release is tagged.
- **Confluence is set up.** The Hub's own text is in its pages, the newer pages exist (Partner templates, Partner logos, Construction overview, Share your presentation) and the page tree follows the Hub's sections. Pages the Hub no longer uses were moved to the space trash with `confluence_cleanup.py`, and the Events pages went with them. These scripts were run on 21 October. Running them again is safe. Pages already created or moved are skipped, and each text update is a new page version, so page history can bring back the old text.
- **Access.** Staff view the space through the staff group. If staff can open the homepage but not the pages behind it, check Space tools → Permissions → Restricted Pages, or Inspect Permissions. This happened once at launch.
  - If someone can't see the Hub at all, check the home page's own restrictions. A view restriction there hides every page below it.
- **Files.** The brand files are attached and labelled (`upload_kit.py`).
- **Canto slideshow.** Published from a 20 October snapshot (`canto_sync.py --publish`). The theme reads it straight from the Photography Media page.
- **Share your presentation.** The button opens an Airtable form on the base **Shared presentations** (SKA Communications workspace). The form's address is `SHARE_DECK_FORM` in `dev/links.json`. The review steps and reply templates are in the local `SHARE-YOUR-PRESENTATION.md`.
- **Events is hidden** (`HIDDEN_SECTIONS` in `scripts/polish.py`) until it has been reworked and reviewed. Its designs are still in the code.
- **Review board.** A Miro board holds screenshots of every page with feedback boxes, matching 2.24.5. The side-menu fixes in 2.24.6 to 2.24.8 don't show at board scale.

## Next steps

1. **Upload 2.25.2 and run `confluence_text.py --apply`.**
   - The order no longer matters: since 2.25.1 the live theme finds pages by ID, so the renames are safe.
   - The script replaces each page's text with the Hub's, so check first that nobody has edited the pages directly in Confluence. Page history keeps the old text either way.
2. **Daily Canto sync.** Rotate the Canto App Secret first. Then run `canto_sync.py` from a scheduler that keeps the Canto credentials and a Confluence token as secrets.
3. **IT service desk link.** It's the only link still missing (`IT_SERVICE_DESK`). Add it to `dev/links.json`, package and upload.
4. **Approved slide decks.** Add talk decks to the Approved slide decks page (titled About SKAO Master Deck until 2.25.0).
   - Use lighter copies under 100 MB, named `YYYY-MM Title.pptx` and labelled `approved`.
   - Put the details in the attachment comment: `Speaker: … · Event: …`.
   - A JPG with the same name becomes the deck's cover.
   - Talks shared through the form can come in this way once they're chosen.
5. **Events.**
   1. Restore its five pages from the Confluence trash first, so they keep the IDs in `scripts/interiors.py`.
   2. Take `'Events'` out of `HIDDEN_SECTIONS`.
   3. Upload its files (`build/kit`, `build/event-files`).
6. **Housekeeping.**
   - Empty the Confluence trash once nobody needs the old pages.
   - The older release branches can be deleted, since all their work is in `main`.
7. **Brand bank flags.**
   - The Brand Book file is called v2 but its cover says v1.2.
   - On the colour sheet, `#9B6017` has the wrong RGB values (it should be 155, 96, 23).

## Known quirks

- **Confluence's own CSS reaches the theme** on the live site. It once pushed the side-menu title down and clipped its toggle. Layout-critical spacing is pinned, so keep it that way.
- **Pages are linked through the site's page tree.** Pages added later are found by title, ignoring capitals. Pages that existed at launch are found by page ID, so renaming them in Confluence is safe. If a newer page is renamed, update `interiors.PLANNED`.
- **The Hub starts in light mode.** People can switch with the moon button, and the Hub remembers per browser. The welcome note and the tour are remembered per browser too.
  - **Start fresh**, the small icon beside Take the tour in the footer, shows them again. So does `?fresh` in local test mode.
  - It was added for demos. To take it out, remove the `footer-tools` link in `footer()` in `scripts/build.py`, along with its test.
- **After adding a link name** to `scripts/links.py`, restart the local test server.

## Local-only files on the owner's Mac (not in Git, on purpose)

| File | What it is |
|---|---|
| `dev/links.json` | Internal document links, including the feedback and share forms |
| `dev/brandbank-map.json` | Where the brand files sit on the Mac |
| `dev/canto.env` | Canto and Confluence credentials: never print, copy or commit |
| `GO-LIVE.md` | The step-by-step go-live guide |
| `SHARE-YOUR-PRESENTATION.md` | The Share form wording, review steps and reply templates |
| `UPLOAD-PLAN.md` | The original Confluence plan |
| `build/` | Generated pictures, the Canto snapshot and form covers |
| `release/` | Packaged themes, and `release/go-live/` (theme files, files per page, page text) |
