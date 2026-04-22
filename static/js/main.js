/* ─── main.js ─────────────────────────────────────────────────────────────── */

'use strict';

// ── State ────────────────────────────────────────────────────────────────────
let selectedMovie = '';

// ── Navbar shrink on scroll ───────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('mainNav');
  if (window.scrollY > 50) {
    nav.style.padding = '8px 0';
  } else {
    nav.style.padding = '14px 0';
  }
});

// ── Movie search / filter ─────────────────────────────────────────────────────
function filterMovies(query) {
  const items = document.querySelectorAll('.movie-item');
  const noResults = document.getElementById('noResults');
  let visible = 0;
  query = query.toLowerCase().trim();

  items.forEach(item => {
    const title = item.dataset.title || '';
    if (!query || title.includes(query)) {
      item.style.display = '';
      visible++;
    } else {
      item.style.display = 'none';
    }
  });

  noResults.classList.toggle('d-none', visible > 0);
}

// ── Set movie from featured card ──────────────────────────────────────────────
function useMovieForReview(title) {
  selectedMovie = title;

  // Update selector
  const selector = document.getElementById('movieSelector');
  for (let i = 0; i < selector.options.length; i++) {
    if (selector.options[i].value === title) {
      selector.selectedIndex = i;
      break;
    }
  }

  updateSelectedBanner(title);

  // Scroll to review section
  document.getElementById('review-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
  setTimeout(() => document.getElementById('reviewInput').focus(), 600);
}

// ── Set movie from dropdown ───────────────────────────────────────────────────
function setMovieTitle(title) {
  selectedMovie = title;
  updateSelectedBanner(title);
}

function updateSelectedBanner(title) {
  const banner = document.getElementById('selectedMovieInfo');
  const titleEl = document.getElementById('selectedMovieTitle');
  if (title) {
    titleEl.textContent = `Menulis review untuk: ${title}`;
    banner.classList.remove('d-none');
  } else {
    banner.classList.add('d-none');
  }
}

// ── Character counter ─────────────────────────────────────────────────────────
function updateCharCount(textarea) {
  const count = textarea.value.length;
  const el = document.getElementById('charCount');
  el.textContent = `${count} / 2000`;
  el.style.color = count > 1800 ? 'var(--accent)' : 'var(--text-muted)';
}

// ── Example reviews ───────────────────────────────────────────────────────────
const EXAMPLES = {
  positive: "This movie was absolutely breathtaking! The storytelling was masterful, the performances were outstanding, and the cinematography left me speechless. Every scene felt purposeful and emotionally resonant. I cannot recommend it highly enough — a true cinematic masterpiece that will stay with me for years.",
  negative: "I was deeply disappointed by this film. The plot was confusing and full of holes, the characters felt flat and unconvincing, and the pacing was painfully slow. The special effects were cheap, and the dialogue was cringe-worthy. A complete waste of time and money."
};

function setExample(type) {
  const textarea = document.getElementById('reviewInput');
  textarea.value = EXAMPLES[type];
  updateCharCount(textarea);
  textarea.focus();
}

function clearReview() {
  const textarea = document.getElementById('reviewInput');
  textarea.value = '';
  updateCharCount(textarea);
  hideResults();
}

// ── Sentiment Analysis (AJAX) ─────────────────────────────────────────────────
async function analyzeSentiment() {
  const textarea = document.getElementById('reviewInput');
  const review = textarea.value.trim();

  // Validation
  if (!review) {
    showError('Harap masukkan teks review terlebih dahulu.');
    return;
  }
  if (review.split(/\s+/).length < 3) {
    showError('Review terlalu pendek. Masukkan minimal 3 kata.');
    return;
  }

  hideResults();
  setLoading(true);

  const startTime = performance.now();

  try {
    const response = await fetch('/api/sentiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ review })
    });

    const elapsed = Math.round(performance.now() - startTime);
    const data = await response.json();

    if (!response.ok) {
      showError(data.error || 'Terjadi kesalahan pada server.');
      return;
    }

    showResult(data, elapsed);

  } catch (err) {
    showError('Tidak dapat menghubungi server. Pastikan Flask berjalan.');
  } finally {
    setLoading(false);
  }
}

// ── UI Helpers ────────────────────────────────────────────────────────────────
function setLoading(isLoading) {
  const btn = document.getElementById('analyzeBtn');
  const inner = btn.querySelector('.btn-analyze-inner');

  if (isLoading) {
    btn.disabled = true;
    inner.innerHTML = '<span class="spinner-ring me-2"></span>Menganalisis...';
  } else {
    btn.disabled = false;
    inner.innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Analisis Sentimen Sekarang';
  }
}

function showResult(data, elapsedMs) {
  const panel = document.getElementById('resultPanel');
  const isPositive = data.sentiment === 'positive';

  // Configure panel class
  panel.classList.remove('positive', 'negative', 'd-none');
  panel.classList.add(isPositive ? 'positive' : 'negative');

  // Icon
  document.getElementById('resultIcon').textContent = isPositive ? '😊' : '😞';

  // Label
  document.getElementById('resultLabel').textContent =
    isPositive ? '✅ Sentimen Positif' : '❌ Sentimen Negatif';

  // Movie info
  const movieEl = document.getElementById('resultMovie');
  movieEl.textContent = selectedMovie ? `Film: ${selectedMovie}` : 'Review umum';

  // Confidence
  const conf = data.confidence;
  document.getElementById('confidenceValue').textContent = `${conf.toFixed(1)}%`;
  const fill = document.getElementById('confidenceFill');
  fill.style.width = '0%';
  setTimeout(() => { fill.style.width = `${conf}%`; }, 50);

  // Meta
  document.getElementById('wordCount').textContent = data.review_length;
  document.getElementById('analysisTime').textContent = `${elapsedMs}ms`;

  // Show panel
  panel.classList.remove('d-none');
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(msg) {
  const errorAlert = document.getElementById('errorAlert');
  document.getElementById('errorMsg').textContent = msg;
  errorAlert.classList.remove('d-none');
  setTimeout(() => errorAlert.classList.add('d-none'), 5000);
}

function hideResults() {
  document.getElementById('resultPanel').classList.add('d-none');
  document.getElementById('errorAlert').classList.add('d-none');
}

// ── Enter key shortcut ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Apply staggered animation delay from data-delay attribute
  document.querySelectorAll('.movie-fadein[data-delay]').forEach(el => {
    el.style.animationDelay = el.dataset.delay + 's';
  });

  // Apply rating bar widths from data-width attribute
  document.querySelectorAll('.rating-fill[data-width]').forEach(el => {
    el.style.width = el.dataset.width + '%';
  });

  document.getElementById('reviewInput').addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      analyzeSentiment();
    }
  });
});
