/* ============================================================
   VELORA MARKETPLACE — Main Script v2.0
   ============================================================ */
'use strict';

/* ---- THEME ---- */
const THEME_KEY = 'velora_theme';
function applyTheme(t) {
  if (t === 'dark') t = 'sunset-saffron';
  if (t === 'light') t = 'classic-light';
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem(THEME_KEY, t);
  updateThemeUIActiveState(t);

  // Sync to database if CSRF token is present
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    fetch('/dashboard/theme/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ theme: t })
    }).catch(() => {});
  }
}

function updateThemeUIActiveState(t) {
  document.querySelectorAll('.theme-opt').forEach(opt => {
    opt.classList.toggle('active', opt.dataset.themeVal === t);
  });
  document.querySelectorAll('.theme-opt-circle').forEach(circle => {
    circle.classList.toggle('active', circle.dataset.themeVal === t);
  });
}

(function initTheme() {
  let saved = localStorage.getItem(THEME_KEY);
  if (saved === 'dark') saved = 'sunset-saffron';
  if (saved === 'light') saved = 'classic-light';
  const pref = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'sunset-saffron' : 'classic-light';
  applyTheme(saved || pref);
})();

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('themeToggleBtn');
  const dropdown = document.getElementById('themeDropdown');
  if (btn && dropdown) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = dropdown.style.display === 'none' || dropdown.style.display === '';
      dropdown.style.display = isHidden ? 'block' : 'none';
    });
    document.addEventListener('click', () => { dropdown.style.display = 'none'; });
    dropdown.addEventListener('click', (e) => { e.stopPropagation(); });
    dropdown.querySelectorAll('.theme-opt').forEach(opt => {
      opt.addEventListener('click', () => {
        applyTheme(opt.dataset.themeVal);
        dropdown.style.display = 'none';
      });
    });
  }
  document.querySelectorAll('.theme-opt-circle').forEach(circle => {
    circle.addEventListener('click', () => { applyTheme(circle.dataset.themeVal); });
  });
  const currentTheme = localStorage.getItem(THEME_KEY) || 'sunset-saffron';
  updateThemeUIActiveState(currentTheme);
});

/* ---- NAVBAR SCROLL ---- */
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.vnav');
  if (!nav) return;
  let lastY = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    nav.classList.toggle('scrolled', y > 20);
    lastY = y;
  }, { passive: true });
});

/* ---- MOBILE DRAWER ---- */
document.addEventListener('DOMContentLoaded', () => {
  const burger = document.getElementById('vBurger');
  const drawer = document.getElementById('vDrawer');
  const overlay = document.getElementById('vDrawerOverlay');
  const close = document.getElementById('vDrawerClose');
  if (!burger || !drawer) return;
  function openDrawer() {
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.classList.add('nav-open');
    burger.setAttribute('aria-expanded', 'true');
  }
  function closeDrawer() {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.classList.remove('nav-open');
    burger.setAttribute('aria-expanded', 'false');
  }
  burger.addEventListener('click', openDrawer);
  close?.addEventListener('click', closeDrawer);
  overlay?.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });
});

/* ---- USER DROPDOWN ---- */
document.addEventListener('DOMContentLoaded', () => {
  const trigger = document.getElementById('userDropdownTrigger');
  const menu = document.getElementById('userDropdownMenu');
  if (!trigger || !menu) return;
  trigger.addEventListener('click', e => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });
  document.addEventListener('click', () => menu.classList.remove('open'));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') menu.classList.remove('open');
  });
});

/* ---- SCROLL REVEAL ---- */
document.addEventListener('DOMContentLoaded', () => {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('in'), i * 80);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  els.forEach(el => io.observe(el));
});

