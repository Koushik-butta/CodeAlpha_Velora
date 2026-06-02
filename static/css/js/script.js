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
      opt.addEventListener('click', (e) => {
        applyThemeWithTransition(opt.dataset.themeVal, e);
        dropdown.style.display = 'none';
      });
    });
  }
  document.querySelectorAll('.theme-opt-circle').forEach(circle => {
    circle.addEventListener('click', (e) => { applyThemeWithTransition(circle.dataset.themeVal, e); });
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
          const isWish = btn.classList.contains('wishlisted');
          const icon = btn.querySelector('.wish-icon');
          if (icon) icon.textContent = isWish ? '♥' : '♡';
          if (isWish) {
            triggerHearts(e.clientX, e.clientY);
          }
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

/* ---- CONFETTI CELEBRATION EFFECT ---- */
function triggerConfetti() {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '99999';
  document.body.appendChild(canvas);
  
  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;
  
  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });
  
  const colors = ['#FF9933', '#128807', '#3B82F6', '#EC4899', '#FBBF24', '#00FFFF'];
  const particles = [];
  
  for (let i = 0; i < 150; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height - height,
      r: Math.random() * 6 + 4,
      d: Math.random() * width,
      color: colors[Math.floor(Math.random() * colors.length)],
      tilt: Math.random() * 10 - 5,
      tiltAngleIncremental: Math.random() * 0.07 + 0.02,
      tiltAngle: 0
    });
  }
  
  let opacity = 1.0;
  
  function draw() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p, idx) => {
      p.tiltAngle += p.tiltAngleIncremental;
      p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
      p.x += Math.sin(p.tiltAngle);
      p.tilt = Math.sin(p.tiltAngle - idx/3) * 15;
      
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.globalAlpha = opacity;
      ctx.moveTo(p.x + p.tilt + p.r/2, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r/2);
      ctx.stroke();
    });
    
    opacity -= 0.006;
    if (opacity > 0) {
      requestAnimationFrame(draw);
    } else {
      canvas.remove();
    }
  }
  draw();
}

document.addEventListener('DOMContentLoaded', () => {
  const hasSuccessToast = document.querySelector('.alert-success');
  if (hasSuccessToast) {
    // Small delay so toast loads, then boom!
    setTimeout(triggerConfetti, 200);
  }
  
  // Attach sparks listener to Ashoka Chakra spinning wheels
  document.querySelectorAll('.chakra-wheel').forEach(wheel => {
    wheel.style.cursor = 'pointer';
    wheel.addEventListener('click', e => {
      e.stopPropagation();
      triggerSparks(e.clientX, e.clientY);
    });
  });
  
  // Initialize new visual components
  initScrollEffects();
  initCard3DTilt();
  initMagneticButtons();
  initHeroParticles();
  initDynamicGreeting();
  initCursorTrail();
});

/* ---- ADVANCED TRANSITIONS & EFFECTS ---- */

// 1. Theme Change Circular Sweep Ripple Transition
function applyThemeWithTransition(t, e) {
  let x = window.innerWidth / 2;
  let y = window.innerHeight / 2;
  if (e && e.clientX && e.clientY) {
    x = e.clientX;
    y = e.clientY;
  }

  // Create sweep overlay ripple
  const ripple = document.createElement('div');
  ripple.className = 'theme-switch-ripple';
  
  // Calculate size to cover all corners
  const maxDim = Math.max(window.innerWidth, window.innerHeight);
  const size = maxDim * 2.5;
  ripple.style.width = size + 'px';
  ripple.style.height = size + 'px';
  ripple.style.left = (x - size / 2) + 'px';
  ripple.style.top = (y - size / 2) + 'px';
  
  // Setup colors (radial sweep gradient starting with primary theme variables)
  ripple.style.background = 'radial-gradient(circle, var(--primary) 0%, var(--bg) 80%)';
  document.body.appendChild(ripple);
  
  // Trigger paint
  ripple.offsetHeight;
  
  ripple.style.transform = 'scale(1)';
  ripple.style.opacity = '0.96';
  
  setTimeout(() => {
    applyTheme(t);
  }, 220);
  
  setTimeout(() => {
    ripple.style.opacity = '0';
    setTimeout(() => ripple.remove(), 400);
  }, 650);
}

