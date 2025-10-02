let scoresChartInst = null;
let ratingsChartInst = null;
let loadedOnce = false;

function byId(id) {
  return document.getElementById(id);
}

// 🔍 AI Heuristics Helper
function heuristicsFor(h) {
  const tips = [];
  if ((h.transport || '').toLowerCase() === 'air') {
    tips.push('Switch from air to sea or rail; batch shipments to reduce GHG.');
  }
  if ((h.materials || []).includes('plastic')) {
    tips.push('Increase recycled or bio-based content; redesign to reduce plastic mass.');
  }
  if ((h.circularity ?? 100) < 60) {
    tips.push('Improve design for reuse/repair/recycling to raise circularity above 60%.');
  }
  if ((h.gwp ?? 0) > 12) {
    tips.push('Target processes or suppliers with lower embodied carbon to cut GWP.');
  }
  return tips;
}

// 🧠 Show AI Suggestions Panel
function showAiPanel(h) {
  const panel = byId('aiPanel'), why = byId('aiWhy'), ul = byId('aiActions');
  if (!panel || !why || !ul) return;

  panel.hidden = false;

  // Summary reasoning
  const parts = [];
  parts.push(`Score ${Math.round(h.score)} (${h.rating}) driven by ${h.transport || 'unknown'} transport and ${Array.isArray(h.materials) ? h.materials.join(', ') : 'materials'}.`);
  if (typeof h.circularity === 'number') parts.push(`Circularity at ${h.circularity}%.`);
  if (typeof h.gwp === 'number') parts.push(`GWP approx. ${h.gwp}.`);
  why.textContent = parts.join(' ');

  // Suggestions
  const combo = [...(h.suggestions || []), ...heuristicsFor(h)];
  const seen = new Set(), top = [];
  for (const s of combo) {
    const k = s.toLowerCase();
    if (!seen.has(k)) {
      seen.add(k);
      top.push(s);
    }
    if (top.length === 3) break;
  }

  ul.innerHTML = '';
  top.forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    ul.appendChild(li);
  });
}

// Fetch JSON helper
async function fetchJson(url) {
  const r = await fetch(url, {
    headers: { "Accept": "application/json" },
    cache: "no-store"
  });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}

// Prevent Chart.js resize loop
function lockCanvas(id) {
  const el = byId(id);
  if (!el) return;
  el.height = 260;
  el.style.height = '260px';
  el.style.width = '100%';
  el.style.display = 'block';
}

// 🟦 Render Scores Chart
function renderScores(hist) {
  lockCanvas('scoresChart');
  const empty = byId('scoresEmpty');
  const canvas = byId('scoresChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (!hist || hist.length === 0) {
    if (empty) empty.hidden = false;
    if (scoresChartInst) {
      scoresChartInst.destroy();
      scoresChartInst = null;
    }
    return;
  }

  if (empty) empty.hidden = true;

  const last = hist.slice(-20); // 👈 Save for click handler
  const labels = last.map(h => `${h.product_name} #${h.id}`);
  const data = last.map(h => h.score);

  if (scoresChartInst) {
    scoresChartInst.destroy();
    scoresChartInst = null;
  }

  scoresChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Sustainability Score',
        data,
        backgroundColor: '#4f46e5',
        borderColor: '#4338ca',
        borderWidth: 1
      }]
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      animation: loadedOnce ? false : { duration: 300 },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 10 }
        }
      },
      plugins: {
        legend: { display: false }
      },
      // 👇 Click handler for AI suggestions
      onClick: (evt, els) => {
        if (!els || !els.length) return;
        const idx = els[0].index;
        const h = last[idx];
        showAiPanel(h);
      }
    }
  });

  scoresChartInst.update(); // 👈 Required after modifying options
}

// 🟡 Render Ratings Chart
function renderRatings(sum) {
  lockCanvas('ratingsChart');
  const empty = byId('ratingsEmpty');
  const canvas = byId('ratingsChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const ratings = (sum && sum.ratings) ? sum.ratings : {};
  const labels = Object.keys(ratings);
  const data = labels.map(k => ratings[k]);
  const total = data.reduce((a, b) => a + b, 0);

  if (total === 0) {
    if (empty) empty.hidden = false;
    if (ratingsChartInst) {
      ratingsChartInst.destroy();
      ratingsChartInst = null;
    }
    return;
  }

  if (empty) empty.hidden = true;

  if (ratingsChartInst) {
    ratingsChartInst.destroy();
    ratingsChartInst = null;
  }

  ratingsChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: ['#16a34a', '#3b82f6', '#f59e0b', '#ef4444']
      }]
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      animation: loadedOnce ? false : { duration: 300 },
      plugins: { legend: { position: 'bottom' } }
    }
  });
}

// 📊 Render Summary KPIs
function renderSummary(sum) {
  byId('kpiTotal').textContent = sum.total_products;
  byId('kpiAvg').textContent = (sum.average_score ?? 0).toFixed(2);

  const badge = byId('kpiAvgBadge');
  const avg = sum.average_score ?? 0;
  let label = 'Needs data', cls = 'tag';
  if (avg >= 85) { label = 'Excellent'; cls = 'tag ok'; }
  else if (avg >= 70) { label = 'Good'; cls = 'tag'; }
  else { label = 'Attention'; cls = 'tag warn'; }
  badge.className = cls;
  badge.textContent = label;

  // Ratings tags
  const rt = byId('kpiRatings');
  rt.innerHTML = '';
  ['A', 'B', 'C', 'D'].forEach(k => {
    const v = (sum.ratings && sum.ratings[k]) ? sum.ratings[k] : 0;
    const t = document.createElement('span');
    t.className = v >= 1 ? 'tag ok' : 'tag';
    t.textContent = `${k}: ${v}`;
    rt.appendChild(t);
  });

  // Top issues
  const issues = byId('kpiIssues');
  issues.innerHTML = '';
  (sum.top_issues || []).forEach(s => {
    const t = document.createElement('span');
    t.className = 'tag warn';
    t.textContent = s;
    issues.appendChild(t);
  });

  // Raw JSON
  const el = byId('summary');
  if (el) {
    el.textContent = JSON.stringify({
      total_products: sum.total_products,
      average_score: sum.average_score,
      ratings: sum.ratings,
      top_issues: sum.top_issues
    }, null, 2);
  }
}

// 🌐 Load Data and Render
async function load() {
  if (window.__DASHBOARD_LOADING__) return;
  window.__DASHBOARD_LOADING__ = true;
  try {
    const [hist, sum] = await Promise.all([
      fetchJson('/history?limit=50'),
      fetchJson('/score-summary')
    ]);
    renderScores(hist);
    renderRatings(sum);
    renderSummary(sum);
    loadedOnce = true;
  } catch (err) {
    console.error(err);
    const el = byId('summary');
    if (el) el.textContent = `Failed to load: ${err}`;
  } finally {
    window.__DASHBOARD_LOADING__ = false;
  }
}

// Initialize
if (!window.__DASHBOARD_BOUND__) {
  window.__DASHBOARD_BOUND__ = true;
  document.addEventListener('DOMContentLoaded', load, { once: true });
}
