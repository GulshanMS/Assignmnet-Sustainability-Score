let scoresChartInst = null;
let ratingsChartInst = null;
let loadedOnce = false;

function byId(id) { return document.getElementById(id); }

async function fetchJson(url) {
  const r = await fetch(url, { headers: { "Accept": "application/json" }, cache: "no-store" });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}

// Lock canvas pixel size to stop Chart.js resize loop
function lockCanvas(id) {
  const el = byId(id);
  if (!el) return;
  el.height = 260;            // device pixels
  el.style.height = '260px';  // CSS pixels
  el.style.width = '100%';
  el.style.display = 'block';
}

function renderScores(hist) {
  lockCanvas('scoresChart');
  const empty = byId('scoresEmpty');
  const canvas = byId('scoresChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (!hist || hist.length === 0) {
    if (empty) empty.hidden = false;
    if (scoresChartInst) { scoresChartInst.destroy(); scoresChartInst = null; }
    return;
  }
  if (empty) empty.hidden = true;

  const last = hist.slice(-20);
  const labels = last.map(h => `${h.product_name} #${h.id}`);
  const data = last.map(h => h.score);

  if (scoresChartInst) { scoresChartInst.destroy(); scoresChartInst = null; }
  scoresChartInst = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Sustainability Score', data, backgroundColor: '#4f46e5', borderColor: '#4338ca', borderWidth: 1 }] },
    options: {
      responsive: false,                 // critical: disable auto-resize
      maintainAspectRatio: false,
      animation: loadedOnce ? false : { duration: 300 },
      scales: { y: { beginAtZero: true, max: 100, ticks: { stepSize: 10 } } },
      plugins: { legend: { display: false } }
    }
  });
}

function renderRatings(sum) {
  lockCanvas('ratingsChart');
  const empty = byId('ratingsEmpty');
  const canvas = byId('ratingsChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const ratings = (sum && sum.ratings) ? sum.ratings : {};
  const labels = Object.keys(ratings);
  const data = labels.map(k => ratings[k]);
  const total = data.reduce((a,b)=>a+b,0);

  if (total === 0) {
    if (empty) empty.hidden = false;
    if (ratingsChartInst) { ratingsChartInst.destroy(); ratingsChartInst = null; }
    return;
  }
  if (empty) empty.hidden = true;

  if (ratingsChartInst) { ratingsChartInst.destroy(); ratingsChartInst = null; }
  ratingsChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: ['#16a34a','#3b82f6','#f59e0b','#ef4444'] }] },
    options: {
      responsive: false,                 // critical: disable auto-resize
      maintainAspectRatio: false,
      animation: loadedOnce ? false : { duration: 300 },
      plugins: { legend: { position: 'bottom' } }
    }
  });
}

function renderSummary(sum) {
  const el = byId('summary');
  if (!el) return;
  el.textContent = JSON.stringify({
    total_products: sum.total_products,
    average_score: sum.average_score,
    ratings: sum.ratings,
    top_issues: sum.top_issues
  }, null, 2);
}

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
    const el = byId('summary'); if (el) el.textContent = `Failed to load: ${err}`;
  } finally {
    window.__DASHBOARD_LOADING__ = false;
  }
}

if (!window.__DASHBOARD_BOUND__) {
  window.__DASHBOARD_BOUND__ = true;
  document.addEventListener('DOMContentLoaded', load, { once: true });
}
