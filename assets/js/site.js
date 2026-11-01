(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  // Theme toggle (initial theme is set inline in <head> to avoid a flash)
  var themeBtn = $('#themeToggle');
  function syncThemeLabel() {
    var dark = root.getAttribute('data-theme') === 'dark';
    themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', dark ? '#07080F' : '#F7F7FB');
  }
  themeBtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    syncThemeLabel();
  });
  syncThemeLabel();

  // Mobile menu
  var links = $('#navLinks'), menuBtn = $('#menuBtn');
  function setMenu(open) {
    links.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open);
    menuBtn.innerHTML = open ? '<i class="bi bi-x-lg"></i>' : '<i class="bi bi-list"></i>';
  }
  menuBtn.addEventListener('click', function () { setMenu(!links.classList.contains('open')); });
  $$('a', links).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && links.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
  });
  document.addEventListener('click', function (e) {
    var path = e.composedPath();
    if (links.classList.contains('open') && path.indexOf(links) < 0 && path.indexOf(menuBtn) < 0) setMenu(false);
  });

  // Scroll: progress bar, nav shadow, back-to-top, active section link
  var bar = $('#progress'), nav = $('#topbar'), toTop = $('#toTop');
  var sections = $$('main section[id]');
  var ticking = false;
  function onScroll() {
    ticking = false;
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%';
    nav.classList.toggle('scrolled', scrollY > 30);
    toTop.classList.toggle('show', scrollY > 600);
    var current = '';
    sections.forEach(function (s) { if (scrollY >= s.offsetTop - 140) current = s.id; });
    $$('a', links).forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + current); });
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  toTop.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });

  // Typewriter
  var typed = $('#typed');
  if (typed) {
    var roles = ['Lead Software Engineer', 'Quality Engineering Leader', 'Test Automation Architect', 'Performance Testing Specialist', 'AI-Driven Engineer', 'Open-Source Creator'];
    if (reduce) {
      typed.textContent = roles[0];
    } else {
      var ri = 0, ci = 0, del = false;
      (function type() {
        var word = roles[ri];
        typed.textContent = word.slice(0, ci);
        if (!del && ci < word.length) ci++;
        else if (del && ci > 0) ci--;
        else { del = !del; if (!del) ri = (ri + 1) % roles.length; return setTimeout(type, del ? 1600 : 300); }
        setTimeout(type, del ? 35 : 75);
      })();
    }
  }

  // Reveal on scroll, count-up numbers and skill bars
  function count(n) {
    var target = +n.dataset.count, start = null;
    if (reduce) { n.textContent = target + '+'; return; }
    n.textContent = '0';
    requestAnimationFrame(function step(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / 1600, 1);
      n.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + (p === 1 ? '+' : '');
      if (p < 1) requestAnimationFrame(step);
    });
  }
  function reveal(el) {
    el.classList.add('in');
    $$('[data-count]', el).forEach(count);
    $$('.bar i', el).forEach(function (b) { b.style.width = b.dataset.w + '%'; });
  }
  var targets = $$('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        reveal(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (n) { io.observe(n); });
  } else {
    targets.forEach(reveal);
  }

  // Cursor spotlight on cards
  if (window.matchMedia('(hover: hover)').matches) {
    $$('.spot').forEach(function (c) {
      c.addEventListener('pointermove', function (e) {
        var r = c.getBoundingClientRect();
        c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        c.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });
  }

  // Tabs that switch sibling panes
  $$('.tabs').forEach(function (tabs) {
    var buttons = $$('.tab[data-pane]', tabs);
    if (!buttons.length) return;
    buttons.forEach(function (t) {
      t.addEventListener('click', function () {
        buttons.forEach(function (x) {
          x.classList.toggle('active', x === t);
          x.setAttribute('aria-selected', x === t);
        });
        $$(':scope > .pane', tabs.parentElement).forEach(function (p) {
          var show = p.id === 'pane-' + t.dataset.pane;
          p.classList.toggle('show', show);
          if (show) $$('.reveal', p).forEach(reveal);
        });
      });
    });
  });

  // Project filter
  var filters = $$('#filters .tab');
  filters.forEach(function (t) {
    t.addEventListener('click', function () {
      filters.forEach(function (x) {
        x.classList.toggle('active', x === t);
        x.setAttribute('aria-pressed', x === t);
      });
      $$('.project').forEach(function (p) {
        var show = t.dataset.filter === 'all' || p.dataset.cat === t.dataset.filter;
        p.classList.toggle('hide', !show);
        if (show) {
          p.classList.add('in');
          if (!reduce) p.animate([{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'none' }], { duration: 450, easing: 'ease-out' });
        }
      });
    });
  });

  // Testimonials slider
  var quotes = $$('.quote'), dots = $('#dots');
  if (quotes.length && dots) {
    var qi = 0, timer;
    quotes.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Show testimonial ' + (i + 1));
      b.addEventListener('click', function () { go(i); restart(); });
      dots.appendChild(b);
    });
    var go = function (i) {
      qi = (i + quotes.length) % quotes.length;
      quotes.forEach(function (q, j) { q.classList.toggle('active', j === qi); q.setAttribute('aria-hidden', j !== qi); });
      $$('button', dots).forEach(function (d, j) { d.classList.toggle('active', j === qi); });
    };
    var restart = function () {
      clearInterval(timer);
      if (!reduce) timer = setInterval(function () { go(qi + 1); }, 7000);
    };
    var prev = $('.t-nav.prev'), next = $('.t-nav.next'), slider = $('.t-slider');
    if (prev) prev.addEventListener('click', function () { go(qi - 1); restart(); });
    if (next) next.addEventListener('click', function () { go(qi + 1); restart(); });
    slider.addEventListener('mouseenter', function () { clearInterval(timer); });
    slider.addEventListener('mouseleave', restart);
    slider.addEventListener('focusin', function () { clearInterval(timer); });
    var x0 = null;
    slider.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; clearInterval(timer); }, { passive: true });
    slider.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) go(qi + (dx < 0 ? 1 : -1));
      x0 = null; restart();
    });
    go(0); restart();
  }

  // Detail page gallery
  var stage = $('.g-stage');
  if (stage) {
    var slides = $$('img', stage), thumbs = $$('.g-thumbs button'), gi = 0;
    var counter = $('.g-count'), lb = null;
    var show = function (i) {
      gi = (i + slides.length) % slides.length;
      slides.forEach(function (s, j) { s.classList.toggle('active', j === gi); });
      thumbs.forEach(function (t, j) { t.classList.toggle('active', j === gi); });
      var label = (gi + 1) + ' / ' + slides.length;
      if (counter) counter.textContent = label;
      if (lb) { $('img', lb).src = slides[gi].currentSrc || slides[gi].src; $('.lb-count', lb).textContent = label; }
    };
    // Full-screen viewer
    var openLb = function () {
      if (!lb) {
        lb = document.createElement('div');
        lb.className = 'lightbox';
        lb.setAttribute('role', 'dialog');
        lb.setAttribute('aria-modal', 'true');
        lb.setAttribute('aria-label', 'Screenshot viewer');
        lb.innerHTML = '<img alt=""><button class="icon-btn lb-close" type="button" aria-label="Close viewer"><i class="bi bi-x-lg"></i></button>' +
          (slides.length > 1 ? '<button class="icon-btn lb-prev" type="button" aria-label="Previous screenshot"><i class="bi bi-chevron-left"></i></button><button class="icon-btn lb-next" type="button" aria-label="Next screenshot"><i class="bi bi-chevron-right"></i></button>' : '') +
          '<span class="lb-count"></span>';
        document.body.appendChild(lb);
        lb.addEventListener('click', function (e) {
          if (e.target.closest('.lb-prev')) show(gi - 1);
          else if (e.target.closest('.lb-next')) show(gi + 1);
          else if (e.target === lb || e.target.closest('.lb-close')) closeLb();
        });
      }
      show(gi);
      $('img', lb).alt = slides[gi].alt;
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
      $('.lb-close', lb).focus();
    };
    var closeLb = function () {
      if (!lb) return;
      lb.classList.remove('open');
      document.body.style.overflow = '';
      var z = $('.g-zoom'); if (z) z.focus();
    };
    slides.forEach(function (s) { s.addEventListener('click', openLb); });
    var zoom = $('.g-zoom');
    if (zoom) zoom.addEventListener('click', openLb);
    thumbs.forEach(function (t, i) { t.addEventListener('click', function () { show(i); }); });
    var gp = $('.g-nav.prev'), gn = $('.g-nav.next');
    if (gp) gp.addEventListener('click', function () { show(gi - 1); });
    if (gn) gn.addEventListener('click', function () { show(gi + 1); });
    document.addEventListener('keydown', function (e) {
      if (e.target.closest('input, textarea')) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'ArrowLeft') show(gi - 1);
      if (e.key === 'ArrowRight') show(gi + 1);
    });
  }

  // "Download resume (PDF)": print the page with the resume stylesheet
  var printBtn = $('#printCv');
  if (printBtn) {
    printBtn.addEventListener('click', function () {
      window.print();
    });
  }
  var closedForPrint = [];
  addEventListener('beforeprint', function () {
    $$('.reveal').forEach(reveal);
    closedForPrint = $$('details:not([open])');
    closedForPrint.forEach(function (d) { d.open = true; });
  });
  addEventListener('afterprint', function () {
    closedForPrint.forEach(function (d) { d.open = false; });
    closedForPrint = [];
  });

  // Contact form via FormSubmit (free, no backend required)
  var form = $('#contactForm');
  if (form) {
    var status = $('#formStatus'), btn = $('#sendBtn');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) {
        status.className = 'form-status err';
        status.textContent = 'Please fill in all fields with a valid email address.';
        var bad = $(':invalid', form);
        if (bad) bad.focus();
        return;
      }
      btn.disabled = true;
      status.className = 'form-status';
      status.textContent = 'Sending...';
      fetch(form.action, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.success === 'true' || d.success === true) {
            status.className = 'form-status ok';
            status.textContent = 'Thanks! Your message has been sent — I\'ll get back to you soon.';
            form.reset();
          } else {
            throw new Error(d.message);
          }
        })
        .catch(function (err) {
          // FormSubmit rejects pages opened as local files and forms that are not yet activated
          var why = location.protocol === 'file:' ? 'The form only works on the live site, not when the page is opened as a local file. '
            : /activ/i.test(err && err.message) ? 'The form is awaiting activation. ' : '';
          status.className = 'form-status err';
          status.innerHTML = why + 'Please email me directly at <a href="mailto:osanda.deshan@gmail.com">osanda.deshan@gmail.com</a>.';
        })
        .finally(function () { btn.disabled = false; });
    });
  }
})();