// 2. Interactive Canvas Spark Burst centered on Logo Wheel Click
function triggerSparks(x, y) {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '999999';
  document.body.appendChild(canvas);
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  const particles = [];
  const computedStyle = getComputedStyle(document.documentElement);
  const color1 = computedStyle.getPropertyValue('--primary').trim() || '#FF9933';
  const color2 = computedStyle.getPropertyValue('--buy').trim() || '#128807';
  const color3 = computedStyle.getPropertyValue('--swap').trim() || '#F59E0B';
  const resolvedColors = [color1, color2, color3, '#FFFFFF'];

  for (let i = 0; i < 24; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = Math.random() * 4 + 2.5;
    particles.push({
      x: x,
      y: y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: Math.random() * 3 + 1.8,
      color: resolvedColors[Math.floor(Math.random() * resolvedColors.length)],
      alpha: 1.0,
      decay: Math.random() * 0.035 + 0.02
    });
  }
  
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let active = false;
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.08; // gravity
      p.alpha -= p.decay;
      if (p.alpha > 0) {
        active = true;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.shadowBlur = 4;
        ctx.shadowColor = p.color;
        ctx.fill();
      }
    });
    if (active) {
      requestAnimationFrame(draw);
    } else {
      canvas.remove();
    }
  }
  draw();
}

// 3. Scroll Depth and Back-To-Top Circular Button
function initScrollEffects() {
  const scrollIndicator = document.getElementById('scroll-progress-indicator');
  const backToTopBtn = document.getElementById('backToTop');
  const progressCircle = backToTopBtn?.querySelector('.circle-progress');
  
  if (!scrollIndicator && !backToTopBtn) return;
  
  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight <= 0) return;
    
    const pct = (window.scrollY / totalHeight) * 100;
    
    if (scrollIndicator) {
      scrollIndicator.style.width = pct + '%';
    }
    
    if (backToTopBtn) {
      if (window.scrollY > 300) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
      
      if (progressCircle) {
        const offset = 138 - (pct / 100 * 138);
        progressCircle.style.strokeDashoffset = offset;
      }
    }
  }, { passive: true });
  
  backToTopBtn?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// 4. 3D Card Hover Perspective and Cursor Spotlight Glow
function initCard3DTilt() {
  document.querySelectorAll('.pcard').forEach(card => {
    card.style.setProperty('--mouse-x', '0px');
    card.style.setProperty('--mouse-y', '0px');
    
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
      
      // Calculate rotation angles
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -6; // max 6 deg
      const rotateY = ((x - centerX) / centerX) * 6;  // max 6 deg
      
      card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)';
    });
  });
}

