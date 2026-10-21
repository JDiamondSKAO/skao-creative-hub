# Creative Hub handover

Updated 21 October 2026, for whoever picks this up next, whether a person or another AI. Read [AGENTS.md](AGENTS.md) for the working rules and [README.md](README.md) for how the project fits together.

**This repository is public.** Internal links, credentials and working notes live in local files on the owner's Mac, listed at the end.

## Where things stand

- **Live.** Theme **2.24.8** runs on the Scroll Viewport site for the Confluence space `CRH`. Branch `main` is the live release, and each release is tagged.
- **Confluence is set up.** The Hub's own text is in its pages, the newer pages exist (Partner templates, Partner logos, Construction overview, Share your presentation) and the page tree follows the Hub's sections. Pages the Hub no longer uses were moved to the space trash with `confluence_cleanup.py`, and the Events pages went with them. These scripts were run on 21 October. Running them again is safe, because they skip pages already done.
- **Access.** Staff view the space through the staff group. If staff can open the homepage but not the pages behind it, check Space tools → Permissions → Restricted Pages, or Inspect Permissions. This happened once at launch.
- **Files.** The brand files are attached and labelled (`upload_kit.py`).
- **Canto slideshow.** Published from a 20 October snapshot (`canto_sync.py --publish`). The theme reads it straight from the Photography Media page.
- **Share your presentation.** The button opens an Airtable form on the base **Shared presentations** (SKA Communications workspace). The form's address is `SHARE_DECK_FORM` in `dev/links.json`. The review steps and reply templates are in the local `SHARE-YOUR-PRESENTATION.md`.
- **Events is hidden** (`HIDDEN_SECTIONS` in `scripts/polish.py`) until it has been reworked and reviewed. Its designs are still in the code.
- **Review board.** A Miro board holds screenshots of every page with feedback boxes, matching 2.24.5. The side-menu fixes in 2.24.6 to 2.24.8 don't show at board scale.

## Next steps

1. **Daily Canto sync.** Rotate the Canto App Secret first. Then run `canto_sync.py` from a scheduler that keeps the Canto credentials and a Confluence token as secrets.
2. **IT service desk link.** It's the only link still missing (`IT_SERVICE_DESK`). Add it to `dev/links.json`, package and upload.
3. **Approved slide decks.** Add talk decks to the About SKAO Master Deck page.
   - Use lighter copies under 100 MB, named `YYYY-MM Title.pptx` and labelled `approved`.
   - Put the details in the attachment comment: `Speaker: … · Event: …`.
   - A JPG with the same name becomes the deck's cover.
   - Talks shared through the form can come in this way once they're chosen.
4. **Events.**
   1. Restore its five pages from the Confluence trash first, so they keep the IDs in `scripts/interiors.py`.
   2. Take `'Events'` out of `HIDDEN_SECTIONS`.
   3. Upload its files (`build/kit`, `build/event-files`).
5. **Housekeeping.**
   - Empty the Confluence trash once nobody needs the old pages.
   - The older release branches can be deleted, since all their work is in `main`.
6. **Brand bank flags.**
   - The Brand Book file is called v2 but its cover says v1.2.
   - On the colour sheet, `#9B6017` has the wrong RGB values (it should be 155, 96, 23).

## Known quirks

- **Confluence's own CSS reaches the theme** on the live site. It once pushed the side-menu title down and clipped its toggle. Layout-critical spacing is pinned, so keep it that way.
- **Newer pages are found by title**, ignoring capitals, and linked through the site's page tree. If a page is renamed, update `interiors.PLANNED`.
- **The Hub starts in light mode.** People can switch with the moon button, and the Hub remembers per browser. The welcome note and the tour are remembered per browser too. `?fresh` in local test mode, or a private window on the live site, shows them again.
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
