(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const items = document.querySelectorAll('.reveal');

  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.06 });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add('in'));
  }

  const heroImg = document.querySelector('.hero img');
  if (heroImg && !reduce) {
    let queued = false;
    addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => {
        const y = Math.min(scrollY, innerHeight);
        heroImg.style.transform = `translate3d(0, ${y * 0.16}px, 0) scale(1.06)`;
        queued = false;
      });
    }, { passive: true });
  }

  const chips = document.querySelectorAll('[data-lot]');
  const field = document.getElementById('lot-value');
  chips.forEach((chip) => chip.addEventListener('click', () => {
    chips.forEach((c) => c.setAttribute('aria-pressed', 'false'));
    chip.setAttribute('aria-pressed', 'true');
    if (field) field.value = chip.dataset.lot;
  }));
})();
  const dlg = document.getElementById('lightbox');
  if (dlg) {
    document.querySelectorAll('[data-full]').forEach((el) => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        dlg.querySelector('img').src = el.dataset.full;
        dlg.showModal();
      });
    });
    dlg.addEventListener('click', () => dlg.close());
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && dlg.open) dlg.close(); });
  }