// 5. Magnetic Button physics (for CTAs)
function initMagneticButtons() {
  document.querySelectorAll('.btn-sell, .theme-toggle, .hero__pill').forEach(btn => {
    btn.classList.add('btn-magnetic');
    
    btn.addEventListener('mousemove', e => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      
      btn.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`;
    });
    
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0px, 0px)';
    });
  });
}

// 6. Interactive Floating Canvas Particles in Hero Section
function initHeroParticles() {
  const canvas = document.getElementById('hero-particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  let width = canvas.width = canvas.offsetWidth;
  let height = canvas.height = canvas.offsetHeight;
  
  window.addEventListener('resize', () => {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
  });
  
  const particles = [];
  const computedStyle = getComputedStyle(document.documentElement);
  
  for (let i = 0; i < 35; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 2 + 1,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      alpha: Math.random() * 0.4 + 0.15
    });
  }
  
  let mouse = { x: -1000, y: -1000 };
  const parent = canvas.parentElement;
  
  parent.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  
  parent.addEventListener('mouseleave', () => {
    mouse.x = -1000;
    mouse.y = -1000;
  });
  
  function animate() {
    ctx.clearRect(0, 0, width, height);
    
    // Resolve dynamic primary color from theme
    const colorPrimary = computedStyle.getPropertyValue('--primary').trim() || '#FF9933';
    
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      
      // Repel from cursor
      if (mouse.x > -1000) {
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          const force = (100 - dist) / 100;
          p.x += (dx / dist) * force * 2.5;
          p.y += (dy / dist) * force * 2.5;
        }
      }
      
      // Boundaries
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;
      
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = colorPrimary;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    });
    requestAnimationFrame(animate);
  }
  animate();
}

// Initialize Page Loading Progress indicator immediately
initLoadingProgress();

function initLoadingProgress() {
  // Try to find element or create immediate indicator
  document.addEventListener('DOMContentLoaded', () => {
    const bar = document.getElementById('page-loader-progress');
    if (!bar) return;
    
    bar.style.width = '0%';
    bar.style.opacity = '1';
    
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 12 + 4;
      if (progress >= 92) {
        progress = 92;
        clearInterval(interval);
      }
      bar.style.width = progress + '%';
    }, 80);
    
    window.addEventListener('load', () => {
      clearInterval(interval);
      bar.style.width = '100%';
      setTimeout(() => {
        bar.style.opacity = '0';
      }, 150);
    });
  });
}

// 7. Confetti Hearts on Wishlist Toggle
function triggerHearts(x, y) {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '999999';
  document.body.appendChild(canvas);
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  const particles = [];
  
  for (let i = 0; i < 15; i++) {
    particles.push({
      x: x,
      y: y,
      vx: (Math.random() - 0.5) * 3.2,
      vy: -Math.random() * 4 - 2.5, // float upwards
      r: Math.random() * 6 + 4.5,
      color: ['#FF2E93', '#FF4E75', '#FF7597', '#E879F9'][Math.floor(Math.random() * 4)],
      alpha: 1.0,
      decay: Math.random() * 0.02 + 0.015,
      angle: Math.random() * 360,
      spin: (Math.random() - 0.5) * 4.5
    });
  }
  
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let active = false;
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.98; // horizontal air resistance
      p.angle += p.spin;
      p.alpha -= p.decay;
      
      if (p.alpha > 0) {
        active = true;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle * Math.PI / 180);
        ctx.globalAlpha = p.alpha;
        
        // Draw Heart Shape
        ctx.beginPath();
        const size = p.r;
        ctx.moveTo(0, size / 4);
        ctx.bezierCurveTo(0, -size / 2, -size, -size / 2, -size, 0);
        ctx.bezierCurveTo(-size, size / 2, 0, size, 0, size * 1.25);
        ctx.bezierCurveTo(0, size, size, size / 2, size, 0);
        ctx.bezierCurveTo(size, -size / 2, 0, -size / 2, 0, size / 4);
        ctx.closePath();
        
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 4;
        ctx.shadowColor = p.color;
        ctx.fill();
        ctx.restore();
      }
    });
    
    if (active) {
      requestAnimationFrame(draw);
    } else {
      canvas.remove();
    }
  }
  draw();
}

// 8. Time of Day Welcome Greeting for Dashboard Home
function initDynamicGreeting() {
  const el = document.getElementById('dynamic-greeting-label');
  if (!el) return;
  const hours = new Date().getHours();
  let greet = 'Namaste, Welcome Back';
  if (hours < 12) {
    greet = 'Namaste 🌅 Good Morning, Welcome Back';
  } else if (hours < 17) {
    greet = 'Namaste ☀️ Good Afternoon, Welcome Back';
  } else if (hours < 21) {
    greet = 'Namaste 🌆 Good Evening, Welcome Back';
  } else {
    greet = 'Namaste 🌙 Good Night, Welcome Back';
  }
  el.textContent = greet;
}

// 9. Synthesized Foley Audio Feedback (Removed)

// 10. Dynamic Cursor Trail Particles (sparkles following mouse movement)
function initCursorTrail() {
  const canvas = document.getElementById('cursor-trail-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;
  
  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });
  
  const particles = [];
  const computedStyle = getComputedStyle(document.documentElement);
  
  window.addEventListener('mousemove', e => {
    // Spawn trail particles dynamically matching active theme primary colors
    const colorPrimary = computedStyle.getPropertyValue('--primary').trim() || '#FF9933';
    
    for (let i = 0; i < 2; i++) {
      particles.push({
        x: e.clientX,
        y: e.clientY,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5 - 0.4, // float slightly upward
        r: Math.random() * 2.8 + 1.2,
        color: colorPrimary,
        alpha: 0.75,
        decay: Math.random() * 0.035 + 0.02
      });
    }
  });
  
  function draw() {
    ctx.clearRect(0, 0, width, height);
    
    const colorPrimary = computedStyle.getPropertyValue('--primary').trim() || '#FF9933';
    
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.alpha -= p.decay;
      
      if (p.alpha <= 0) {
        particles.splice(i, 1);
      } else {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color === 'var(--primary)' || !p.color ? colorPrimary : p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
}
