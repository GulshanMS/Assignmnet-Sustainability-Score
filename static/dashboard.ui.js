// Inject header, handle theme toggle, persist theme; no chart changes here.
(function () {
  if (window.__UI_BOOTSTRAPPED__) return;
  window.__UI_BOOTSTRAPPED__ = true;

  function applyTheme(t) {
    const root = document.documentElement;
    if (t === 'light') {
      root.style.setProperty('--bg', '#0f172a');
      root.style.setProperty('--card', '#111834'); // keep contrast; light-on-dark variant
      root.style.setProperty('--text', '#e5e7eb');
      root.style.setProperty('--muted', '#a3a8b5');
      root.style.setProperty('--border', '#23304e');
    } else {
      // default dark already defined by base CSS
      root.style.setProperty('--bg', '#0b1020');
      root.style.setProperty('--card', '#111834');
      root.style.setProperty('--text', '#e5e7eb');
      root.style.setProperty('--muted', '#9ca3af');
      root.style.setProperty('--border', '#1f2a44');
    }
  }

  function currentTheme() {
    return localStorage.getItem('theme') || 'dark';
  }

  function setTheme(t) {
    localStorage.setItem('theme', t);
    applyTheme(t);
  }

  function buildAppbar() {
    const bar = document.createElement('div');
    bar.className = 'appbar';
    bar.innerHTML = `
      <div class="brand">Sustainability Dashboard</div>
      <div class="actions">
        <label class="toggle">
          <input type="checkbox" id="themeToggle">
          <span class="switch"></span>
          <span>Light</span>
        </label>
      </div>
    `;
    return bar;
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Insert header above main container
    const headerMount = document.body.firstElementChild;
    const appbar = buildAppbar();
    document.body.insertBefore(appbar, headerMount);

    // Theme setup
    const initial = currentTheme();
    applyTheme(initial);
    const toggle = document.getElementById('themeToggle');
    toggle.checked = (initial === 'light');
    toggle.addEventListener('change', () => setTheme(toggle.checked ? 'light' : 'dark'));
  }, { once: true });

  // ✅ Banner behavior: show once unless dismissed
  document.addEventListener('DOMContentLoaded', () => {
    const key = 'hideSubmitBanner';
    const b = document.getElementById('submitBanner');
    const close = document.getElementById('bannerClose');
    if (b && !localStorage.getItem(key)) b.hidden = false;
    if (close) {
      close.onclick = () => {
        b.hidden = true;
        localStorage.setItem(key, '1');
      };
    }
  }, { once: true });
})();

document.addEventListener('DOMContentLoaded', () => {
  const key = 'hideSubmitBanner';
  const b = document.getElementById('submitBanner');
  const close = document.getElementById('bannerClose');

  if (b && !localStorage.getItem(key)) b.hidden = false;

  if (close) {
    // Capture phase to intercept before any parent/link handlers
    close.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      e.stopPropagation();
      if (b) b.hidden = true;
      try { localStorage.setItem(key, '1'); } catch {}
      return false;
    }, true); // <-- capture
  }
}, { once: true });
