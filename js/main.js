/* ============================================= */
/* SKAO Creative Production Hub                  */
/* Scroll Viewport Theme — main.js v1.0          */
/* ============================================= */

document.addEventListener('DOMContentLoaded', function () {

    /* -----------------------------------------
     * DARK MODE TOGGLE
     * View Transitions API circular reveal animation
     * with fallback overlay approach
     * ----------------------------------------- */
    var themeToggle = document.getElementById('themeToggle');
    var themeAnimating = false;

    function applyTheme(newDark) {
        if (newDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        try { localStorage.setItem('crh-theme', newDark ? 'dark' : 'light'); } catch (e) {}
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            if (themeAnimating) return;

            var btn = themeToggle;
            var rect = btn.getBoundingClientRect();
            var x = rect.left + rect.width / 2;
            var y = rect.top + rect.height / 2;
            var endRadius = Math.hypot(
                Math.max(x, window.innerWidth - x),
                Math.max(y, window.innerHeight - y)
            );
            var newDark = !document.documentElement.classList.contains('dark');

            themeAnimating = true;

            /* Modern path: View Transitions API */
            if ('startViewTransition' in document) {
                var transition = document.startViewTransition(function () {
                    applyTheme(newDark);
                });
                transition.ready.then(function () {
                    document.documentElement.animate(
                        { clipPath: [
                            'circle(0px at ' + x + 'px ' + y + 'px)',
                            'circle(' + endRadius + 'px at ' + x + 'px ' + y + 'px)'
                        ]},
                        { duration: 400,
                          easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
                          pseudoElement: '::view-transition-new(root)' }
                    );
                });
                transition.finished.then(function () { themeAnimating = false; });
            } else {
                /* Fallback: clip-path overlay */
                var overlay = document.createElement('div');
                overlay.style.cssText =
                    'position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;' +
                    'pointer-events:none;will-change:clip-path;' +
                    'background:' + (newDark ? '#0c0f1a' : '#ffffff') + ';' +
                    'clip-path:circle(0px at ' + x + 'px ' + y + 'px);';
                document.body.appendChild(overlay);

                requestAnimationFrame(function () {
                    overlay.style.transition = 'clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                    overlay.style.clipPath = 'circle(' + (endRadius * 1.5) + 'px at ' + x + 'px ' + y + 'px)';
                });

                /* Apply theme mid-animation */
                setTimeout(function () { applyTheme(newDark); }, 150);

                /* Clean up */
                setTimeout(function () {
                    overlay.remove();
                    themeAnimating = false;
                }, 420);
            }
        });
    }

    /* -----------------------------------------
     * ANNOUNCEMENT BANNER DISMISS
     * Manages banner visibility via localStorage
     * ----------------------------------------- */
    var announceBanner = document.getElementById('announcementBanner');
    var announceClose = document.getElementById('announcementClose');

    function checkAnnouncementBannerState() {
        try {
            var isDismissed = localStorage.getItem('crh-banner-announce-v1') === '1';
            if (isDismissed && announceBanner) {
                announceBanner.style.display = 'none';
            } else if (announceBanner) {
                announceBanner.style.display = 'block';
            }
        } catch (e) {
            /* localStorage not available — show banner */
            if (announceBanner) announceBanner.style.display = 'block';
        }
    }

    if (announceClose) {
        announceClose.addEventListener('click', function (e) {
            e.preventDefault();
            if (announceBanner) announceBanner.style.display = 'none';
            try { localStorage.setItem('crh-banner-announce-v1', '1'); } catch (e) {}
        });
    }

    /* Initialize banner state on load */
    checkAnnouncementBannerState();

    /* -----------------------------------------
     * HERO SECTION
     * Hero search trigger button
     * ----------------------------------------- */
    var heroSearchTrigger = document.getElementById('heroSearchTrigger');
    if (heroSearchTrigger) {
        heroSearchTrigger.addEventListener('click', openSearchModal);
    }

    /* -----------------------------------------
     * BACK TO TOP BUTTON
     * ----------------------------------------- */
    var backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 400) {
                backToTop.classList.add('crh-btt-visible');
            } else {
                backToTop.classList.remove('crh-btt-visible');
            }
        });

        backToTop.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /* -----------------------------------------
     * SMOOTH SCROLL FOR ANCHOR LINKS
     * ----------------------------------------- */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;
            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /* -----------------------------------------
     * SEARCH MODAL
     * Full implementation with Confluence CQL REST API
     * ----------------------------------------- */
    var searchModal = document.getElementById('searchModal');
    var searchModalInput = document.getElementById('searchInput');
    var searchModalClose = document.getElementById('closeSearchModal');
    var searchModalBackdrop = document.getElementById('searchBackdrop');
    var openSearchBtn = document.getElementById('openSearchModal');
    var openSearchBtnMobile = document.getElementById('openSearchModalMobile');

    function openSearchModal() {
        if (searchModal) {
            searchModal.style.display = '';
            searchModal.classList.add('crh-search-modal-open');
            document.body.style.overflow = 'hidden';
            if (searchModalInput) {
                setTimeout(function () { searchModalInput.focus(); }, 100);
            }
        }
    }

    function closeSearchModal() {
        if (searchModal) {
            searchModal.classList.remove('crh-search-modal-open');
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
            /* Reset search state */
            if (searchModalInput) searchModalInput.value = '';
            var resultsEl = document.getElementById('searchResults');
            if (resultsEl) { resultsEl.innerHTML = ''; resultsEl.classList.remove('crh-search-results-show'); }
        }
    }

    if (openSearchBtn) openSearchBtn.addEventListener('click', openSearchModal);
    if (openSearchBtnMobile) openSearchBtnMobile.addEventListener('click', openSearchModal);
    if (searchModalClose) searchModalClose.addEventListener('click', closeSearchModal);
    if (searchModalBackdrop) searchModalBackdrop.addEventListener('click', closeSearchModal);

    /* Keyboard shortcut: Ctrl/Cmd+K to open search, Esc to close */
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchModal && searchModal.style.display !== 'none') {
                closeSearchModal();
            } else {
                openSearchModal();
            }
        }
        if (e.key === 'Escape' && searchModal && searchModal.style.display !== 'none') {
            closeSearchModal();
        }
    });

    /* -----------------------------------------
     * LIVE SEARCH via Confluence REST API
     * Searches within the Creative Hub space
     * ----------------------------------------- */
    var searchTimer = null;
    var searchResults = document.getElementById('searchResults');
    var activeResultIndex = -1;

    function showSearchState(state) {
        if (searchResults) {
            if (state === 'empty') {
                searchResults.innerHTML = '<div class="crh-search-empty"><p>Start typing to search</p></div>';
            } else if (state === 'loading') {
                searchResults.innerHTML = '<div class="crh-search-loading"><p>Searching...</p></div>';
            } else if (state === 'noResults') {
                searchResults.innerHTML = '<div class="crh-search-no-results"><p>No results found</p></div>';
            }
            /* 'results' state is handled by renderResults() */
            searchResults.classList.add('crh-search-results-show');
        }
        activeResultIndex = -1;
    }

    function highlightMatch(text, query) {
        if (!query) return text;
        var escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp('(' + escaped + ')', 'gi'), '<mark>$1</mark>');
    }

    function extractExcerpt(body, query, maxLen) {
        maxLen = maxLen || 160;
        if (!body) return '';
        /* Strip HTML tags */
        var text = body.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
        if (!query) return text.substring(0, maxLen) + (text.length > maxLen ? '...' : '');
        /* Find the query in the text and show surrounding context */
        var idx = text.toLowerCase().indexOf(query.toLowerCase());
        if (idx === -1) return text.substring(0, maxLen) + (text.length > maxLen ? '...' : '');
        var start = Math.max(0, idx - 60);
        var end = Math.min(text.length, idx + query.length + 100);
        var excerpt = (start > 0 ? '...' : '') + text.substring(start, end) + (end < text.length ? '...' : '');
        return highlightMatch(excerpt, query);
    }

    function buildResultLink(result) {
        /* Scroll Viewport rewrites URLs, so use _links.webui or build from content ID */
        if (result._links && result._links.webui) {
            return contextPath + result._links.webui;
        }
        return contextPath + '/wiki/spaces/' + (result.space ? result.space.key : spaceKey) + '/pages/' + result.id;
    }

    function performSearch(query) {
        if (!query || query.length < 2) {
            showSearchState('empty');
            return;
        }

        showSearchState('loading');

        /* Use Confluence CQL search — search within the Creative Hub space */
        var cql = 'type=page AND space="' + spaceKey + '" AND (title~"' + query + '" OR text~"' + query + '")';
        var url = contextPath + '/rest/api/content/search?cql=' + encodeURIComponent(cql) + '&limit=10&expand=body.view,space,ancestors';

        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('X-Atlassian-Token', 'nocheck');

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    renderResults(data.results || [], query);
                } catch (e) {
                    /* If JSON parse fails, try the simple search fallback */
                    performSimpleSearch(query);
                }
            } else if (xhr.status === 403 || xhr.status === 401) {
                /* Auth issue — fall back to simple search page */
                performSimpleSearch(query);
            } else {
                showSearchState('noResults');
            }
        };

        xhr.onerror = function () {
            performSimpleSearch(query);
        };

        xhr.send();
    }

    function performSimpleSearch(query) {
        /* Fallback: use Confluence's older search API which may have looser auth */
        var url = contextPath + '/rest/api/content?spaceKey=' + spaceKey + '&title=' + encodeURIComponent(query) + '&limit=10&expand=body.view,space,ancestors';

        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.setRequestHeader('Accept', 'application/json');

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    renderResults(data.results || [], query);
                } catch (e) {
                    showSearchState('noResults');
                }
            } else {
                showSearchState('noResults');
            }
        };

        xhr.onerror = function () {
            showSearchState('noResults');
        };

        xhr.send();
    }

    function renderResults(results, query) {
        if (!searchResults) return;

        if (results.length === 0) {
            showSearchState('noResults');
            return;
        }

        var html = '';
        for (var i = 0; i < results.length; i++) {
            var r = results[i];
            var title = highlightMatch(r.title || 'Untitled', query);
            var bodyHtml = (r.body && r.body.view) ? r.body.view.value : '';
            var excerpt = extractExcerpt(bodyHtml, query);
            var link = buildResultLink(r);

            /* Build breadcrumb from ancestors */
            var breadcrumb = '';
            if (r.ancestors && r.ancestors.length > 0) {
                var crumbs = [];
                for (var a = 0; a < r.ancestors.length; a++) {
                    crumbs.push(r.ancestors[a].title);
                }
                breadcrumb = crumbs.join(' › ');
            }

            html += '<a href="' + link + '" class="crh-search-result" data-index="' + i + '">';
            html += '  <div class="crh-search-result-icon">';
            html += '    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>';
            html += '  </div>';
            html += '  <div class="crh-search-result-body">';
            if (breadcrumb) {
                html += '    <span class="crh-search-result-breadcrumb">' + breadcrumb + '</span>';
            }
            html += '    <span class="crh-search-result-title">' + title + '</span>';
            if (excerpt) {
                html += '    <span class="crh-search-result-excerpt">' + excerpt + '</span>';
            }
            html += '  </div>';
            html += '  <div class="crh-search-result-arrow">';
            html += '    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>';
            html += '  </div>';
            html += '</a>';
        }

        searchResults.innerHTML = html;
        showSearchState('results');
    }

    /* Keyboard navigation within results */
    if (searchModalInput) {
        searchModalInput.addEventListener('input', function () {
            var query = this.value.trim();
            clearTimeout(searchTimer);
            searchTimer = setTimeout(function () {
                performSearch(query);
            }, 300);
        });

        searchModalInput.addEventListener('keydown', function (e) {
            if (!searchResults) return;
            var items = searchResults.querySelectorAll('.crh-search-result');
            if (items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                activeResultIndex = Math.min(activeResultIndex + 1, items.length - 1);
                updateActiveResult(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                activeResultIndex = Math.max(activeResultIndex - 1, -1);
                updateActiveResult(items);
            } else if (e.key === 'Enter' && activeResultIndex >= 0) {
                e.preventDefault();
                items[activeResultIndex].click();
            }
        });
    }

    function updateActiveResult(items) {
        for (var i = 0; i < items.length; i++) {
            items[i].classList.toggle('crh-search-result-active', i === activeResultIndex);
        }
        if (activeResultIndex >= 0 && items[activeResultIndex]) {
            items[activeResultIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    /* -----------------------------------------
     * SIDEBAR NAVIGATION & TOGGLE
     * Mobile/desktop sidebar panel management
     * ----------------------------------------- */
    var sidebarPanel = document.getElementById('sidebarPanel');
    var sidebarToggle = document.getElementById('sidebarToggle');
    var sidebarClose = document.getElementById('sidebarClose');

    function openSidebar() {
        if (sidebarPanel) sidebarPanel.classList.add('crh-sidebar-open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebarPanel) sidebarPanel.classList.remove('crh-sidebar-open');
        document.body.style.overflow = '';
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);

    /* Close sidebar on escape key */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebarPanel && sidebarPanel.classList.contains('crh-sidebar-open')) {
            closeSidebar();
        }
    });

    /* -----------------------------------------
     * MOBILE MENU TOGGLE
     * ----------------------------------------- */
    var mobileMenuBtn = document.getElementById('mobileMenuBtn');
    var headerNav = document.getElementById('headerNav');

    if (mobileMenuBtn && headerNav) {
        mobileMenuBtn.addEventListener('click', function () {
            headerNav.classList.toggle('crh-header-nav-open');
        });
    }

    /* -----------------------------------------
     * "MORE" NAV DROPDOWN TOGGLE
     * ----------------------------------------- */
    var navMore = document.getElementById('navMore');
    var navMoreBtn = document.getElementById('navMoreBtn');

    if (navMore && navMoreBtn) {
        navMoreBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            var isOpen = navMore.classList.toggle('crh-nav-more-open');
            navMoreBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        /* Close on outside click */
        document.addEventListener('click', function (e) {
            if (!navMore.contains(e.target)) {
                navMore.classList.remove('crh-nav-more-open');
                navMoreBtn.setAttribute('aria-expanded', 'false');
            }
        });

        /* Close on Escape */
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && navMore.classList.contains('crh-nav-more-open')) {
                navMore.classList.remove('crh-nav-more-open');
                navMoreBtn.setAttribute('aria-expanded', 'false');
                navMoreBtn.focus();
            }
        });
    }

    /* -----------------------------------------
     * ARTICLE DATE FORMATTING
     * Reads the raw Confluence date from data-raw-date
     * and renders a human-friendly "Last updated: DD Mon YYYY"
     * ----------------------------------------- */
    var dateMeta = document.querySelector('.crh-article-date[data-raw-date]');
    if (dateMeta) {
        var rawDate = dateMeta.getAttribute('data-raw-date');
        var dateText = dateMeta.querySelector('.crh-article-date-text');
        if (rawDate && dateText) {
            try {
                var d = new Date(rawDate);
                if (!isNaN(d.getTime())) {
                    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                    var formatted = d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
                    dateText.textContent = 'Last updated: ' + formatted;
                }
            } catch (e) {
                /* Fallback: leave as "Last updated" */
            }
        }
    }

    /* -----------------------------------------
     * AUTO-GENERATED TABLE OF CONTENTS
     * Scans .crh-content-body for h2/h3 headings
     * Provides sidebar navigation with scroll-spy
     * ----------------------------------------- */
    var contentBody = document.querySelector('.crh-content .crh-content-body');
    var sidebarInner = document.querySelector('.crh-sidebar .crh-sidebar-inner');

    /* Skip TOC on section pages (pages with child listings) — sidebar already has nav */
    var isSectionPage = document.querySelector('.crh-child-pages');

    if (contentBody && sidebarInner && !isSectionPage) {
        var headings = contentBody.querySelectorAll('h2, h3');
        if (headings.length >= 3) {
            /* Show sidebar (it may be empty on leaf pages) */
            sidebarInner.parentElement.style.display = '';
            /* Build TOC with collapse toggle */
            var tocHtml = '<div class="crh-sidebar-toc-header">'
                + '<h4 class="crh-sidebar-title crh-sidebar-toc-title">On this page</h4>'
                + '<button class="crh-sidebar-collapse-btn" id="sidebarCollapseBtn" aria-label="Collapse sidebar" title="Collapse sidebar">'
                + '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>'
                + '</button>'
                + '</div>'
                + '<ul class="crh-sidebar-toc">';
            for (var h = 0; h < headings.length; h++) {
                var heading = headings[h];
                /* Ensure each heading has an ID */
                if (!heading.id) {
                    heading.id = 'toc-' + heading.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
                }
                var indent = heading.tagName === 'H3' ? ' crh-sidebar-toc-h3' : '';
                tocHtml += '<li class="crh-sidebar-toc-item' + indent + '"><a href="#' + heading.id + '" class="crh-sidebar-toc-link">' + heading.textContent.trim() + '</a></li>';
            }
            tocHtml += '</ul>';

            /* Insert TOC before existing sidebar nav */
            var tocContainer = document.createElement('div');
            tocContainer.className = 'crh-sidebar-toc-wrap';
            tocContainer.innerHTML = tocHtml;
            sidebarInner.insertBefore(tocContainer, sidebarInner.firstChild);

            /* Sidebar collapse/expand */
            var sidebarEl = sidebarInner.parentElement;
            var layoutEl = document.querySelector('.crh-layout');
            var collapseBtn = document.getElementById('sidebarCollapseBtn');
            var sidebarCollapsed = false;

            /* Create an expand button that sits outside sidebar-inner (visible when collapsed) */
            var expandBtn = document.createElement('button');
            expandBtn.className = 'crh-sidebar-expand-btn';
            expandBtn.setAttribute('aria-label', 'Show sidebar');
            expandBtn.setAttribute('title', 'Show sidebar');
            expandBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>';
            sidebarEl.appendChild(expandBtn);

            /* Check localStorage for saved state */
            try {
                sidebarCollapsed = localStorage.getItem('crh-sidebar-collapsed') === '1';
            } catch (e) {}

            function applySidebarState() {
                if (sidebarCollapsed) {
                    sidebarEl.classList.add('crh-sidebar-collapsed');
                    if (layoutEl) layoutEl.classList.add('crh-sidebar-hidden');
                } else {
                    sidebarEl.classList.remove('crh-sidebar-collapsed');
                    if (layoutEl) layoutEl.classList.remove('crh-sidebar-hidden');
                }
            }

            applySidebarState();

            collapseBtn.addEventListener('click', function () {
                sidebarCollapsed = true;
                try { localStorage.setItem('crh-sidebar-collapsed', '1'); } catch (e) {}
                applySidebarState();
            });

            expandBtn.addEventListener('click', function () {
                sidebarCollapsed = false;
                try { localStorage.setItem('crh-sidebar-collapsed', '0'); } catch (e) {}
                applySidebarState();
            });

            /* Scroll-spy: highlight active heading on scroll.
             * Strategy: on every scroll tick, find the last heading whose top
             * edge is at or above a "trigger line" (120px from viewport top).
             * This avoids IntersectionObserver edge-cases where the clicked
             * heading sits above the observer zone and the next one wins. */
            var tocLinks = tocContainer.querySelectorAll('.crh-sidebar-toc-link');
            var spyTicking = false;
            var TRIGGER_LINE = 120; /* px from viewport top */

            function updateTocHighlight() {
                var activeId = null;

                /* Walk backwards: first heading whose top <= TRIGGER_LINE wins */
                for (var hi = headings.length - 1; hi >= 0; hi--) {
                    if (headings[hi].getBoundingClientRect().top <= TRIGGER_LINE) {
                        activeId = headings[hi].id;
                        break;
                    }
                }

                /* Edge-case: user at very top, no heading above trigger line yet */
                if (!activeId && headings.length) {
                    activeId = headings[0].id;
                }

                tocLinks.forEach(function (l) { l.classList.remove('crh-sidebar-toc-active'); });
                if (activeId) {
                    var activeLink = tocContainer.querySelector('a[href="#' + activeId + '"]');
                    if (activeLink) activeLink.classList.add('crh-sidebar-toc-active');
                }
                spyTicking = false;
            }

            window.addEventListener('scroll', function () {
                if (!spyTicking) {
                    window.requestAnimationFrame(updateTocHighlight);
                    spyTicking = true;
                }
            }, { passive: true });

            /* Run once on load so the right item is highlighted immediately */
            updateTocHighlight();
        } else {
            /* Not enough headings for a TOC — keep sidebar for nav tree only */
            /* Sidebar is part of the layout and will show the navigation tree */
        }
    }

    /* -----------------------------------------
     * CODE BLOCK COPY-TO-CLIPBOARD
     * Wraps pre blocks and adds copy buttons
     * ----------------------------------------- */
    document.querySelectorAll('pre').forEach(function (pre) {
        /* Skip if already has a copy button */
        if (pre.querySelector('.code-copy-btn')) return;

        var wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrap';
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        var btn = document.createElement('button');
        btn.className = 'code-copy-btn';
        btn.setAttribute('aria-label', 'Copy code');
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

        btn.addEventListener('click', function () {
            var code = pre.querySelector('code') ? pre.querySelector('code').textContent : pre.textContent;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(function () {
                    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    setTimeout(function () {
                        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                    }, 2000);
                });
            }
        });

        wrapper.appendChild(btn);
    });

    /* -----------------------------------------
     * WATCH PAGE TOGGLE
     * Uses Confluence REST API to watch/unwatch
     * the current page for update notifications
     * ----------------------------------------- */
    var watchBtn = document.getElementById('watchPageBtn');
    if (watchBtn && typeof pageId !== 'undefined' && pageId) {
        var watchIconOff = watchBtn.querySelector('.watch-icon-off');
        var watchIconOn = watchBtn.querySelector('.watch-icon-on');
        var watchLabel = watchBtn.querySelector('.watch-label');
        var isWatching = false;
        var watchBusy = false;
        var watchApiBase = (typeof contextPath !== 'undefined' ? contextPath : '') + '/rest/api/user/watch/content/' + pageId;

        function updateWatchUI() {
            if (isWatching) {
                watchIconOff.style.display = 'none';
                watchIconOn.style.display = '';
                watchLabel.textContent = 'Watching';
                watchBtn.classList.add('crh-watch-btn-active');
                watchBtn.setAttribute('aria-label', 'Stop watching this page');
            } else {
                watchIconOff.style.display = '';
                watchIconOn.style.display = 'none';
                watchLabel.textContent = 'Watch';
                watchBtn.classList.remove('crh-watch-btn-active');
                watchBtn.setAttribute('aria-label', 'Watch this page for updates');
            }
        }

        /* Check current watch status */
        fetch(watchApiBase, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json' }
        }).then(function (res) {
            if (res.ok) return res.json();
            throw new Error(res.status);
        }).then(function (data) {
            /* Confluence returns { "watching": true/false } */
            isWatching = !!(data && data.watching);
            updateWatchUI();
            watchBtn.style.visibility = 'visible';
        }).catch(function () {
            /* API not available (user not logged in, or permission issue) — hide button */
            watchBtn.style.display = 'none';
        });

        watchBtn.addEventListener('click', function () {
            if (watchBusy) return;
            watchBusy = true;
            watchBtn.classList.add('crh-watch-btn-loading');

            fetch(watchApiBase, {
                method: isWatching ? 'DELETE' : 'POST',
                credentials: 'same-origin',
                headers: { 'X-Atlassian-Token': 'no-check' }
            }).then(function (res) {
                if (res.status === 204 || res.ok) {
                    isWatching = !isWatching;
                    updateWatchUI();
                }
            }).catch(function () {
                /* Silently fail — button stays in current state */
            }).finally(function () {
                watchBusy = false;
                watchBtn.classList.remove('crh-watch-btn-loading');
            });
        });
    }

    /* -----------------------------------------
     * PAGE FEEDBACK WIDGET
     * Yes: thank locally. No: send user to Jira Service Desk with
     * pre-filled page context so the feedback actually lands somewhere.
     * ----------------------------------------- */
    var pfWidget = document.getElementById('pageFeedback');
    if (pfWidget) {
        var pfThanks = document.getElementById('pfThanks');
        var pfHelpdeskUrl = 'https://jira.skatelescope.org/servicedesk/customer/portal/364';

        pfWidget.querySelectorAll('.crh-feedback-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var vote = this.getAttribute('data-vote');
                pfWidget.querySelectorAll('.crh-feedback-btn').forEach(function (b) { b.classList.remove('crh-feedback-selected'); });
                this.classList.add('crh-feedback-selected');

                /* Record vote locally so returning users don't re-vote mindlessly */
                try {
                    var key = 'crh-feedback-' + (pageId || document.title);
                    localStorage.setItem(key, vote + ':' + new Date().toISOString());
                } catch (e) {}

                if (vote === 'no') {
                    /* Surface the "what's missing?" prompt on the widget itself —
                       user can click through to the helpdesk with context. */
                    var questionEl = pfWidget.querySelector('.crh-feedback-question');
                    if (questionEl) questionEl.style.display = 'none';
                    var followUp = document.createElement('div');
                    followUp.className = 'crh-feedback-followup';
                    var summary = 'Creative Hub feedback: ' + (document.title || 'page');
                    var body = 'Page: ' + window.location.href + '\n\nWhat was missing or unclear?\n';
                    followUp.innerHTML =
                        '<p class="crh-feedback-followup-text">Sorry this wasn&rsquo;t helpful. Tell us what\u2019s missing and we\u2019ll fix it.</p>' +
                        '<a class="crh-feedback-followup-btn" href="' + pfHelpdeskUrl +
                        '?summary=' + encodeURIComponent(summary) +
                        '&description=' + encodeURIComponent(body) +
                        '" target="_blank" rel="noopener">Raise a ticket &rarr;</a>';
                    pfWidget.appendChild(followUp);
                } else {
                    /* Yes path — simple thanks */
                    setTimeout(function () {
                        var questionEl = pfWidget.querySelector('.crh-feedback-question');
                        if (questionEl) questionEl.style.display = 'none';
                        if (pfThanks) pfThanks.style.display = 'flex';
                    }, 400);
                }
            });
        });
    }

    /* -----------------------------------------
     * ANNOUNCEMENT BANNER DISMISS
     * Remembers dismissal via localStorage
     * ----------------------------------------- */
    var announceBanner = document.getElementById('announcementBanner');
    var announceClose = document.getElementById('announcementClose');
    if (announceBanner && announceClose) {
        var bannerKey = 'crh-banner-announce-v1';
        try {
            if (localStorage.getItem(bannerKey) === 'dismissed') {
                announceBanner.style.display = 'none';
            }
        } catch (e) {}
        announceClose.addEventListener('click', function () {
            announceBanner.style.display = 'none';
            try { localStorage.setItem(bannerKey, 'dismissed'); } catch (e) {}
        });
    }

    /* -----------------------------------------
     * HERO SEARCH TRIGGER
     * Clicking the hero search box opens the search modal
     * ----------------------------------------- */
    var heroSearchTrigger = document.getElementById('heroSearchTrigger');
    if (heroSearchTrigger) {
        heroSearchTrigger.addEventListener('click', function () {
            var openBtn = document.getElementById('openSearchModal');
            if (openBtn) openBtn.click();
        });
    }

    /* -----------------------------------------
     * ARTICLE DATE FORMATTING
     * Format raw date from Confluence into readable format
     * ----------------------------------------- */
    var dateEl = document.querySelector('.crh-article-date');
    if (dateEl) {
        var rawDate = dateEl.getAttribute('data-raw-date');
        if (rawDate) {
            try {
                var d = new Date(rawDate);
                if (!isNaN(d.getTime())) {
                    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                    var textEl = dateEl.querySelector('.crh-article-date-text');
                    if (textEl) {
                        textEl.textContent = 'Updated ' + months[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
                    }
                }
            } catch (e) {}
        }
    }

    /* -----------------------------------------
     * 404 INTERACTIVE PHYSICS PAGE (Matter.js)
     * Bouncing SKAO pictorial marks with mouse
     * repulsion and drag-and-drop interaction
     * ----------------------------------------- */
    var nfContainer = document.getElementById('notFoundContainer');
    var nfCanvas = document.getElementById('nfCanvas');

    if (nfContainer && nfCanvas && typeof Matter !== 'undefined') {
        /* Hide header/footer — 404 is full-screen */
        var header = document.querySelector('.crh-header');
        var footer = document.querySelector('.crh-footer');
        if (header) header.style.display = 'none';
        if (footer) footer.style.display = 'none';

        /* Resolve the real SKAO pictorial mark from theme assets */
        var themeBase = (function () {
            var link = document.querySelector('link[href*="/css/style.css"]');
            if (link) return link.href.replace('/css/style.css', '');
            return '';
        })();
        var markTextureURL = themeBase + '/images/skao-mark.png';

        /* Preload the texture before starting physics */
        var markImg = new Image();
        markImg.src = markTextureURL;
        markImg.onload = function () {
            initPhysics404(markTextureURL);
        };
    }

    function initPhysics404(textureURL) {
        var canvas = document.getElementById('nfCanvas');
        var container = document.getElementById('notFoundContainer');
        if (!canvas || !container) return;

        var Engine = Matter.Engine,
            Render = Matter.Render,
            World = Matter.World,
            Bodies = Matter.Bodies,
            Body = Matter.Body,
            Mouse = Matter.Mouse,
            MouseConstraint = Matter.MouseConstraint,
            Events = Matter.Events,
            Runner = Matter.Runner;

        /* Size canvas to container */
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;

        /* Create engine */
        var engine = Engine.create({
            gravity: { x: 0, y: 0.9 },
            enableSleeping: false,
            constraintIterations: 3,
            positionIterations: 6,
            velocityIterations: 4,
            timing: { timeScale: 1 }
        });

        /* Create renderer */
        var render = Render.create({
            canvas: canvas,
            engine: engine,
            options: {
                width: canvas.width,
                height: canvas.height,
                wireframes: false,
                background: 'transparent'
            }
        });

        /* Boundary walls */
        var wallT = 50;
        var cw = canvas.width, ch = canvas.height;
        var walls = [
            Bodies.rectangle(cw / 2, ch - wallT / 2, cw, wallT, { isStatic: true, restitution: 0.7, render: { fillStyle: 'transparent' } }),
            Bodies.rectangle(cw / 2, wallT / 2, cw, wallT, { isStatic: true, restitution: 0.7, render: { fillStyle: 'transparent' } }),
            Bodies.rectangle(wallT / 2, ch / 2, wallT, ch, { isStatic: true, restitution: 0.7, render: { fillStyle: 'transparent' } }),
            Bodies.rectangle(cw - wallT / 2, ch / 2, wallT, ch, { isStatic: true, restitution: 0.7, render: { fillStyle: 'transparent' } })
        ];
        World.add(engine.world, walls);

        /* Create SKAO marks */
        var markSize = 50;
        var markRadius = markSize / 2;
        var numMarks = 30;
        var marks = [];

        var groundY = ch - 150;
        var marksPerRow = 6;
        var spacing = markSize * 1.5;

        for (var i = 0; i < numMarks; i++) {
            var row = Math.floor(i / marksPerRow);
            var col = i % marksPerRow;
            var x = 150 + col * spacing + (row % 2) * (spacing / 2);
            var y = groundY - row * (markSize * 0.9);

            var mark = Bodies.circle(x, y, markRadius, {
                restitution: 0.7,
                friction: 0.02,
                frictionAir: 0.01,
                density: 0.0014,
                inertia: Infinity,
                slop: 0.05,
                render: {
                    sprite: {
                        texture: textureURL,
                        xScale: markSize / 200,
                        yScale: markSize / 200
                    }
                }
            });
            marks.push(mark);
        }
        World.add(engine.world, marks);

        /* Mouse constraint — instant drag response */
        var mouse = Mouse.create(canvas);
        var mouseConstraint = MouseConstraint.create(engine, {
            mouse: mouse,
            constraint: {
                stiffness: 1.0,
                damping: 0.05,
                render: { visible: false }
            }
        });
        World.add(engine.world, mouseConstraint);
        render.mouse = mouse;

        /* Track mouse position for repulsion */
        var mousePos = { x: -1000, y: -1000 };
        var lastMousePos = { x: -1000, y: -1000 };

        canvas.addEventListener('mousemove', function (e) {
            var rect = canvas.getBoundingClientRect();
            lastMousePos.x = mousePos.x;
            lastMousePos.y = mousePos.y;
            mousePos.x = e.clientX - rect.left;
            mousePos.y = e.clientY - rect.top;
        });
        canvas.addEventListener('mouseleave', function () {
            mousePos.x = -1000; mousePos.y = -1000;
            lastMousePos.x = -1000; lastMousePos.y = -1000;
        });

        /* Mouse repulsion */
        Events.on(engine, 'beforeUpdate', function () {
            for (var m = 0; m < marks.length; m++) {
                var mk = marks[m];
                var dx = mk.position.x - mousePos.x;
                var dy = mk.position.y - mousePos.y;
                var dist = Math.sqrt(dx * dx + dy * dy);

                var mvx = mousePos.x - lastMousePos.x;
                var mvy = mousePos.y - lastMousePos.y;
                var mSpeed = Math.sqrt(mvx * mvx + mvy * mvy);

                if (dist < 160 && dist > 0) {
                    var falloff = Math.pow((160 - dist) / 160, 1.5);
                    var baseForce = 0.016 * falloff;
                    var velBoost = 1 + (mSpeed * 0.08);
                    var force = baseForce * velBoost;

                    Body.applyForce(mk, mk.position, {
                        x: (dx / dist) * force,
                        y: (dy / dist) * force
                    });
                }
            }
            lastMousePos.x = mousePos.x;
            lastMousePos.y = mousePos.y;
        });

        /* Start engine + renderer */
        var runner = Runner.create();
        Runner.run(runner, engine);
        Render.run(render);

        /* Handle window resize */
        window.addEventListener('resize', function () {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            var w = canvas.width, h = canvas.height;

            Body.setPosition(walls[0], { x: w / 2, y: h - wallT / 2 });
            Body.setVertices(walls[0], Bodies.rectangle(w / 2, h - wallT / 2, w, wallT).vertices);
            Body.setPosition(walls[1], { x: w / 2, y: wallT / 2 });
            Body.setVertices(walls[1], Bodies.rectangle(w / 2, wallT / 2, w, wallT).vertices);
            Body.setPosition(walls[2], { x: wallT / 2, y: h / 2 });
            Body.setVertices(walls[2], Bodies.rectangle(wallT / 2, h / 2, wallT, h).vertices);
            Body.setPosition(walls[3], { x: w - wallT / 2, y: h / 2 });
            Body.setVertices(walls[3], Bodies.rectangle(w - wallT / 2, h / 2, wallT, h).vertices);

            render.bounds.max.x = w;
            render.bounds.max.y = h;
            render.options.width = w;
            render.options.height = h;
            render.canvas.width = w;
            render.canvas.height = h;
        });
    }

    /* -----------------------------------------
     * SYSTEM DARK MODE — OS preference listener
     * Updates live when OS theme changes and user has no stored preference
     * ----------------------------------------- */
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            try {
                if (!localStorage.getItem('crh-theme')) {
                    document.documentElement.classList[e.matches ? 'add' : 'remove']('dark');
                }
            } catch (err) {}
        });
    }

    /* -----------------------------------------
     * CONTENT FRESHNESS INDICATOR
     * Adds a warning badge to pages not updated in 12+ months
     * ----------------------------------------- */
    document.querySelectorAll('.crh-article-date[data-raw-date]').forEach(function (el) {
        var raw = el.getAttribute('data-raw-date');
        if (!raw || raw.charAt(0) === '$') return;
        try {
            var d = new Date(raw);
            if (isNaN(d.getTime())) return;
            if (Math.floor((Date.now() - d.getTime()) / 86400000) > 365) {
                var badge = document.createElement('span');
                badge.className = 'crh-stale-badge';
                badge.title = 'Not updated in over a year \u2014 content may be outdated';
                badge.textContent = 'May be outdated';
                el.parentNode.insertBefore(badge, el.nextSibling);
            }
        } catch (e) {}
    });

    /* -----------------------------------------
     * DYNAMIC RECENT UPDATES
     * Replaces skeleton cards with 3 most recently modified pages via CQL
     * ----------------------------------------- */
    var updatesGrid = document.getElementById('crhUpdatesGrid');
    if (updatesGrid) {
        var spaceKey = updatesGrid.getAttribute('data-space') || 'CRH';
        var homeTitle = updatesGrid.getAttribute('data-home-title') || '';
        var tagMap = {
            'brand': 'brand', 'guideline': 'brand',
            'template': 'templates', 'asset': 'templates', 'slide': 'templates',
            'photo': 'media', 'video': 'media', 'animation': 'media',
            'event': 'events', 'tool': 'tools', 'resource': 'tools'
        };
        function getSectionTag(title) {
            var lower = (title || '').toLowerCase();
            for (var k in tagMap) { if (lower.indexOf(k) !== -1) return tagMap[k]; }
            return 'portal';
        }
        function buildUpdateCard(item) {
            var anc = item.ancestors || [];
            var section = anc.length > 1 ? anc[1].title : (anc.length > 0 ? anc[0].title : 'Hub');
            var tag = getSectionTag(section);
            var dateStr = '';
            try { dateStr = new Date(item.version.when).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' }); } catch (e) {}
            var article = document.createElement('article');
            article.className = 'crh-update-card';
            var a = document.createElement('a');
            /* Prepend contextPath — Scroll Viewport rewrites URLs, raw webui is incomplete */
            var webui = (item._links && item._links.webui) ? item._links.webui : '';
            a.href = webui ? ((typeof contextPath !== 'undefined' ? contextPath : '') + webui) : '#';
            a.className = 'crh-update-card-link';
            var h3 = document.createElement('h3');
            h3.className = 'crh-update-title';
            h3.textContent = item.title;
            a.appendChild(h3);
            var t = document.createElement('time');
            t.className = 'crh-update-date';
            t.textContent = dateStr;
            var sp = document.createElement('span');
            sp.className = 'crh-update-tag crh-update-tag-' + tag;
            sp.textContent = section;
            article.appendChild(a);
            article.appendChild(t);
            article.appendChild(sp);
            return article;
        }
        var cql = 'space = "' + spaceKey + '" AND type = page AND title != "' + homeTitle.replace(/"/g, '\\"') + '" ORDER BY lastModified DESC';
        /* Prepend contextPath — Scroll Viewport serves the portal at a rewritten
           URL, so bare /rest/api/content/search won't resolve to the Confluence
           REST endpoint. Same fix as the search modal code above. */
        var ctx = (typeof contextPath !== 'undefined' ? contextPath : '');
        var endpoint = ctx + '/rest/api/content/search?cql=' + encodeURIComponent(cql) + '&limit=3&expand=version,ancestors';
        fetch(endpoint, {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json', 'X-Atlassian-Token': 'nocheck' }
        })
            .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
            .then(function (data) {
                updatesGrid.innerHTML = '';
                if (data.results && data.results.length) {
                    data.results.forEach(function (item) { updatesGrid.appendChild(buildUpdateCard(item)); });
                } else {
                    updatesGrid.innerHTML = '<p class="crh-updates-empty">No recent updates found.</p>';
                }
            })
            .catch(function (err) {
                /* Log to console so the failure mode is diagnosable without server logs */
                try { console.warn('[CRH] Recent updates fetch failed:', err, 'endpoint:', endpoint); } catch (e) {}
                updatesGrid.innerHTML = '<p class="crh-updates-empty">Could not load recent updates.</p>';
            });
    }

    /* -----------------------------------------
     * HOMEPAGE LABEL-DRIVEN SECTIONS
     * Popular Downloads, Featured Templates, Recently Updated Guidelines.
     * All three use the same CQL pattern: filter by label, order by modified,
     * render via a section-specific builder. Containers opt in via data-label
     * on the element, so markup drives the query.
     * ----------------------------------------- */

    /* Shared helpers */
    var ctx = (typeof contextPath !== 'undefined' ? contextPath : '');

    function formatRelative(iso) {
        if (!iso) return '';
        var then = new Date(iso).getTime();
        if (isNaN(then)) return '';
        var secs = Math.round((Date.now() - then) / 1000);
        if (secs < 60)       return 'just now';
        if (secs < 3600)     return Math.floor(secs / 60) + ' min ago';
        if (secs < 86400)    return Math.floor(secs / 3600) + ' hr ago';
        if (secs < 604800)   return Math.floor(secs / 86400) + ' days ago';
        if (secs < 2592000)  return Math.floor(secs / 604800) + ' wk ago';
        if (secs < 31536000) return Math.floor(secs / 2592000) + ' mo ago';
        return Math.floor(secs / 31536000) + ' yr ago';
    }

    function resolveWebui(item) {
        /* Scroll Viewport rewrites URLs \u2014 raw webui paths need contextPath prepended */
        if (item && item._links && item._links.webui) return ctx + item._links.webui;
        return '#';
    }

    function detectFormat(title) {
        /* Infer a file-type badge from page title text. Fallback: "page" */
        var t = (title || '').toLowerCase();
        if (/\.pptx|powerpoint|deck|slide/.test(t)) return 'pptx';
        if (/\.docx|letterhead|memo|report/.test(t)) return 'docx';
        if (/\.pdf|brand book|guidelines pdf/.test(t)) return 'pdf';
        if (/\.zip|pack|kit/.test(t)) return 'zip';
        if (/logo|image|photo/.test(t)) return 'image';
        return 'docx';
    }

    function ancestorSection(item) {
        /* Section name = first ancestor below home. Ancestors are ordered root-first. */
        var anc = (item && item.ancestors) || [];
        if (anc.length > 1) return anc[1].title;
        if (anc.length > 0) return anc[0].title;
        return 'Hub';
    }

    function titleGradient(title) {
        /* Deterministic gradient for thumbnail fallback \u2014 no flicker on reload */
        var hash = 0, s = title || '';
        for (var i = 0; i < s.length; i++) hash = (hash * 31 + s.charCodeAt(i)) & 0xffffffff;
        var palettes = [
            'linear-gradient(135deg, #9333ea, #C8247E)',
            'linear-gradient(135deg, #C8247E, #003366)',
            'linear-gradient(135deg, #003366, #9333ea)',
            'linear-gradient(135deg, #9333ea, #003366)',
            'linear-gradient(135deg, #C8247E, #9333ea)'
        ];
        return palettes[Math.abs(hash) % palettes.length];
    }

    function showSectionEmpty(container, message) {
        if (!container) return;
        var empty = document.createElement('div');
        empty.className = 'crh-section-empty';
        empty.textContent = message;
        container.innerHTML = '';
        container.appendChild(empty);
    }

    function fetchByLabel(label, limit) {
        var space = 'CRH';
        try { space = document.body.getAttribute('data-space') || space; } catch (e) {}
        var cql = 'space = "' + space + '" AND type = page AND label = "' + label + '" ORDER BY lastModified DESC';
        var endpoint = ctx + '/rest/api/content/search?cql=' + encodeURIComponent(cql) +
                       '&limit=' + limit +
                       '&expand=version,ancestors,metadata.labels';
        return fetch(endpoint, {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json', 'X-Atlassian-Token': 'nocheck' }
        }).then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); });
    }

    /* ---- Popular Downloads ---- */
    var popularList = document.getElementById('crhPopularList');
    if (popularList) {
        var popLabel = popularList.getAttribute('data-label') || 'popular-download';
        var popLimit = parseInt(popularList.getAttribute('data-limit') || '5', 10);
        fetchByLabel(popLabel, popLimit)
            .then(function (data) {
                popularList.innerHTML = '';
                if (!data.results || !data.results.length) {
                    showSectionEmpty(popularList, 'No popular downloads yet. Apply the popular-download label to any page to feature it here.');
                    return;
                }
                data.results.forEach(function (item) {
                    var a = document.createElement('a');
                    a.className = 'crh-popular-item';
                    a.href = resolveWebui(item);
                    var icon = document.createElement('div');
                    icon.className = 'crh-popular-icon';
                    icon.setAttribute('data-type', detectFormat(item.title));
                    var meta = document.createElement('div');
                    meta.className = 'crh-popular-meta';
                    var title = document.createElement('span');
                    title.className = 'crh-popular-title';
                    title.textContent = item.title;
                    var detail = document.createElement('span');
                    detail.className = 'crh-popular-detail';
                    detail.textContent = ancestorSection(item) + ' \u00b7 Updated ' + formatRelative(item.version && item.version.when);
                    meta.appendChild(title);
                    meta.appendChild(detail);
                    var arrow = document.createElement('svg');
                    arrow.setAttribute('class', 'crh-popular-arrow');
                    arrow.setAttribute('width', '18');
                    arrow.setAttribute('height', '18');
                    arrow.setAttribute('viewBox', '0 0 24 24');
                    arrow.setAttribute('fill', 'none');
                    arrow.setAttribute('stroke', 'currentColor');
                    arrow.setAttribute('stroke-width', '2');
                    arrow.innerHTML = '<polyline points="9 18 15 12 9 6"/>';
                    a.appendChild(icon);
                    a.appendChild(meta);
                    a.appendChild(arrow);
                    popularList.appendChild(a);
                });
            })
            .catch(function (err) {
                try { console.warn('[CRH] Popular downloads fetch failed:', err); } catch (e) {}
                showSectionEmpty(popularList, 'Could not load popular downloads.');
            });
    }

    /* ---- Featured Templates ---- */
    var templateGrid = document.getElementById('crhTemplateGrid');
    if (templateGrid) {
        var tplLabel = templateGrid.getAttribute('data-label') || 'featured-template';
        var tplLimit = parseInt(templateGrid.getAttribute('data-limit') || '4', 10);
        fetchByLabel(tplLabel, tplLimit)
            .then(function (data) {
                templateGrid.innerHTML = '';
                if (!data.results || !data.results.length) {
                    showSectionEmpty(templateGrid, 'No featured templates yet. Apply the featured-template label to surface a page here.');
                    return;
                }
                data.results.forEach(function (item) {
                    var a = document.createElement('a');
                    a.className = 'crh-template-card';
                    a.href = resolveWebui(item);
                    var thumb = document.createElement('div');
                    thumb.className = 'crh-template-thumb';
                    /* Confluence Data Centre exposes a page thumbnail at
                       /download/thumbnails/<pageId>/<filename>. We can't know the
                       filename, but attempting the directory listing redirects to
                       the cover image if one is set. Fall back to gradient on 404. */
                    var thumbUrl = ctx + '/download/thumbnails/' + item.id;
                    var probe = new Image();
                    probe.onload = function () { thumb.style.backgroundImage = 'url(' + thumbUrl + ')'; };
                    probe.onerror = function () { thumb.style.backgroundImage = titleGradient(item.title); };
                    probe.src = thumbUrl;
                    /* Default to gradient immediately so there's no delay */
                    thumb.style.backgroundImage = titleGradient(item.title);
                    var fmt = document.createElement('span');
                    fmt.className = 'crh-template-format';
                    fmt.textContent = detectFormat(item.title).toUpperCase();
                    thumb.appendChild(fmt);
                    var body = document.createElement('div');
                    body.className = 'crh-template-body';
                    var title = document.createElement('span');
                    title.className = 'crh-template-title';
                    title.textContent = item.title;
                    var desc = document.createElement('span');
                    desc.className = 'crh-template-desc';
                    desc.textContent = ancestorSection(item);
                    body.appendChild(title);
                    body.appendChild(desc);
                    a.appendChild(thumb);
                    a.appendChild(body);
                    templateGrid.appendChild(a);
                });
            })
            .catch(function (err) {
                try { console.warn('[CRH] Featured templates fetch failed:', err); } catch (e) {}
                showSectionEmpty(templateGrid, 'Could not load featured templates.');
            });
    }

    /* ---- Recently Updated Guidelines ---- */
    var guidelinesList = document.getElementById('crhGuidelinesList');
    if (guidelinesList) {
        var glLabel = guidelinesList.getAttribute('data-label') || 'brand-guideline';
        var glLimit = parseInt(guidelinesList.getAttribute('data-limit') || '5', 10);
        fetchByLabel(glLabel, glLimit)
            .then(function (data) {
                guidelinesList.innerHTML = '';
                if (!data.results || !data.results.length) {
                    var li = document.createElement('li');
                    li.innerHTML = '<div class="crh-section-empty" style="border:none;">No recently updated guidelines. Apply the brand-guideline label to surface pages here.</div>';
                    guidelinesList.appendChild(li);
                    return;
                }
                data.results.forEach(function (item) {
                    var li = document.createElement('li');
                    var a = document.createElement('a');
                    a.className = 'crh-guidelines-item';
                    a.href = resolveWebui(item);
                    var title = document.createElement('span');
                    title.className = 'crh-guidelines-item-title';
                    title.textContent = item.title;
                    var section = document.createElement('span');
                    section.className = 'crh-guidelines-item-section';
                    section.textContent = ancestorSection(item);
                    var date = document.createElement('span');
                    date.className = 'crh-guidelines-item-date';
                    date.textContent = formatRelative(item.version && item.version.when);
                    a.appendChild(title);
                    a.appendChild(section);
                    a.appendChild(date);
                    li.appendChild(a);
                    guidelinesList.appendChild(li);
                });
            })
            .catch(function (err) {
                try { console.warn('[CRH] Recent guidelines fetch failed:', err); } catch (e) {}
                guidelinesList.innerHTML = '<li><div class="crh-section-empty" style="border:none;">Could not load recent guidelines.</div></li>';
            });
    }

    /* -----------------------------------------
     * READING PROGRESS BAR
     * Fills a thin bar at the top as the user scrolls through content
     * ----------------------------------------- */
    var progressBar = document.getElementById('crhProgressBar');
    if (progressBar) {
        function updateProgress() {
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            var docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            var pct = docHeight > 0 ? Math.min(100, Math.round((scrollTop / docHeight) * 100)) : 0;
            progressBar.style.width = pct + '%';
            progressBar.setAttribute('aria-valuenow', pct);
        }
        window.addEventListener('scroll', updateProgress, { passive: true });
        updateProgress();
    }

    /* -----------------------------------------
     * NEW BADGE ON NAV ITEMS
     * Highlights sections updated within the last 14 days
     * ----------------------------------------- */
    var cutoff = Date.now() - (14 * 24 * 60 * 60 * 1000);
    document.querySelectorAll('.crh-nav-link[data-lastmod]').forEach(function (link) {
        var raw = link.getAttribute('data-lastmod');
        if (!raw || raw.charAt(0) === '$') return;
        try {
            var d = new Date(raw);
            if (!isNaN(d.getTime()) && d.getTime() > cutoff) {
                var badge = document.createElement('span');
                badge.className = 'crh-nav-new';
                badge.setAttribute('aria-label', 'Recently updated');
                badge.textContent = 'NEW';
                link.appendChild(badge);
            }
        } catch (e) {}
    });

    /* -----------------------------------------
     * KEYBOARD SHORTCUTS MODAL
     * Opens on ? key; lists all hub shortcuts
     * ----------------------------------------- */
    var kbdModal = document.getElementById('kbdModal');
    var kbdClose = document.getElementById('closeKbdModal');
    var kbdBackdrop = document.getElementById('kbdBackdrop');

    function openKbdModal() {
        if (!kbdModal) return;
        kbdModal.style.display = 'flex';
        requestAnimationFrame(function () { kbdModal.classList.add('crh-kbd-open'); });
        if (kbdClose) kbdClose.focus();
    }
    function closeKbdModal() {
        if (!kbdModal) return;
        kbdModal.classList.remove('crh-kbd-open');
        setTimeout(function () { kbdModal.style.display = 'none'; }, 200);
    }

    if (kbdClose) kbdClose.addEventListener('click', closeKbdModal);
    if (kbdBackdrop) kbdBackdrop.addEventListener('click', closeKbdModal);

    /* D key — dark mode toggle; ? key — shortcuts modal */
    document.addEventListener('keydown', function (e) {
        var tag = (document.activeElement || {}).tagName || '';
        var isEditing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
        if (isEditing) return;
        if (e.key === '?' || (e.key === '/' && e.shiftKey)) {
            e.preventDefault();
            if (kbdModal && kbdModal.style.display !== 'none') { closeKbdModal(); }
            else { openKbdModal(); }
        }
        if (e.key === 'd' || e.key === 'D') {
            var toggle = document.getElementById('themeToggle');
            if (toggle) toggle.click();
        }
        if (e.key === 'Escape') {
            if (kbdModal && kbdModal.style.display !== 'none') closeKbdModal();
        }
    });

});
