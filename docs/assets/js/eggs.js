/* ============================================= */
/* SKAO Science Portal — Easter Eggs              */
/* eggs.js — shhh, it's a secret                  */
/* ============================================= */

document.addEventListener('DOMContentLoaded', function () {

    var eeKeyBuffer = '';
    var eeLogoClicks = 0;
    var eeLastClickTime = 0;
    var eePulsarTimer = null;

    /* --- REGISTRY — all known eggs --- */
    var EE_ALL = ['wow', '1420', 'pulsar', '42'];
    var EE_TOTAL = EE_ALL.length;

    /* --- DISCOVERY TRACKER --- */
    function eeIsDiscovered(type) {
        try { return localStorage.getItem('skao-ee-found-' + type) === '1'; }
        catch (e) { return false; }
    }

    function eeMarkDiscovered(type) {
        try { localStorage.setItem('skao-ee-found-' + type, '1'); }
        catch (e) {}
    }

    function eeGetProgress() {
        var count = 0;
        EE_ALL.forEach(function (t) { if (eeIsDiscovered(t)) count++; });
        return { found: count, total: EE_TOTAL };
    }

    function eeProgressText() {
        var p = eeGetProgress();
        if (p.found === p.total) return 'You\'ve found all ' + p.total + ' surprises! \u2728';
        return 'You\'ve discovered ' + p.found + '/' + p.total + ' surprises!';
    }

    /**
     * Call this when an egg is triggered.
     * Returns true if it's a NEW discovery.
     */
    function eeDiscover(type) {
        var isNew = !eeIsDiscovered(type);
        eeMarkDiscovered(type);
        return isNew;
    }

    /* --- SUPPRESSION via localStorage (don't show again) --- */
    function eeIsSuppressed(type) {
        try { return localStorage.getItem('skao-ee-hide-' + type) === '1'; }
        catch (e) { return false; }
    }

    function eeSuppress(type) {
        try { localStorage.setItem('skao-ee-hide-' + type, '1'); }
        catch (e) {}
    }

    /* Close icon SVG */
    var eeCloseSVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

    function eeClose(overlay) {
        if (eePulsarTimer) { clearInterval(eePulsarTimer); eePulsarTimer = null; }
        var cb = overlay.querySelector('.ee-suppress-cb');
        if (cb && cb.checked) {
            var type = cb.getAttribute('data-ee-type');
            if (type) eeSuppress(type);
        }
        overlay.classList.add('ee-closing');
        setTimeout(function () { overlay.remove(); document.body.style.overflow = ''; }, 250);
    }

    function eeSuppressToggle(type) {
        return '<label class="ee-suppress"><input type="checkbox" class="ee-suppress-cb" data-ee-type="' + type + '"> Don\'t show this again</label>';
    }

    /** Build the progress badge HTML */
    function eeBadgeHTML(flavorText) {
        var p = eeGetProgress();
        var allFound = p.found === p.total;
        var progressBar = '<div class="ee-progress">' +
            '<div class="ee-progress-bar"><div class="ee-progress-fill" style="width:' + Math.round((p.found / p.total) * 100) + '%"></div></div>' +
            '<span class="ee-progress-label">' + p.found + '/' + p.total + ' surprises discovered' + (allFound ? ' \u2728' : '') + '</span>' +
        '</div>';
        return '<div style="text-align:center;"><span class="ee-badge">' + flavorText + '</span></div>' + progressBar;
    }

    function eeShow(html, themeClass, type, badgeFlavor) {
        /* Mark discovery FIRST so progress counts are correct */
        var isNew = eeDiscover(type);

        if (eeIsSuppressed(type)) {
            var star = document.getElementById('resetEasterEggs');
            if (star) star.title = eeProgressText();
            return null;
        }

        /* Build badge + suppress HTML AFTER discovery is recorded */
        var badgeBlock = badgeFlavor ? eeBadgeHTML(badgeFlavor) : '';
        var suppressBlock = eeSuppressToggle(type);

        /* Don't stack multiples */
        var existing = document.querySelector('.ee-overlay');
        if (existing) existing.remove();

        document.body.style.overflow = 'hidden';
        var overlay = document.createElement('div');
        overlay.className = 'ee-overlay';
        overlay.innerHTML = '<div class="ee-modal ' + themeClass + '">' +
            '<button class="ee-close" aria-label="Close">' + eeCloseSVG + '</button>' +
            html + badgeBlock + suppressBlock +
            '</div>';

        document.body.appendChild(overlay);

        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) eeClose(overlay);
        });

        overlay.querySelector('.ee-close').addEventListener('click', function () {
            eeClose(overlay);
        });

        var escHandler = function (e) {
            if (e.key === 'Escape') {
                eeClose(overlay);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        /* Update footer star progress */
        var star = document.getElementById('resetEasterEggs');
        if (star) star.title = eeProgressText();

        return overlay;
    }

    /* --- WOW! SIGNAL --- */
    function eeShowWow() {
        eeShow(
            '<div class="ee-header">' +
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><circle cx="12" cy="12" r="3"/><path d="M2 12h4M18 12h4M12 2v4M12 18v4"/></svg>' +
                '<h2>Wow! Signal Detected</h2>' +
            '</div>' +
            '<div class="ee-panel">' +
                '<div class="ee-signal">6EQUJ5</div>' +
                '<div class="ee-signal-date">August 15, 1977 &middot; Big Ear Radio Observatory</div>' +
            '</div>' +
            '<p class="ee-text">The <strong>Wow! signal</strong> was a strong narrowband radio signal detected on August 15, 1977, by Ohio State University\'s Big Ear radio telescope.</p>' +
            '<p class="ee-text">The signal appeared to come from the direction of Sagittarius and lasted 72 seconds. Astronomer Jerry R. Ehman was so impressed that he circled it on the computer printout and wrote <strong>"Wow!"</strong> in the margin.</p>' +
            '<p class="ee-text"><em>To this day, it remains one of the most intriguing potential signals from space... and a reminder of why we keep listening.</em></p>',
            'ee-wow', 'wow', 'Easter egg discovered!'
        );
    }

    /* --- HYDROGEN LINE (1420) --- */
    function eeShow1420() {
        eeShow(
            '<div class="ee-header">' +
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>' +
                '<h2>The Hydrogen Line</h2>' +
            '</div>' +
            '<div class="ee-panel">' +
                '<div class="ee-freq">1420.405 MHz</div>' +
                '<div class="ee-wavelength">21 cm wavelength</div>' +
            '</div>' +
            '<p class="ee-text">The <strong>21-cm hydrogen line</strong> at 1420.405 MHz is the most important spectral line in radio astronomy.</p>' +
            '<p class="ee-text">It\'s caused by a change in the energy state of neutral hydrogen atoms and allows us to map hydrogen distribution throughout our galaxy and the universe. Since hydrogen is the most abundant element in the universe, this line is fundamental to understanding cosmic structure.</p>' +
            '<p class="ee-text">Fun fact: This frequency is often called the "universal frequency" and is protected from terrestrial interference by international agreement.</p>' +
            '<p class="ee-text"><em>"If extraterrestrial intelligence exists, they\'d know about this frequency too." &mdash; Carl Sagan</em></p>',
            'ee-1420', '1420', 'You know your radio astronomy!'
        );
    }

    /* --- PULSAR --- */
    function eeShowPulsar() {
        var overlay = eeShow(
            '<div class="ee-header">' +
                '<h2>Pulsar Detected</h2>' +
            '</div>' +
            '<p class="ee-subtitle">PSR J0437-4715</p>' +
            '<div class="ee-pulsar-viz">' +
                '<div class="ee-pulsar-glow-outer"></div>' +
                '<div class="ee-pulsar-glow-inner"></div>' +
                '<div class="ee-pulsar-core">' +
                    '<div class="ee-pulsar-beam ee-pulsar-beam-1"></div>' +
                    '<div class="ee-pulsar-beam ee-pulsar-beam-2"></div>' +
                '</div>' +
            '</div>' +
            '<div class="ee-panel ee-pulsar-stats">' +
                '<div class="ee-period">Period: 5.757 ms</div>' +
                '<div class="ee-count" id="eePulseCount">0 pulses detected</div>' +
            '</div>' +
            '<p class="ee-text"><strong>Pulsars</strong> are rapidly rotating neutron stars that emit beams of electromagnetic radiation from their magnetic poles.</p>' +
            '<p class="ee-text">First discovered by Jocelyn Bell Burnell in 1967, pulsars are some of the most precise clocks in the universe. Some rotate hundreds of times per second!</p>' +
            '<p class="ee-text"><em>"Little Green Men"? Nope &mdash; just ultra-dense stellar remnants spinning at incredible speeds.</em></p>',
            'ee-pulsar', 'pulsar', 'Pulsar timing initiated!'
        );

        if (!overlay) return; /* suppressed */

        var pulseCount = 0;
        var countEl = document.getElementById('eePulseCount');
        eePulsarTimer = setInterval(function () {
            pulseCount++;
            if (countEl) countEl.textContent = pulseCount + ' pulse' + (pulseCount !== 1 ? 's' : '') + ' detected';
        }, 500);
    }

    /* --- ANSWER TO EVERYTHING (42) --- */
    function eeShow42() {
        eeShow(
            '<div style="text-align:center;">' +
                '<div class="ee-42-number">42</div>' +
                '<h2>The Answer to Life, the Universe, and Everything</h2>' +
            '</div>' +
            '<div class="ee-panel">' +
                '<p><em>"The answer to the ultimate question of life, the universe, and everything is... forty-two."</em></p>' +
                '<p class="ee-attr">&mdash; Douglas Adams, The Hitchhiker\'s Guide to the Galaxy</p>' +
            '</div>' +
            '<p class="ee-text">Fun astronomy fact: The number 42 appears surprisingly often in astrophysics!</p>' +
            '<ul class="ee-facts">' +
                '<li>The angle of rainbow formation: ~42 degrees</li>' +
                '<li>M42: The Orion Nebula (one of the brightest nebulae visible to the naked eye)</li>' +
                '<li>NGC 42: A galaxy in the Pegasus constellation</li>' +
                '<li>Asteroid 42 Isis discovered in 1856</li>' +
            '</ul>' +
            '<p class="ee-text"><em>"So long, and thanks for all the fish!"</em></p>',
            'ee-42', '42', 'Don\'t forget your towel!'
        );
    }

    /* --- KEYBOARD DETECTION --- */
    document.addEventListener('keypress', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return;
        var searchModal = document.getElementById('searchModal');
        if (searchModal && searchModal.classList.contains('search-modal-open')) return;

        eeKeyBuffer = (eeKeyBuffer + e.key.toLowerCase()).slice(-10);

        if (eeKeyBuffer.indexOf('wow') !== -1) {
            eeKeyBuffer = '';
            eeShowWow();
        } else if (eeKeyBuffer.indexOf('1420') !== -1) {
            eeKeyBuffer = '';
            eeShow1420();
        } else if (eeKeyBuffer.indexOf('pulsar') !== -1) {
            eeKeyBuffer = '';
            eeShowPulsar();
        }
    });

    /* --- RESET LINK (footer star) --- */
    var resetLink = document.getElementById('resetEasterEggs');
    if (resetLink) {
        /* Show progress on hover via title attribute */
        resetLink.title = eeProgressText();

        resetLink.addEventListener('click', function (e) {
            e.preventDefault();
            /* Reset both suppression AND discovery */
            EE_ALL.forEach(function (t) {
                try {
                    localStorage.removeItem('skao-ee-hide-' + t);
                    localStorage.removeItem('skao-ee-found-' + t);
                } catch (ex) {}
            });
            resetLink.textContent = '\u2605'; /* filled star */
            resetLink.title = 'Surprises reset! 0/' + EE_TOTAL + ' discovered.';
            resetLink.classList.add('ee-reset-done');
            setTimeout(function () {
                resetLink.textContent = '\u2606'; /* back to outline star */
                resetLink.title = eeProgressText();
                resetLink.classList.remove('ee-reset-done');
            }, 2000);
        });
    }

    /* --- LOGO CLICK DETECTION (42 clicks) --- */
    var logoLink = document.querySelector('.brand-link');
    var eeNavTimer = null;

    if (logoLink) {
        logoLink.addEventListener('click', function (e) {
            e.preventDefault();

            var now = Date.now();
            clearTimeout(eeNavTimer);

            if (now - eeLastClickTime > 3000) {
                eeLogoClicks = 0;
            }

            eeLogoClicks++;
            eeLastClickTime = now;

            if (eeLogoClicks >= 42) {
                eeLogoClicks = 0;
                eeShow42();
                return;
            }

            var href = logoLink.getAttribute('href') || logoLink.href;
            eeNavTimer = setTimeout(function () {
                eeLogoClicks = 0;
                window.location.href = href;
            }, 600);
        });
    }

});
