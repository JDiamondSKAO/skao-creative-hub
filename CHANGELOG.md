# Changes

## 2.22.0 Events: what we've made, on request or to download (proposal, branch claude/creative-hub-v2.22)

Built on 2.21. Events no longer reads as if Communications plans people's events. It shows what already exists for SKAO events: the exhibition kit (on request) and print and giveaway files (to download), with sustainability in mind. Planning an event starts at the Comms helpdesk. Refined over several rounds of Joe's feedback, with plain, professional wording (the kit is available on request, not "borrowed").

- **Event materials** (the Events landing, was Plan event materials) has two columns, like the Hub's other landings:
  - On the left, **What's available** is a picture list in place of the section list: Exhibition kit (on request), then Banners and signage, Giveaways, Partner versions and Event logos (to download). Each row has a thumbnail, a line on what's in it and how you get it, and links straight to its place.
  - On the right is a "Planning an event?" card that opens the Comms helpdesk.
  - Below the card, **Reuse first** has four steps along a line, each with an icon and its number: Use what exists, Update a design, Choose screens over print, Make new items last.
  - Last comes **Also useful for events**: slides, posters, and photos and video.
  - On tablets the side cards sit below the list. The lead-times table, request steps and "Before you start" panels are gone.
- **Exhibition kit** (was Stands and merchandise):
  - It covers backdrops, banners, a kiosk and table cloths, available on request from the Communications team at each site.
  - The kit is a 3 × 2 grid of cards; the sixth card is "How to request it", with three steps.
  - "Care and setup" sits beside the Events Production Manual.
- **Print and giveaway files** (new; it reuses the old Merchandise and Giveaways page) is a download library like the template pages.
  - Each design is a card with its cover, a short description and its download: a print file, or a ZIP of its sizes or versions.
  - The groups are Banners and signage, Giveaways, Partner versions (with a note to check with the partner) and Event logos. Each has a clear heading and can be linked to.
  - A short "Before you print" note comes first.
  - It is built from the files on the page. To add more, such as new outreach material, upload a file labelled "approved", with a picture under the same name as its cover.
  - `scripts/event_files.py` builds today's 14 files and covers from the reusable event assets and merchandise folders (read only). One-off builds such as the IAU GA 2024 stand are left out.
- Download cards that a page names (brandkit.DOWNLOAD_GROUPS) keep the page's order. Each group has an anchor, and group notes always show.
- Landings can now:
  - put a card level with the intro (`data-landing-beside`);
  - put their own list in place of the section list (`data-landing-directory`);
  - show pictures from other pages (`data-kit-page`).
- Event safety and the event checklist now say why they've gone. Search answers "Can you help plan my event?" and "Do we have exhibition kit, banners or giveaways?".
- Fixed: on the other landings, "Before you start" sits level with the intro again, and a test guards it.

## 2.21.0 Review board feedback, round 4 (proposal, branch claude/creative-hub-v2.21)

Built on 2.20, from the notes on the review board. The Events pages wait for the next round.

