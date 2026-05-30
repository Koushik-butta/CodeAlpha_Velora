document.addEventListener('DOMContentLoaded', () => {
    const THEME_KEY = 'velora-theme';

    const getTheme = () => document.documentElement.getAttribute('data-theme') || 'dark';

    const setTheme = (theme) => {
        const next = theme === 'light' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem(THEME_KEY, next);

        let meta = document.querySelector('meta[name="theme-color"]:not([media])');
        if (!meta) {
            meta = document.createElement('meta');
            meta.name = 'theme-color';
            document.head.appendChild(meta);
        }
        meta.content = next === 'light' ? '#f4f2fa' : '#0a0a0a';
    };

    const toggleTheme = () => {
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    };

    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    document.getElementById('themeToggleDrawer')?.addEventListener('click', toggleTheme);

    const yearEl = document.getElementById('year');
    if (yearEl) {
        yearEl.textContent = String(new Date().getFullYear());
    }

    const navToggle = document.getElementById('navToggle');
    const navClose = document.getElementById('navClose');
    const navDrawer = document.getElementById('navDrawer');
    const drawerLinks = navDrawer?.querySelectorAll('.vdrawer__link, .vdrawer__cta a, .vdrawer__brandMini');

    const openDrawer = () => {
        if (!navDrawer) return;
        navDrawer.classList.add('is-open');
        navDrawer.setAttribute('aria-hidden', 'false');
        navToggle?.setAttribute('aria-expanded', 'true');
        document.body.classList.add('is-nav-open');
    };

    const closeDrawer = () => {
        if (!navDrawer) return;
        navDrawer.classList.remove('is-open');
        navDrawer.setAttribute('aria-hidden', 'true');
        navToggle?.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('is-nav-open');
    };

    const isDrawerOpen = () => navDrawer?.classList.contains('is-open') ?? false;

    navToggle?.addEventListener('click', () => {
        if (isDrawerOpen()) {
            closeDrawer();
        } else {
            openDrawer();
        }
    });

    navClose?.addEventListener('click', closeDrawer);

    navDrawer?.addEventListener('click', (event) => {
        if (event.target === navDrawer) {
            closeDrawer();
        }
    });

    drawerLinks?.forEach((link) => {
        link.addEventListener('click', closeDrawer);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && isDrawerOpen()) {
            closeDrawer();
        }
    });

    const revealEls = document.querySelectorAll('[data-reveal]');
    if (revealEls.length) {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('is-in');
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
            );
            revealEls.forEach((el) => observer.observe(el));
        } else {
            revealEls.forEach((el) => el.classList.add('is-in'));
        }
    }

    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length && 'IntersectionObserver' in window) {
        const animateCounter = (el) => {
            const target = Number(el.dataset.to || 0);
            const duration = 1400;
            const start = performance.now();

            const tick = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.floor(target * eased).toLocaleString();
                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    el.textContent = target.toLocaleString();
                }
            };

            requestAnimationFrame(tick);
        };

        const counterObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.35 },
        );

        counters.forEach((el) => counterObserver.observe(el));
    }
});
