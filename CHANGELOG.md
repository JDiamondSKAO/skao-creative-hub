# Changes

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
