/* Presentation-only interactions. No blockchain RPC, wallet access, or transaction submission. */
(() => {
  'use strict';

  // Strip incoming marketing parameters from the visible Pages URL without
  // removing functional query parameters or changing the research content.
  try {
    const cleanUrl = new URL(window.location.href);
    const marketingKeys = /^(?:utm_[a-z0-9_-]+|gclid|fbclid|mc_cid|mc_eid|ref_src|referrer)$/i;
    let cleaned = false;
    for (const key of [...cleanUrl.searchParams.keys()]) {
      if (!marketingKeys.test(key)) continue;
      cleanUrl.searchParams.delete(key);
      cleaned = true;
    }
    if (cleaned) {
      window.history.replaceState(
        window.history.state, '',
        cleanUrl.pathname + cleanUrl.search + cleanUrl.hash
      );
    }
  } catch (_) {
    // Keep the document readable even if URL editing is disallowed.
  }

  const conditions = {
    C0: {
      title: 'Normal delivery',
      description: 'Each completed transfer minted once and invoked the approved observer once.',
      mints: 1, effects: 1, refunds: 0,
      summary: 'Ordinary transfer completes once.'
    },
    C1: {
      title: 'Rejected application',
      description: 'The rejected application produced no successful destination mint or application effect. All three source transfers were refunded.',
      mints: 0, effects: 0, refunds: 3,
      summary: 'Three mined source refunds.'
    },
    F1: {
      title: 'Interrupted processing',
      description: 'For each of three controlled receiver interruptions, settlement minted once but the approved application observer recorded two executions.',
      mints: 1, effects: 2, refunds: 0,
      summary: 'One mint, two effects · all three trials.'
    },
    F2: {
      title: 'Interrupted completion',
      description: 'Across three separate interrupted-completion trials, a later recovery execution repeated the observer effect without a second destination mint.',
      mints: 1, effects: 2, refunds: 0,
      summary: 'One mint, two effects · all three trials.'
    }
  };

  const $ = (selector) => document.querySelector(selector);
  const all = (selector) => [...document.querySelectorAll(selector)];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  function showCondition(key) {
    const result = conditions[key];
    if (!result) return;

    all('[data-condition]').forEach((button) => {
      const active = button.dataset.condition === key;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    $('#condition-heading').textContent = result.title;
    $('#condition-description').textContent = result.description;
    $('#mint-value').textContent = String(result.mints);
    $('#app-value').textContent = String(result.effects);
    $('#refund-value').textContent = result.refunds + ' of 3';
    $('#condition-summary').textContent = result.summary;
    $('#mint-bar').style.width = (result.mints / 2 * 100) + '%';
    $('#app-bar').style.width = (result.effects / 2 * 100) + '%';
  }

  all('[data-condition]').forEach((button) => {
    button.addEventListener('click', () => showCondition(button.dataset.condition));
  });
  showCondition('C0');

  // Native clipboard is only invoked by a deliberate button click.
  all('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const original = button.textContent;
      const status = $('#copy-status');
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) {
          throw new Error('Clipboard unavailable');
        }
        await navigator.clipboard.writeText(button.dataset.copy);
        button.textContent = 'Copied ✓';
        status.textContent = 'Copied to clipboard.';
      } catch (_) {
        button.textContent = 'Select text';
        status.textContent = 'Clipboard permission unavailable. Select the displayed text manually.';
      }
      window.setTimeout(() => { button.textContent = original; }, 2000);
    });
  });

  // Reveal sections with a light 3D entrance. Never hide content without JS.
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    document.documentElement.classList.add('js');
    const observer = new IntersectionObserver((entries, obs) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      }
    }, { rootMargin: '0px 0px -35px 0px', threshold: 0.07 });
    all('[data-reveal]').forEach((el) => observer.observe(el));
  }

  const progress = $('#scroll-progress-fill');
  const art = $('[data-tilt]');
  const glow = $('.hero-glow-one');
  let scrollRequested = false;

  function updateScroll() {
    scrollRequested = false;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const fraction = maxScroll > 0 ? window.scrollY / maxScroll : 0;
    if (progress) progress.style.transform = 'scaleX(' + Math.max(0, Math.min(1, fraction)) + ')';

    if (!reducedMotion.matches && window.scrollY < window.innerHeight * 1.4) {
      const offset = Math.max(0, window.scrollY);
      if (glow) glow.style.transform = 'translate3d(0,' + Math.round(offset * .16) + 'px,0)';
      if (art && !finePointer.matches) art.style.setProperty('--rx', Math.min(6, offset / 100) + 'deg');
    }
  }
  window.addEventListener('scroll', () => {
    if (scrollRequested) return;
    scrollRequested = true;
    requestAnimationFrame(updateScroll);
  }, { passive: true });
  window.addEventListener('resize', updateScroll, { passive: true });
  updateScroll();

  if (finePointer.matches && !reducedMotion.matches && art) {
    const hitbox = art.parentElement;
    hitbox.addEventListener('pointermove', (event) => {
      const bounds = hitbox.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - .5;
      const y = (event.clientY - bounds.top) / bounds.height - .5;
      art.style.setProperty('--ry', (x * 10).toFixed(2) + 'deg');
      art.style.setProperty('--rx', (-y * 7).toFixed(2) + 'deg');
    });
    hitbox.addEventListener('pointerleave', () => {
      art.style.setProperty('--ry', '0deg');
      art.style.setProperty('--rx', '0deg');
    });
  }

  if ('IntersectionObserver' in window) {
    const links = all('.main-nav a[href^="#"]');
    const sectionMap = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
    const sectionObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((a) => a.removeAttribute('aria-current'));
        const selected = sectionMap.get(entry.target.id);
        if (selected) selected.setAttribute('aria-current', 'true');
      }
    }, { rootMargin: '-30% 0px -55% 0px', threshold: 0 });
    for (const id of sectionMap.keys()) {
      const section = document.getElementById(id);
      if (section) sectionObserver.observe(section);
    }
  }
})();