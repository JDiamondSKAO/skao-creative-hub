# Changes

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
