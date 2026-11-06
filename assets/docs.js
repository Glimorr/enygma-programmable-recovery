/* Independent Enygma research library enhancements.
 * Read-only navigation, animations, copy controls and an original animated guide.
 * No wallet API, RPC calls, transaction submission, or experimental execution. */
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

  const $ = (s, root = document) => root.querySelector(s);
  const all = (s, root = document) => Array.from(root.querySelectorAll(s));
  const content = $('#research-content');
  if (!content) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover:hover) and (pointer:fine)');
  const siteBase = window.location.pathname.split('/docs/')[0] || '';
  const docs = [
    { file: 'Research.html', label: 'Research report' },
    { file: 'Evidence-Register.html', label: 'Evidence register' },
    { file: 'Verification-Boundaries.html', label: 'Verification method' },
    { file: 'Claims-and-Evidence.html', label: 'Claims & evidence' },
    { file: 'Disclosure.html', label: 'Disclosure & scope' },
    { file: 'Recording-Guide.html', label: 'Recording guide' }
  ];
  const currentFile = window.location.pathname.split('/').filter(Boolean).pop() || 'Research.html';
  const pageIndex = Math.max(0, docs.findIndex(doc => doc.file === currentFile));

  // Kramdown emits .html pages for the public site. Keep original Markdown
  // source links intact in GitHub while making the rendered HTML links work.
  all('a[href]', content).forEach((link) => {
    const attr = link.getAttribute('href') || '';
    if (!attr || attr.startsWith('#') || /^(https?:|mailto:|tel:|data:)/i.test(attr)) return;
    if (/\.md(?:#|$)/i.test(attr)) {
      link.setAttribute('href', attr.replace(/\.md(?=#|$)/i, '.html'));
    }
    // GitHub Pages does not provide directory listings for evidence directories.
    const href = link.getAttribute('href');
    if (/^(?:\.\.\/)?(?:evidence\/raw\/measured\/|lab\/)(?:#.*)?$/.test(href || '')) {
      const subdir = href.replace(/^(\.\.\/)/, '').split('#')[0];
      link.href = 'https://github.com/Glimorr/enygma-programmable-recovery/tree/main/' + subdir;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
  });

  // Responsive source tables remain semantically complete and keyboard-scrollable.
  all('table', content).forEach((table) => {
    if (table.parentElement?.classList.contains('table-wrap')) return;
    const container = document.createElement('div');
    container.className = 'table-wrap';
    container.tabIndex = 0;
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', 'Scrollable research data table');
    table.parentNode.insertBefore(container, table);
    container.appendChild(table);
  });

  function copyToClipboard(text) {
    if (navigator.clipboard?.writeText && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('aria-hidden', 'true');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.append(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    textarea.remove();
    return success ? Promise.resolve() : Promise.reject(new Error('Clipboard denied'));
  }

  all('pre', content).forEach((pre) => {
    const original = pre.textContent.trim();
    if (!original || original.length > 16000) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'code-copy';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code block');
    button.addEventListener('click', async () => {
      try {
        await copyToClipboard(original);
        button.textContent = 'Copied ✓';
      } catch {
        button.textContent = 'Select text';
        const range = document.createRange();
        range.selectNodeContents(pre);
        window.getSelection()?.removeAllRanges();
        window.getSelection()?.addRange(range);
      }
      window.setTimeout(() => { button.textContent = 'Copy'; }, 2500);
    });
    pre.append(button);
  });

  // Build an accessible table of contents directly from published section headings.
  const headings = all('h2', content);
  const toc = $('#page-toc');
  const mobileToc = $('#mobile-toc');
  headings.forEach((heading, index) => {
    if (!heading.id) {
      const base = heading.textContent.toLowerCase().normalize('NFKD')
        .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      heading.id = 'chapter-' + (base || (index + 1));
    }
    const anchor = document.createElement('a');
    anchor.href = '#' + heading.id;
    anchor.textContent = heading.textContent.trim();
    anchor.dataset.chapterIndex = String(index);
    toc?.append(anchor);
    mobileToc?.append(anchor.cloneNode(true));
  });
  if (headings.length === 0 && toc) {
    toc.textContent = 'Full document';
  }

  const tocToggle = $('#toc-toggle');
  const mobileOutline = $('#mobile-outline');
  tocToggle?.addEventListener('click', () => {
    const open = tocToggle.getAttribute('aria-expanded') !== 'true';
    tocToggle.setAttribute('aria-expanded', String(open));
    mobileOutline.hidden = !open;
  });
  all('#mobile-toc a').forEach((a) => {
    a.addEventListener('click', () => {
      mobileOutline.hidden = true;
      tocToggle?.setAttribute('aria-expanded', 'false');
    });
  });

  all('.collection-links a').forEach((a) => {
    if (a.dataset.pageName === currentFile) {
      a.classList.add('is-current');
      a.setAttribute('aria-current', 'page');
    }
  });
  all('.header-links a').forEach((a) => {
    if (a.pathname === window.location.pathname) {
      a.classList.add('is-current');
      a.setAttribute('aria-current', 'page');
    }
  });

  const pageCount = content.textContent.trim().split(/\s+/).length;
  const timeTarget = $('#read-time');
  if (timeTarget) timeTarget.textContent = Math.max(1, Math.ceil(pageCount / 220)) + ' MIN';

  // Related reading navigation never changes the source or the trial archive.
  const pagination = $('#document-prev-next');
  function paginationLink(doc, direction) {
    const a = document.createElement('a');
    a.href = siteBase + '/docs/' + doc.file;
    a.className = 'doc-pagination-link';
    const type = document.createElement('small');
    type.textContent = direction === 'prev' ? '← PREVIOUS DOCUMENT' : 'NEXT DOCUMENT →';
    const title = document.createElement('strong');
    title.textContent = doc.label;
    a.append(type, title);
    return a;
  }
  if (pagination) {
    if (pageIndex > 0) pagination.append(paginationLink(docs[pageIndex - 1], 'prev'));
    if (pageIndex < docs.length - 1) pagination.append(paginationLink(docs[pageIndex + 1], 'next'));
    if (pagination.children.length === 1) pagination.style.gridTemplateColumns = '1fr';
  }

  const guide = $('#guide-widget');
  const guideToggle = $('#guide-toggle');
  const guideBubble = $('#guide-speech');
  const guideMessage = $('#guide-message');
  const guideStep = $('#guide-step');
  const guideNext = $('#guide-next');
  const guideHide = $('#guide-hide');
  const status = $('#guide-status');
  let activeChapter = -1;
  let guideOpen = window.matchMedia('(max-width: 650px)').matches ? false : true;

  function setGuideOpen(open) {
    guideOpen = open;
    if (guide) guide.dataset.open = open ? 'true' : 'false';
    guideToggle?.setAttribute('aria-expanded', String(open));
    guideToggle?.setAttribute('aria-label', open ? 'Hide animated research guide' : 'Open animated research guide');
    guideBubble?.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (status) status.textContent = open ? 'Orbit research guide opened.' : 'Orbit research guide hidden.';
  }
  setGuideOpen(guideOpen);
  guideToggle?.addEventListener('click', () => setGuideOpen(!guideOpen));
  guideHide?.addEventListener('click', () => setGuideOpen(false));

  function guideTip(text) {
    const heading = text.toLowerCase();
    if (/network|experiment|environment|test|method/.test(heading))
      return 'Here’s how the experiment was constructed. Keep the control conditions separate from recovery trials.';
    if (/result|finding|observation|supported/.test(heading))
      return 'Follow both numbers: destination token mints and application effects are different measurements.';
    if (/refund|compensat/.test(heading))
      return 'A refund should be traced to its actual source-chain transaction and restored balance.';
    if (/evidence|receipt|archive|inspect/.test(heading))
      return 'Want to verify a claim? Follow the corresponding source records and transaction hashes.';
    if (/verification|hosted|independent|rebuild/.test(heading))
      return 'Hosted checks reproduce code or archive calculations—not the original private-chain consensus.';
    if (/public|commit|digest/.test(heading))
      return 'The public testnet transaction commits the archive digest after the experiment.';
    if (/interpretation|scope|disclosure|boundar|what these/.test(heading))
      return 'Separate what the controlled trial established from what would require another deployment.';
    if (/source/.test(heading))
      return 'These sources link the measurements back to the relevant official Rayls documentation and code.';
    if (/video|capture|record/.test(heading))
      return 'Keep the recording silent and read-only, with transaction hashes legible on screen.';
    return 'This section adds context to the research. Use the next-section button to follow the evidence in order.';
  }

  function setActiveChapter(index) {
    activeChapter = index;
    all('.toc-links a, #mobile-toc a').forEach((link) => {
      const active = Number(link.dataset.chapterIndex) === index;
      link.classList.toggle('is-active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (guideStep) guideStep.textContent = String(Math.min(headings.length, index + 1)).padStart(2, '0');
    if (guideMessage) {
      guideMessage.textContent = index < 0
        ? 'I’m Orbit. I’ll help you navigate the methodology and evidence without changing a single result.'
        : guideTip(headings[index]?.textContent || '');
    }
    if (guideNext) {
      guideNext.innerHTML = index < headings.length - 1
        ? 'Next section <span aria-hidden="true">↓</span>'
        : 'Next document <span aria-hidden="true">↗</span>';
    }
  }

  guideNext?.addEventListener('click', () => {
    if (headings.length === 0 || activeChapter >= headings.length - 1) {
      const next = docs[Math.min(pageIndex + 1, docs.length - 1)];
      if (next.file !== currentFile) window.location.assign(siteBase + '/docs/' + next.file);
      else window.location.assign(siteBase + '/');
      return;
    }
    const nextIndex = activeChapter + 1;
    headings[nextIndex].scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth', block: 'start' });
  });

  const progressFill = $('#progress-fill');
  const graphic = $('#hero-graphic');
  const heroCard = $('#hero-card');
  let pendingFrame = false;
  function updateScroll() {
    pendingFrame = false;
    const denominator = document.documentElement.scrollHeight - window.innerHeight;
    const progress = denominator > 0 ? Math.min(1, Math.max(0, window.scrollY / denominator)) : 0;
    if (progressFill) progressFill.style.transform = 'scaleX(' + progress + ')';

    // Use simple bounding-rectangle checks, limited to the small document TOC.
    let chapter = -1;
    for (let i = 0; i < headings.length; i++) {
      if (headings[i].getBoundingClientRect().top < window.innerHeight * .48) chapter = i;
      else break;
    }
    if (chapter !== activeChapter) setActiveChapter(chapter);

    if (!reduceMotion.matches && graphic && window.scrollY < 640) {
      const amount = Math.max(0, window.scrollY);
      graphic.style.transform = 'translate3d(0,' + Math.round(amount * .15) + 'px,0)';
      if (!finePointer.matches && heroCard) {
        heroCard.style.setProperty('--tilt-x', Math.min(6, amount / 90).toFixed(2) + 'deg');
      }
    }
  }
  window.addEventListener('scroll', () => {
    if (!pendingFrame) {
      pendingFrame = true;
      window.requestAnimationFrame(updateScroll);
    }
  }, { passive:true });
  window.addEventListener('resize', updateScroll, { passive: true });
  setActiveChapter(-1);
  updateScroll();

  if (finePointer.matches && !reduceMotion.matches && graphic && heroCard) {
    graphic.addEventListener('pointermove', e => {
      const r = graphic.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      heroCard.style.setProperty('--tilt-y', (x * 10).toFixed(2) + 'deg');
      heroCard.style.setProperty('--tilt-x', (-y * 8).toFixed(2) + 'deg');
    });
    graphic.addEventListener('pointerleave', () => {
      heroCard.style.setProperty('--tilt-y', '0deg');
      heroCard.style.setProperty('--tilt-x', '0deg');
    });
  }

  // Deliberate use of IntersectionObserver: readers without JS still see everything.
  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    document.documentElement.classList.add('js');
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      }
    }, { threshold: 0.08, rootMargin:'0px 0px -15px 0px' });
    all('h2, .table-wrap, p > img', content).forEach(el => {
      el.dataset.reveal = 'true';
      observer.observe(el);
    });
  }
})();