- **Latest files** replaces All resources. It lists the files themselves rather than every page: each new or updated file in the Hub, newest first and grouped by month, with the page it's on, its Hub section and a download button. Search and section filters sit above the list. Several files added to one page on the same day fold into one row ("6 new files"), which opens to list them. The site teams' progress slides are included without needing a label. The footer link, a search answer and the old Hub updates pages now point here.
- **Approved slide decks** (was Decks to reuse) takes over from Recent talks, which is gone, and the "Shared by staff" group leaves Presentations. The page is now a deck library. Search by title, event or speaker, filter by topic, and sort newest, oldest or A to Z. Each deck is a wide card with:
  - its cover: a picture attached under the deck's own name (Deck.pptx and Deck.jpg), or else a drawn title slide in the brand's navy to magenta;
  - its topic, as a neutral pill with a cool-coloured dot (red, orange or green would read as a status);
  - its title, then the event, place and month on one line. A title drops the event name when that line says it anyway;
  - the details from its attachment comment in Confluence, in small capitals over a heavier value, always in the same order (Speaker, Audience, Made by, Classification). The slide count stays off the card;
  - a strip along the bottom with the format, size and when it was added or updated, then Preview (Confluence's own viewer, so nobody downloads a 3 GB deck blind) and Download.

  The reuse advice and the formatting guide follow the list. Tested with eight decks from the public talk bank.
- **Welcome and feedback:** on a first visit, a short note says the Hub is new for the Observatory and in active development, in both features and content, with Explore the Hub and Share feedback. It shows once per browser. "Beta · Share feedback" sits in the masthead on every page, and "Give feedback" in the footer. Both open the feedback form once its link is in (FEEDBACK_FORM, an Airtable form); until then they open the Comms helpdesk. The form opens with the page the person came from already filled in, so we know what the feedback is about.
- **Partner templates:** the downloads are two cards, each with a cover and a plain name (SKAO and SARAO; SRCNet), and buttons that say PowerPoint or Keynote.
- **Partner logos:** each logo is a tile with a preview (white versions on navy) and AI, EPS and PNG buttons, grouped as SRCNet logo, SRCNet avatar and Regional centres. Each regional pack is a compact card naming the centre's country.
- **Construction overview, SKA-Low and SKA-Mid:** "Status and photos" becomes "Live status", with two larger cards. On the overview these are the dashboard and the overall status; on the site pages, the site's status slides and the dashboard. The weekly all-hands photos get their own band, as on Photos and video. On the site pages, earlier slides now follow the latest deck as a dated list (a month tile, the details and a download button), showing six before a "Show all" button.
- **Video and animation** starts with the Canto slideshow. The downloads, the brand video kit and "Need new video?" are gone.
- **Poster templates:** Word and PDF only. The Illustrator files and the mention of them are gone.
- **Co-branding with CSIRO** keeps the co-branding guidelines and points to Letterheads for the office letterheads. Letterheads now names each Australian office, including Kensington, Perth (with CSIRO).
- **Link cards:** the AI policy and AI pages on Using AI image tools, the W3C reference on Accessibility checks, and the logo use request form on Using the SKAO logo (its link is now known). Each card shows what the link is and where it lives.
- **Apply the brand** drops the "Want a second opinion?" box.
- **Header:** the masthead keeps just the logo, Beta · Share feedback and the theme toggle. Search is a small icon at the start of the section row’s tools, on every page and at every width, with a tooltip that gives the shortcut (⌘K or Ctrl K; / still works). Beside it is the Canto Media Library button, with a subtle teal tint ("Canto ↗" on mid-size screens). When the masthead scrolls away, the compact bar keeps the search icon and an icon for the Canto Media Library, with small tooltips, and Feedback slides in beside them in the masthead’s gradient. On phones the search icon sits next to Menu, the Canto Media Library and Share feedback are in the menu, and the footer link uses the same name.
- **Homepage quick links** each have their own colour.
- **Canto slideshow:** up to 24 images. Photos and video shows the curated highlights first, then photos from the collections. The sync now keeps 24 highlights and up to 16 photos per collection.
- **Dropdowns** use the Hub's own chevron with room around it.
- **Google Slides:** the Standard SKAO template links to the Google Slides template gallery, for SKAO Google accounts (GOOGLE_SLIDES).
- **Test mode:** `scripts/cover_images.py` makes covers with Quick Look. Examples in `dev/brandbank-map.json` can now come from another folder (the talk bank), with labels and covers.

## 2.20.0 Construction overview (proposal, branch claude/creative-hub-progress)

Built on 2.19. The SKA-Low and SKA-Mid pages were hard to follow, so both telescopes now sit under one page, and all three are simpler.

- **New Construction overview** (Presentations › Site progress): a photo tile for each telescope, showing the month of that team's newest slides and leading to its page, then "Status and photos": the construction dashboard, the overall status and the weekly all-hands photos. It needs a Confluence page called "Construction overview" in the Creative Hub space; until then the theme matches it by that title.
- **SKA-Low progress and SKA-Mid progress** sit under it (the label above the title says Construction overview). Each opens with one navy panel: the telescope photo blended into its right side, the month of the newest deck in large type, the file details and a Download slides button. Under it, "Status and photos" is three compact cards (the site's status slides, the dashboard, the all-hands photos), then earlier decks as a plain list when there are any. Notes for the site teams are gone: they add files in Confluence.
- **Construction overview** uses the same three-card row for the dashboard, the overall status and the all-hands photos.
- **Photos:** each site page carries its telescope photo as an attachment called `site-photo.jpg`, made by `scripts/site_images.py` from the official images in the image bank. Until it's there, the tile and the panel show the navy gradient on its own.
- The Presentations list shows Construction overview only; the side menu nests SKA-Low and SKA-Mid under it. The homepage "Site progress" quick link and the search answer for construction figures open Construction overview.
- **All resources:** filters are the six Hub sections (Work with print suppliers now sits under How-to guides, and the stray "Creative services" filter is gone). Search and sort share one row the width of the list, with the filters under them. Each row shows its section and date in one aligned column, with the full summary. The page drops the extra labels and the "Updated" line.
- **Homepage quick links** stay on one row at every desktop width: the left column gets more room below 1240px, and the presentations card moves under the search below 1060px.
- **Links that leave the Hub open in a new tab** (other sites, other Confluence spaces); Hub pages and downloads open in place.

## 2.19.0 Events from the production manual (proposal, branch claude/creative-hub-events)

Built on 2.18. Three things from the Creative Production team's Events Production Manual, so the Events pages say what the team actually offers.

- **The event kit** on Stands and merchandise: the 3 m and 2 m Fabrilux backdrops, pull-up banners (85 × 200 cm), the kiosk and the table cloths, each with a picture, its size and what it's for. Ask for it through the Comms helpdesk; the Events and Logistics teams deliver it. The page's button now opens the Comms helpdesk.
- **How much notice we need** on Plan event materials: the manual's minimum lead times, from 2–3 weeks for standard print to 8–10 weeks or more for bespoke production.
- **No Event materials checklist.** The lead times and request steps cover what it asked, so it is folded into Plan event materials and its old page points to the lead times. The tick-list feature it used is gone with it.
- **How a request runs** on Plan event materials: helpdesk, a short chat, drafts with one or two rounds of changes, final approval by Communications, then production and delivery.
- **Pictures:** each kit picture is a file attached to Stands and merchandise under a fixed name (kit-fabrilux-3m.webp and so on), made by `scripts/kit_images.py` from the manual's own renders. Until a picture is there, an outline of the item shows. They are not in this repository.
- **The manual itself** is an approved download on Stands and merchandise once it is attached there.

## 2.18.0 Lighter navigation (proposal, branch claude/creative-hub-nav)

Built on 2.17 after a look at how current documentation and resource sites handle navigation. The Hub only goes Home › Section › Page, so it now says where you are once, not four times.

- **Header:** the same as 2.17 (full masthead, then the section row with the full "Search the Hub"), after trying a one-row header that read as busier.
- **Notification bar** is slimmer and in exact SKAO accent swatches: Sites #F9B34C into Science #F49E6B with text in Science #0D1D2C (dark mode: Sites #6A3F23 into Technology #5D2A2B with a gold label).
- **Get help is one page, Common questions, in the footer.** It opens with the Comms helpdesk, then short answers, then "Sharing your work" (how to share a deck, and how to share photos or video). The header has six sections. Get help and Share material show "this page has moved" notes, and Recent talks and Photos and video link straight to the right answer.
- **Homepage:** "Good work starts here." now says what is here: templates, brand files, slides and photos from across the SKAO, including the latest from both sites. Search invites a plain question, and the quick links are Logo files, Slide template, Photos, Site progress, and Colours and fonts, on one row and tinted by section. Section overviews give each group an anchor, such as presentations.html#site-progress.
- **No breadcrumb.** The section label above the title links back to the section.
- **On this page** appears only on long pages (four sections or more).
- **Previous and next** at the foot of each page on wide screens; phones, which have no sidebar, keep the "More in" list.
- **Search:** plain questions work ("where do I find the letterhead"), quick answers to the most common questions appear above the results, approved files are found by name, and / opens search.
- **Small touches:** a copy-link button on section headings, and an "Updated" date under each page title.
- **Before you start** on section overviews sits level with the intro at the top of the page, not halfway down. With several items they start closed. Overview pages drop the small label above the title, since the title is the section.

## 2.17.0 Fewer, fuller pages

The Hub goes from 51 pages to 38, and adds the three things asked for in the repository request: site progress, recent talks and the sites' weekly photos.

- **Presentations:**
  - Widescreen template is gone: every SKAO template is 16:9, so the Standard SKAO template is the widescreen one.
  - The six reusable decks become one **Decks to reuse** page that grows as files land: about the SKAO, science case, construction progress, SRCNet, local communities and specialised topics.
  - SKA-Low and SKA-Mid overviews become **SKA-Low progress** and **SKA-Mid progress**: the team's live status slides, the overall construction status, and every slide deck the team adds, newest first.
  - New **Recent talks**: staff add their own slides, shown newest first, labelled as not reviewed. "Share a deck" is folded into it.
- **Pages people keep current themselves** (Recent talks and the progress pages) list every file on the page, so adding a file in Confluence is the whole job; no "approved" label needed. Names starting with the year and month ("2026-10 …") show the month.
- **Photos and video:** the six topic pages that only pointed to Canto are folded into the landing, which keeps their search tips under "Looking for something specific?". It also gets a "Weekly all-hands photos" card.
- **Documents:** Memo and report templates are one page.
- **Events:** Stands and merchandise are one page; event safety is a short note with the HSSE link on the landing.
- **How-to guides:** Format a presentation is listed once, under Presentations.
- **Links to internal documents** stay out of this public repo: their addresses live in a local file that only the release build and local test mode read. Links still to come (Google Slides, logo request form, AI policy, all-hands albums) show as "link to follow" in the preview and are left out of the live theme until they arrive.
- **Section pages** list their groups without a page count beside each title.
- **Header:** the masthead's pause button is gone; the motion stays (and still stops for anyone who has reduced motion turned on). Once you scroll, the compact header shows the official SKAO lettermark in colour, with "Creative Hub" beside it, instead of a small grey logo.
- **Get help** is now a short note that points to the Comms helpdesk for questions and larger projects, then Common questions and Share material. The brief checklist and "what happens next" steps are gone, and the helpdesk is called the Comms helpdesk throughout, including the footer band.
- **Photos and video:** the slideshow uses Canto's large preview (2000 px instead of 640–800 px), loads each image just before it shows, and its caption band runs the full width. Weekly all-hands photos are one card with a single link to where they are stored (link to follow). The list of library collections under the slideshow is gone.
- **More in…** cards at the foot of each page no longer carry a "Next" label.
- **All resources** opens on a search box, then the type filters. In Confluence every row is dated ("Added" for the newest approved file on that page, otherwise "Updated" for the page's last edit) and the list runs newest first, so it follows on from "Just added" on the homepage. A Sort menu switches to A to Z.
- **Notification bar** uses a warm sweep from the accent palettes (Technology #F7BE00, Sites #F9B34C, Science #EF7C38) with dark text, instead of the SKAO navy and magenta. The black "New" pill becomes a quiet "New on the Hub" lead-in with a small sparkle and a hairline before the page title.
- **Side menus.** "On this page" moves to its own column on the right, away from the section menu. Both fold to a slim strip with the button at their top to give the page more room, and each viewer's choice is remembered. On narrower screens "On this page" sits in a box above the content.
- **How-to guides** read as numbered steps, each with a short description of what to do and why, instead of tick lists. The Event materials checklist keeps its ticks.
- Old addresses show a short "this page has moved" note, and search still finds them by their old names.
- The folded pages are kept as they were in `archive/removed-v2.16.html` and at the git tag `v2.16.0`.

## 2.16.0 Third round of board feedback

- **Main cards on resource pages** no longer carry "Ask for this file". Pages without files yet say "Not yet available to download". Once the approved files load, the card shows the version, the last updated date and "Approved by Communications", read from the files themselves (Brand Book keeps its edition instead of a version).
- **Intro buttons** such as "Open Noto Sans at Google Fonts", "Find logo files" and "Open the Canto library" sit under their text instead of on the far right.
- **Before you use the file** is now a card beside the downloads rather than a list below them.
- **New pages.** Partner templates (Presentations › Templates) holds the SKAO–SARAO and SRCNet templates. Partner logos (Brand › Artwork and files) holds the SRCNet network and regional centre logos. Standard SKAO template and Logos and icons now list SKAO files only, with links across. Both pages are matched by title in Confluence until their page IDs are known.
- **Standard and Widescreen templates** mention the Google Slides version; the link is to follow.
- **Letterheads** are grouped by information classification, then by site: United Kingdom (Global Headquarters, Jodrell Bank) and Australia (Geraldton offices), each with its site colour.
- **Video and animation** downloads are grouped by use: landscape and portrait logo intros, logo animations, lower thirds and framing guides.
- **Co-branding with CSIRO and SARAO** lead with "Prior approval needed", which links to Communications, and list only the co-branding guidelines and the office letterheads. Logo files for co-branded work come from Communications once a use is approved.
- **Photos and video pages** show a view-only slideshow of approved images from Canto instead of clickable tiles, with pause, previous and next controls, and the "Open the Canto library" button under it. It stays still for people who prefer reduced motion. Canto images now sync at 1280 px.
- **Using the Canto library** is one page, written for staff new to Canto (register with your SKAO email, then sign in). The duplicate "Accessing Canto" page points to it.
- **Email signatures** are removed from Documents, the menus and the homepage quick links, because IT now looks after them. The old address explains this.
- **Colours and typography** open all three accent palettes.
- **Apply the brand** ends with a "Want a second opinion?" card to reach Creative Production.
- **Using the SKAO logo** explains the logo use request form for people outside the SKAO; the link is to follow.
- **Work with print suppliers** asks Communications for trusted suppliers for your location and job.
- **Using AI image tools** starts with the SKAO AI policy; the link is to follow.
- **Deck descriptions.** Construction progress covers both sites; Specialised decks are shared by staff and approved by Communications.
- **Get help.** The helpdesk button closes the brief card. "What we can help with" is removed for now. "What happens next" has four steps: brief received, scope agreed, production, review and delivery.
- **Share material** has no helpdesk button; its intro links to the helpdesk instead.
- Search ranks titles that start with your words first.
- Removed content is kept in `archive/removed-v2.15.html`.

## 2.15.3 Second round of board feedback

- The Photos and video tile is redrawn in the family's style: two photo prints, the front one a night sky with a dish, and a small play badge for video.
- Sharing a deck is now a quiet dashed "Share a deck" row at the end of Decks to reuse on Presentations, replacing the larger card.
- Download buttons share one width, with the format and size in fixed columns, so a 20.1 MB file lines up with a 3.4 MB one.

## 2.15.2 Review board feedback

- Templates and assets is now called All resources, which is what it is: every template, guide and service in one filterable list. Its links across the Hub use the new name, and its list heading reads "Filter by type or name".
- Each resource type has one colour, shown as a dot on its filter and on its rows (slides orange, documents blue, brand pink, media teal, events purple, guides green, services slate).
- The announcement banner is a navy-to-magenta band with white text, so it is noticed.
- The Photos and video tile on the homepage is a light card like its neighbours: a photo in the brand gradient with a play button.
- Presentations has a "Help build the library" card under its advice, inviting staff to share decks through Share material.

## 2.15.1 Get help layout

- The page follows one flow: a short intro with the helpdesk button, then the brief as a single card beside what to expect.
- The brief card lists the five things to include as labelled rows (purpose, timing, output, people, inputs), with "Copy as a template" in its header and the video, print and business card extras as compact rows inside it.
- "What happens next" is a three-step timeline with the timing note and a small "Urgent?" note; "What we can help with" sits below it. Both are always visible, with no toggles.
- Common questions and Share material close the page as a pair of links. On phones everything stacks in reading order.

## 2.15.0 Get help, simplified

- Get help is one page instead of thirteen. It opens with a single button to the creative helpdesk, then "What to include" (with a "Copy as a template" button for the helpdesk form) and "Asking for something specific?" for video, print and business cards. A "Good to know" panel beside it covers what happens next and what the team can help with, each said once.
- Common questions absorbs Help with the Hub (seven questions, no repeats) and Share material is three plain routes with one helpdesk button.
- Replaced pages keep their addresses and point to the part of Get help that now holds them, which opens on arrival. Search still finds them by their old names. Work with print suppliers moves to How-to guides › Print and posters.
- Hub updates and Updates archive leave the menus and footer; the announcement banner and Just added cover what's new.
- Generic "ask the team" boxes that only repeated the footer are gone.
- The footer band has one call to action, straight to the helpdesk, and speaks to bigger work: "Planning something bigger? Most everyday work can start right here in the Hub. For campaigns, flagship events or new publications, bring Creative Production in early so we can shape it with you."
- The previous text of all thirteen pages is kept in `archive/get-help-v2.14.html`, and the whole Hub before this change is at the git tag `pre-get-help-simplify`.

## 2.14.0 Header, section menus and motion

- Header, refined rather than redesigned: the pause and theme controls are a matching pair of round buttons (the pause control has real pause and play icons), and the "Resources for staff" label is gone. The current section no longer shifts its neighbours when it turns bold.
- One underline slides to the section under the pointer or keyboard focus and settles back on the current one, which keeps a faint mark meanwhile.
- Once the brand bar scrolls away, a small SKAO logo leads the pinned bar back home. Below 1,200 px the search box shortens to its icon and shortcut, so nothing overflows.
- The phone menu icon turns into a close mark and the menu slides open.
- The announcement is quieter: a soft tint, an underline that draws in on hover, and it slides open and closed.
- Section menus hide nothing: a plain section heading, an "Overview" link to the landing page, then every page under small uppercase group labels. Small capitals now only ever mean a label.
- Status dots, the "On request" key, the status pill and the "Need a file marked on request?" box are removed; the footer's "Need new work or a review?" band is the route for help. Resource pages keep "How to get it" until their files are uploaded.
- "Before you start" items are tinted by kind, with no icons: guidance (slate), checks (sage, with sage step numbers or ticks), and ask-the-team prompts (ochre). The colours are muted and never share the heading's magenta. The open item takes a faint tint of its colour, keyboard focus sits inside the row, and loose "A · B" links become small buttons.
- The "Before you start" heading leads the panel: the masthead gradient along its top edge, a magenta label on a soft tint, a gentle lift off the page, and a one-time slide-in after the page loads.
- "Just added" lists pages, not raw file names: the page people recognise ("Logos and icons"), then the file or "3 new files" and a short date ("Today", "3 days ago", "17 Apr"). Each row opens that page's Downloads section rather than starting a download. A softly pulsing dot marks it as live, rows fade in one after another, and "See all" is a small button.
- File badges have one colour per kind: ZIP amber (no longer a greyed-out look), artwork purple, video teal, images green, alongside the existing slides, PDF and document colours.
- Motion: one set of timings for every hover; link underlines fill in on hover; arrows travel a few pixels toward where the link goes; buttons lift and press; focus rings snap in; accordions fade as they open; search rises in; Canto images zoom more slowly. In Chrome and Safari, moving between Hub pages fades the new page in while the header holds still. All of it stops with reduced-motion settings.
- Stylesheet and script URLs carry a hash of their contents, so a browser can't pair new pages with an old cached stylesheet.
- `scripts/package.py` now also builds the flat upload for the space theme editor (via `staging_files.py`) and checks its paths. The flat zips handed over for 2.12.1 to 2.13.0 were flattened by hand with folder paths left in `page.vm`; use this one instead.

## 2.13.0 SKAO Staff portal

- Canto tiles, album links and every general Canto link now open the private SKAO Staff portal, which shows only the Staff media library to staff signed in as Consumers. Closing an asset returns to its album in the portal.
- The gallery note tells first-time visitors to choose Register Now and use their SKAO email address.
- `CANTO_PORTAL` defaults to `SKAOStaff`; set it to `library` for main-library links.

## 2.12.2 Canto assets open in their album

- Tiles open the asset over its own album (`/album/{album}?column=image&id={asset}`), so closing it returns to that album rather than to every image in Canto.

## 2.12.1 Canto links open the staff library

- Tiles open the asset in the Canto library (`/smartalbum/image?column=image&id={asset}`, the format canto-metadata-assistant uses), and collection links open their album or folder. 2.12.0 linked to the SKAO Library portal, which doesn't include the staff folder, so Canto said the album "cannot be accessed" and offered to remove the file's record.
- "Open in Canto" on Photos and video, and "Open album in Canto" on topic pages, open the staff folder when a strip spans several albums.
- `CANTO_PORTAL` switches every link to a portal instead (for example a staff portal), for staff without a Canto login.

## 2.12.0 curated Canto showcase

- Tiles open the asset's own view in the SKAO Library portal (`/v/SKAOLibrary/album/{album}?column=image&id={asset}`), found by testing the portal; collection links open their folder.
- The sync curates instead of taking the newest: approved, credited, at least 2,000 px, never uncleared wording (heritage review, pending, embargo, draft…), scored on description, tags, shape, resolution, recency and subject. Per-album caps, one per numbered frame sequence, one per title, and identical files and visually near-identical images removed.
- Highlights is its own pick: images without people, a subject mix (at most 1 composite, 2 night skies, 3 aerials, 2 artist impressions), shown in full rows.
- Titles fall back to the description where Canto's name is a file name; descriptions become alt text, and tag-list descriptions are ignored. People-focused descriptions count as people when the People keyword is missing.
- Editors can pin assets by tagging them "Hub feature" in Canto.

## 2.11.1 Canto sync tested against SKAO's Canto

- Client credentials use `https://oauth.canto.global/oauth/api/oauth2/token` with `app_id` and `app_secret` and read the camelCase reply (`accessToken`, `expiresIn`). App ID and Secret are preferred over a generated token because they renew themselves.
- Albums are listed with `/search?scheme=album` (paged; counts from `size`), because `/api/v1/album` returns the web app on this tenant.
- The 43 albums under Staff media library are grouped into collections by path (SKA-Low, SKA-Mid, Hero shots, Artist impressions and animations, Events 2026, Events 2025, Booth videos, Promo videos). Preferred collections come first (`CANTO_ORDER`), the rest by newest asset, and collections with fewer than 3 images or videos are left out (`CANTO_MIN_ASSETS`).
- Videos appear with their poster frame and a Video badge. Explainer animations and Video and animation get strips too.
- The gallery opens on Highlights: photos from the image collections without repeats; events and videos keep their own tabs.
- HTTPS verification uses certifi when Python has no certificate bundle (python.org builds on macOS). `--env FILE` reads settings from a local file.

## 2.11.0 Canto showcase

- Photos and video leads with a gallery of approved images from the Canto Staff media library folder, with album tabs, titles and credits. Tiles open the asset in Canto.
- Telescope imagery, Hero images and Event photography show a strip from the matching album, linking to the album in Canto.
- `scripts/canto_sync.py` publishes 640 px previews (metadata stripped) and `canto-showcase.json` as attachments on one Hub page, so browsers never need a Canto token or an expiring Canto link. Adapted from canto-metadata-assistant's client: bearer token or OAuth client credentials, album namePath, directUrlPreview, retry with backoff. The Canto token is never forwarded to the CDN on redirect.
- The theme only shows images served from Hub attachments and links that go to canto.global, and stays hidden when there is no manifest or no matching album.
- Local test mode builds stand-in albums with the sync's own code.

## 2.10.2 downloads as choices

- Downloads move out of the resource panel into their own section under it, so the panel stays compact and its artwork no longer stretches.
- Files are grouped by the choice people are making: by information classification (Unrestricted to Strictly Confidential, with the proper labels), by office and layout, then by file type, with partner versions last.
- One row per version with a button per format (for example A0 → DOCX, PDF, AI). Labels drop words every file in the group shares, so rows read "Confidential", "Bradford Office" or "ukSRC". Each button states the format and size.
- Once files are listed, the panel's version chips and "How to get it" row give way to them, and "When you receive the file" reads "Before you use the file".

## 2.10.1 local test mode and fixes found with real files

- Local test mode (`scripts/dev_server.py`) simulates Confluence so downloads, Just added, the announcement banner and search can be tested with real brand-bank files.
- Any Hub page with approved attachments shows a Downloads section, not only resource pages.
- Just added shows at most three files; file names drop underscores but keep hyphens.
- Search puts title matches first whatever order Confluence returns, and shows Hub page titles rather than Confluence page names.
- Header flicker fixed: the sticky header no longer uses a blur filter, and the decorative lens runs on its own layer and pauses while the bar is scrolled away.

## 2.10.0 brand bank details and live downloads

Content checked against the SKAO brand bank (September 2026). No files are published from this repository.

- Resource pages list what the pack contains. The Standard SKAO template comes in six versions, one per information classification label, all 16:9, plus SKAO–SARAO and SRCNet versions. Also covered: letterheads (office, landscape, classification and SKAO–CSIRO versions), email signatures (full-colour and white logo), posters (A0, A1 and A2 in Illustrator, Word and PDF), logos (lettermark and pictorial mark, colourways, formats, co-brand and SRCNet regional centre logos) and the Brand Book (March 2022).
- The Widescreen template page explains that it is the same 16:9 layout as the Standard template.
- Colours: CMYK and Pantone join hex and RGB for Blueshift Navy (2745 C) and Redshift Magenta (213 C), and the Science, Technology and Sites accent palettes are copyable swatches.
- Logo guidance adds the minimum sizes (20 mm in print, 50 px on screen) and when to use the single-colour logo. Fonts adds which Noto Sans weight to use. Co-branding pages describe the partner packs. Video and Merchandise list the existing kits and designs.
- Files attached to a Hub page and labelled `approved` now appear as downloads on that page, clear its "On request" marker on landing pages and in Templates and assets, and show in Just added. Only same-site links are used.
- References to "Brand Book v2" are replaced with "March 2022".

## 2.9.0 homepage polish and a proper footer

- The Presentations feature card is back in the hero.
- Latest approved files move to a slim "Just added" strip under the hero: three files in one line with type, name, date and "See all". It stays hidden when there is nothing new (no auto-rotating carousel; see NN/g research on auto-forwarding carousels).
- Footer rebuilt: a navy help band ("Need new work or a review?" with Request creative help and Report a problem), then a brand bar with the SKAO logo and five links. It holds together at every width.
- "Request help" leaves the quick links because the footer band covers it; five quick links fit on one row.

## 2.8.0 leaner homepage

- The hero pairs search and quick links with the newest approved files, which replace the Presentations promo card. What changes most now sits where people look first.
- One search on the homepage: the header search button is hidden there (Cmd/Ctrl K still works).
- "Browse the Hub" is a compact index: small thumbnail, section name and what it contains. It replaces the six large picture tiles, and the "01 / 02 / 03" numbering is gone.
- The "Need a hand?" band is removed; the footer's help row on every page carries its wording ("Need new work or a review?") and the request button. "Request help" joins the quick links.
- Announcement banner text is centred, with the close button at the right edge.
- Unused homepage styles removed (about 6 KB).

## 2.7.0 progressive disclosure, announcements, footer

- Section landing pages put the page list on the left and a sticky help panel on the right: an "Ask for a file" action when items are on request, then the section's advice as one-line headings that open on demand (first one open). On phones the panel follows the list.
- "On request" is a one-line legend above the list; group labels show their page count.
- Detail-page sidebars open only the group that holds the current page; other groups show their count and open on click.
- Pages with three or more questions (Common questions, Help) get an "Expand all" control. All question blocks share one hairline accordion style, and open smoothly where supported (no motion with reduced-motion settings).
- Announcement banner returns under the header on every page. It shows the newest CRH page labelled `announcement` and links to it; editors control it from Confluence. Dismissal is remembered per page version, so an updated announcement shows again. The preview shows a marked example.
- Footer in two tiers: identity with a "Can't find what you need?" request action, then a quiet bar of five secondary links.

## 2.6.0 landing pages as lists

- Section landing pages list their pages as grouped rows (group label on the left, title and one-line summary on the right) instead of equal-weight cards, so they scan top to bottom and odd counts leave no gaps.
- "On request" is explained once in a short note; rows carry a small dot, with the words kept for screen readers.
- Supporting advice (release checks, useful checks, reuse guidance, contacts) sits under the list as light columns instead of stacked boxes.
- Templates and assets is a filterable list with title, type and status columns, alphabetical within each type.
- Unused card styles removed.

## 2.5.0 lighter navigation

Same seven sections and groups, with each list shown once. Typical pages drop from 91–109 links to 26–32.

- Top menu: seven plain links to the section landing pages, with the current section underlined. The drop-down panels are gone; each landing page lists its whole section, so every page is within two clicks.
- Section landing pages and Templates and assets are full width with no sidebar, because they are the list. Detail pages keep the grouped section sidebar.
- Homepage section tiles are single links; "Quick links" (renamed from "Jump to") covers the most common tasks. The latest-assets band no longer repeats the catalogue link.
- Templates and assets drops its four starting-point cards; the type filters do the same job.
- Footer: six links in one row. Search quick links match the homepage quick links.
- Labels are consistent: "Templates and assets" everywhere; the catalogue heading is "All resources".

## 2.4.0 one structure everywhere

- One information architecture drives the top menu, sidebars, breadcrumbs, landing pages and homepage: Presentations, Documents, Brand, Photos and video, Events, How-to guides, Get help, each split into named groups (for example Templates / Decks to reuse / How to).
- The top menu is those sections. Each opens a panel listing every page in its groups, so any page is one click from anywhere. Keyboard accessible (Escape closes, one panel at a time); on phones the panels expand inline.
- Sidebars show the section's groups with group headings; the landing page is named rather than "Overview". "Other sections" is gone because the top menu covers it.
- Section landing pages show their whole section as a grouped directory with summaries and "On request" status, instead of three cards and collapsed extras. Short advice that was hidden in accordions is now visible.
- Homepage "Browse by section" tiles each carry three direct links.
- Confluence breadcrumbs follow the Hub sections for known pages. Card numbering removed; focus outline on the main area removed.

## 2.3.0 page journeys and latest assets

- Homepage "03 / Just added" band lists the newest Confluence attachments labelled `approved` in the CRH space. If none are labelled yet, it shows recent deliverable files (slides, documents, PDFs, artwork, video; never page images) and says so. Links stay on the Confluence origin; uploader names are not shown. The preview shows marked examples only.
- Every section (Presentations, Documents, Brand, Photos and video, Events, How-to guides, Creative services, Help) has its own sidebar listing its pages, with other sections tucked away. Breadcrumbs include the section in the preview.
- Every page ends with "More in {section}": the next page and two more, with summaries. Section landing pages without cards list their whole section.
- The 15 template and file pages open with a resource panel: purpose, status, how to get it, and a link to the relevant guidance.
- Event checklist, print preparation, poster and accessibility pages are tick-off checklists with progress, clear and print. Ticks stay in the viewer's browser.
- Request help starts with two routes: submit an existing brief, or write one with the helper.
- Media pages' Canto hand-off panel is styled. Print styles hide navigation.

## 2.2.0 visual and layout pass

- Homepage leads with a search box; typing hands straight over to the full search.
- Navigation stays pinned while scrolling, with the search button always in reach. The masthead is more compact.
- Interior pages open with a title band (breadcrumbs, section, title) and a sticky sidebar so "On this page" stays visible.
- "File not available" panels are now a one-line "Available on request" notice, so guidance comes first.
- Templates and assets gains "Everything in the Hub": every resource as a card, filterable by type and name, with on-request items marked.
- Grouped footer: Find, Get help, Contribute.
- Cards lift on hover; spacing, shadows and dark mode refined throughout.

## 2.1.0 finding things faster

- Search ranks page titles above summaries and body text, matches every word, and understands common alternatives (PowerPoint/deck/slides, color/colour, photo/image, logo/artwork and others).
- Search results show the section and a real summary or matching snippet, with the matched words highlighted. Page markup is no longer searchable.
- ↑/↓ moves through results; Enter opens the top result once results are shown.
- The search dialog opens with quick links and the last few pages viewed in this browser.
- In Confluence, page titles from the Hub tree match instantly while full-text results load, and the full-text query includes the same alternatives.
- Homepage "Jump to" links for logo files, the slide template, colours, fonts and email signatures.
- Brand colour values copy with one click (hex and RGB), with a keyboard fallback where clipboard access is blocked.
- "On this page" highlights the section in view; resource pages link back to their named collection.
- The shortcut hint shows ⌘K or Ctrl K for the device. The Document templates tile stays inside the Hub.

## 2.0.0 staging redesign

- Reworked homepage with featured presentation card and clear resource choices.
- Added branded masthead, continuous decorative lens with pause/reduced-motion support, and light/dark themes.
- Simplified search, footer and request entry points.
- Reviewed all 60 interior routes with task-focused layouts, optional guidance and explicit file availability.
- Separated media browsing, contribution and presentation sharing.
- Added static previews, template build tools and 15 automated checks.

This commit records the accumulated redesign as one baseline. Earlier editing sessions were not committed individually.