/* ---- COUNTER ANIMATION ---- */
function animateCounter(el) {
  const target = parseFloat(el.dataset.counter);
  const suffix = el.dataset.suffix || '';
  const prefix = el.dataset.prefix || '';
  const duration = parseInt(el.dataset.duration || 1800);
  const isDecimal = target % 1 !== 0;
  const start = performance.now();
  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = target * ease;
    el.textContent = prefix + (isDecimal ? val.toFixed(1) : Math.floor(val).toLocaleString('en-IN')) + suffix;
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = prefix + (isDecimal ? target.toFixed(1) : target.toLocaleString('en-IN')) + suffix;
  }
  requestAnimationFrame(update);
}
document.addEventListener('DOMContentLoaded', () => {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { animateCounter(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => io.observe(c));
});

/* ---- OTP INPUT BOXES ---- */
document.addEventListener('DOMContentLoaded', () => {
  const otpBoxes = document.querySelectorAll('.otp-box');
  if (!otpBoxes.length) return;
  otpBoxes.forEach((box, i) => {
    box.addEventListener('input', e => {
      const val = e.target.value.replace(/\D/g, '');
      e.target.value = val.slice(-1);
      if (val) { box.classList.add('filled'); }
      else { box.classList.remove('filled'); }
      if (val && i < otpBoxes.length - 1) otpBoxes[i + 1].focus();
      combineOTP();
    });
    box.addEventListener('keydown', e => {
      if (e.key === 'Backspace' && !box.value && i > 0) {
        otpBoxes[i - 1].focus();
        otpBoxes[i - 1].value = '';
        otpBoxes[i - 1].classList.remove('filled');
      }
      if (e.key === 'ArrowLeft' && i > 0) otpBoxes[i - 1].focus();
      if (e.key === 'ArrowRight' && i < otpBoxes.length - 1) otpBoxes[i + 1].focus();
    });
    box.addEventListener('paste', e => {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
      [...text.slice(0, 6)].forEach((char, j) => {
        if (otpBoxes[j]) { otpBoxes[j].value = char; otpBoxes[j].classList.add('filled'); }
      });
      const next = Math.min(text.length, otpBoxes.length - 1);
      otpBoxes[next].focus();
      combineOTP();
    });
  });
  function combineOTP() {
    const hidden = document.getElementById('otp_combined');
    if (hidden) hidden.value = [...otpBoxes].map(b => b.value).join('');
  }
});

/* ---- OTP COUNTDOWN TIMER ---- */
document.addEventListener('DOMContentLoaded', () => {
  const timerEl = document.getElementById('otpCountdown');
  const resendBtn = document.getElementById('otpResend');
  if (!timerEl) return;
  let seconds = parseInt(timerEl.dataset.seconds || 120);
  function tick() {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
    if (seconds <= 0) {
      timerEl.textContent = '0:00';
      if (resendBtn) { resendBtn.removeAttribute('disabled'); resendBtn.classList.remove('btn-ghost'); resendBtn.classList.add('btn-sell'); }
      return;
    }
    seconds--;
    setTimeout(tick, 1000);
  }
  tick();
});

/* ---- MULTI-STEP FORM ---- */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('multiStepForm');
  if (!form) return;
  const steps = form.querySelectorAll('[data-step]');
  const progressNums = document.querySelectorAll('.step-progress__num');
  const progressLines = document.querySelectorAll('.step-progress__line');
  let current = 0;
  function showStep(n) {
    steps.forEach((s, i) => s.style.display = i === n ? 'block' : 'none');
    progressNums.forEach((p, i) => {
      p.classList.remove('active', 'done');
      if (i < n) p.classList.add('done');
      if (i === n) p.classList.add('active');
    });
    progressLines.forEach((l, i) => {
      l.classList.toggle('done', i < n);
    });
    current = n;
  }
  showStep(0);
  form.querySelectorAll('[data-next]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (validateStep(current)) showStep(current + 1);
    });
  });
  form.querySelectorAll('[data-prev]').forEach(btn => {
    btn.addEventListener('click', () => { if (current > 0) showStep(current - 1); });
  });
  function validateStep(n) {
    const step = steps[n];
    const required = step.querySelectorAll('[required]');
    let valid = true;
    required.forEach(inp => {
      if (!inp.value.trim()) {
        inp.classList.add('error');
        valid = false;
        inp.addEventListener('input', () => inp.classList.remove('error'), { once: true });
      }
    });
    return valid;
  }
});

/* ---- HERO SEARCH SELECT ---- */
document.addEventListener('DOMContentLoaded', () => {
  const catSelect = document.getElementById('heroCategory');
  const searchInput = document.getElementById('heroSearchInput');
  const form = document.getElementById('heroSearchForm');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const q = searchInput?.value.trim();
    const cat = catSelect?.value;
    let url = '/products/?q=' + encodeURIComponent(q || '');
    if (cat) url += '&category=' + encodeURIComponent(cat);
    window.location.href = url;
  });
});

/* ---- WISHLIST TOGGLE ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-wishlist-btn]').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault(); e.stopPropagation();
      const productId = btn.dataset.productId;
      if (!productId) { window.location.href = '/login/'; return; }
      try {
        const res = await fetch(`/products/wishlist/toggle/${productId}/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        if (res.ok) {
          btn.classList.toggle('wishlisted');
          const icon = btn.querySelector('.wish-icon');
          if (icon) icon.textContent = btn.classList.contains('wishlisted') ? '♥' : '♡';
        } else if (res.status === 403) { window.location.href = '/login/'; }
      } catch {}
    });
  });
});

/* ---- PASSWORD STRENGTH ---- */
document.addEventListener('DOMContentLoaded', () => {
  const pwdInput = document.getElementById('id_password1') || document.getElementById('id_new_password1');
  const bar = document.getElementById('pwdStrengthBar');
  if (!pwdInput || !bar) return;
  pwdInput.addEventListener('input', () => {
    const pw = pwdInput.value;
    let score = 0;
    if (pw.length >= 8) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['', 'var(--error)', 'var(--offer)', 'var(--swap)', 'var(--buy)'];
    bar.style.width = (score * 25) + '%';
    bar.style.background = colors[score];
    const txt = document.getElementById('pwdStrengthTxt');
    if (txt) { txt.textContent = labels[score]; txt.style.color = colors[score]; }
  });
});

/* ---- CATEGORY PILL ACTIVE ---- */
document.addEventListener('DOMContentLoaded', () => {
  const url = new URL(window.location.href);
  const cat = url.searchParams.get('category');
  if (cat) {
    document.querySelectorAll('.cat-pill').forEach(p => {
      if (p.dataset.cat === cat) { p.classList.add('active'); p.classList.add(`cat-pill-${cat}`); }
    });
  }
});

/* ---- TOAST MESSAGES (auto-dismiss) ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast-msg').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 300);
    }, 4000);
    el.querySelector('.toast-close')?.addEventListener('click', () => el.remove());
  });
});

/* ---- CSRF HELPER ---- */
function getCookie(name) {
  const parts = `; ${document.cookie}`.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

/* ---- SMOOTH ANCHOR SCROLL ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});
