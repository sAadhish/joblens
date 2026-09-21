// When the UI is hosted by FastAPI at /app/ it shares the same origin.
// For standalone use, override with window.JOBLENS_API_URL or fall back to localhost:8080.
const API = window.JOBLENS_API_URL || (window.location.protocol === 'file:' ? 'http://127.0.0.1:8080' : window.location.origin);

// ──────────────────────── Markdown renderer setup ──────────────────────── //
if (typeof marked !== 'undefined') {
  marked.setOptions({ breaks: true, gfm: true });
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
    return DOMPurify.sanitize(marked.parse(text));
  }
  // Fallback: escape HTML and preserve whitespace
  const escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return `<pre style="white-space:pre-wrap">${escaped}</pre>`;
}
const sessionId = crypto.randomUUID();
const $ = (selector) => document.querySelector(selector);
const messages = $('#messages');
const input = $('#message-input');
const chatForm = $('#chat-form');
const toast = $('#toast');

$('#session-id').textContent = sessionId.slice(0, 18) + '…';

/* ──────────────────────────── Toast ──────────────────────────── */

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.className = `toast show${isError ? ' error' : ''}`;
  setTimeout(() => { toast.className = 'toast'; }, 3600);
}

/* ──────────────────────────── Chat ──────────────────────────── */

function addMessage(kind, content, sources = []) {
  const item = document.createElement('article');
  item.className = `message ${kind}-message`;
  item.innerHTML = `<span class="message-meta">${kind === 'user' ? 'YOU' : 'JOBLENS'}</span><div class="bubble"></div>`;
  const bubble = item.querySelector('.bubble');
  if (kind === 'assistant') {
    bubble.innerHTML = renderMarkdown(content);
  } else {
    bubble.textContent = content;
  }
  if (sources.length) {
    const row = document.createElement('div');
    row.className = 'source-row';
    row.innerHTML = '<span class="source-label">Sources</span>';
    sources.forEach(source => {
      const pill = document.createElement('span');
      pill.className = 'source-pill';
      pill.textContent = source;
      row.appendChild(pill);
    });
    item.appendChild(row);
  }
  messages.appendChild(item);
  item.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function setLoading(loading) {
  chatForm.querySelector('button').disabled = loading;
  if (loading) {
    const loader = document.createElement('article');
    loader.className = 'message assistant-message';
    loader.id = 'typing';
    loader.innerHTML = '<span class="message-meta">JOBLENS IS THINKING</span><div class="typing"><span></span><span></span><span></span></div>';
    messages.appendChild(loader);
    loader.scrollIntoView({ behavior: 'smooth', block: 'end' });
  } else {
    $('#typing')?.remove();
  }
}

async function sendMessage(message) {
  if (!message.trim()) return;
  $('#welcome').hidden = true;
  addMessage('user', message.trim());
  input.value = '';
  input.style.height = 'auto';
  setLoading(true);
  try {
    const response = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message.trim(), session_id: sessionId })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || 'The request could not be completed.');
    addMessage('assistant', body.answer, body.sources || []);
  } catch (error) {
    addMessage('assistant', `I couldn't reach the career service just now. ${error.message}`);
    showToast('Could not connect to the API', true);
  } finally {
    setLoading(false);
    input.focus();
  }
}

chatForm.addEventListener('submit', (e) => { e.preventDefault(); sendMessage(input.value); });
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 160) + 'px'; });
input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); chatForm.requestSubmit(); } });
document.querySelectorAll('.suggestion').forEach(btn => btn.addEventListener('click', () => sendMessage(btn.textContent)));

/* ──────────────────── Knowledge Hub helpers ──────────────────── */

async function refreshCompanies() {
  const list = $('#company-list');
  try {
    const r = await fetch(`${API}/companies`);
    const data = await r.json();
    list.innerHTML = data.companies?.length
      ? data.companies.map(name => `<span>${name}</span>`).join('')
      : '<span class="muted">No job descriptions indexed yet.</span>';
  } catch {
    list.innerHTML = '<span class="muted">Companies will appear here once the API is available.</span>';
  }
}

async function checkApi() {
  const status = $('#api-status');
  const coldStart = $('#cold-start');
  let resolved = false;

  // Show cold-start overlay if health check takes > 3s
  const slowTimer = setTimeout(() => {
    if (!resolved) {
      coldStart.hidden = false;
    }
  }, 3000);

  try {
    const r = await fetch(`${API}/health`);
    const data = await r.json();
    resolved = true;
    clearTimeout(slowTimer);
    coldStart.hidden = true;
    if (data.status === 'healthy') {
      status.classList.add('online');
      status.querySelector('span').textContent = `${data.total_vectors.toLocaleString()} knowledge vectors`;
    } else {
      status.querySelector('span').textContent = 'API is in limited mode';
    }
  } catch {
    resolved = true;
    clearTimeout(slowTimer);
    coldStart.hidden = true;
    status.querySelector('span').textContent = 'API unavailable';
  }
}

/* ── Resume upload (Knowledge Hub) ── */

$('#resume-file').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) $('#file-label').textContent = file.name;
});

$('#resume-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formEl = event.currentTarget;                    // ← capture BEFORE any await
  const file = $('#resume-file').files[0];
  if (!file) return showToast('Choose a PDF resume first.', true);
  const data = new FormData();
  data.append('file', file);
  const button = formEl.querySelector('button');
  button.disabled = true;
  button.textContent = 'Uploading…';
  try {
    const response = await fetch(`${API}/index/resume`, { method: 'POST', body: data });
    const body = await response.json();
    if (!response.ok || !body.success) throw new Error(body.detail || body.message);
    showToast(`Resume added — ${body.chunks_indexed} sections indexed.`);
    formEl.reset();                                      // ← use captured ref (not event.currentTarget)
    $('#file-label').textContent = 'Choose a PDF';
  } catch (error) {
    showToast(error.message || 'Resume upload failed.', true);
  } finally {
    button.disabled = false;
    button.textContent = 'Add resume';
  }
});

/* ── JD indexing (Knowledge Hub) ── */

$('#jd-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formEl = event.currentTarget;                    // ← capture BEFORE any await
  const button = formEl.querySelector('button');
  button.disabled = true;
  button.textContent = 'Indexing…';
  try {
    const response = await fetch(`${API}/index/jd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company: $('#company-input').value.trim(),
        jd_text: $('#jd-input').value.trim()
      })
    });
    const body = await response.json();
    if (!response.ok || !body.success) throw new Error(body.detail || body.message);
    showToast(`Job description added — ${body.chunks_indexed} sections indexed.`);
    formEl.reset();                                      // ← use captured ref
    refreshCompanies();
  } catch (error) {
    showToast(error.message || 'Could not index that description.', true);
  } finally {
    button.disabled = false;
    button.textContent = 'Index job description';
  }
});

/* ──────────────────── View navigation ──────────────────── */

const viewTitles = { chat: 'Career chat', knowledge: 'Knowledge hub', dashboard: 'API Dashboard' };

document.querySelectorAll('[data-view]').forEach(link => link.addEventListener('click', (event) => {
  event.preventDefault();
  const view = link.dataset.view;
  document.querySelectorAll('.nav-link').forEach(item => item.classList.toggle('active', item === link));
  document.querySelectorAll('.view').forEach(item => item.classList.toggle('active-view', item.id === `${view}-view`));
  $('#page-title').textContent = viewTitles[view] || view;
  if (view === 'knowledge') refreshCompanies();
  if (view === 'dashboard') refreshDashboardKPIs();
  $('#sidebar').classList.remove('open');
}));

$('#new-chat').addEventListener('click', () => window.location.reload());
$('#reset-button').addEventListener('click', () => window.location.reload());
$('#menu-button').addEventListener('click', () => $('#sidebar').classList.toggle('open'));

/* ──────────────────── API Dashboard ──────────────────── */

function renderJson(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
  el.classList.add('has-data');
}

function setEndpointLoading(btn, el) {
  btn.disabled = true;
  btn.textContent = 'Loading…';
  el.textContent = '';
  el.classList.remove('has-data');
}

function resetBtn(btn, label) {
  btn.disabled = false;
  btn.textContent = label;
}

/* ──────────────────── KPI Loading ──────────────────── */
async function refreshDashboardKPIs() {
  try {
    const rHealth = await fetch(`${API}/health`);
    const health = await rHealth.json();
    $('#kpi-health-status').textContent = health.status === 'healthy' ? 'Online' : 'Offline';
    $('#kpi-health-status').style.color = health.status === 'healthy' ? '#5fd2a7' : '#e0a644';
    $('#kpi-total-vectors').textContent = health.total_vectors || 0;
  } catch (e) {
    $('#kpi-health-status').textContent = 'Error';
    $('#kpi-health-status').style.color = '#e0a644';
  }

  try {
    const rCompanies = await fetch(`${API}/companies`);
    const companies = await rCompanies.json();
    $('#kpi-total-companies').textContent = (companies.companies || []).filter(c => c).length;
  } catch (e) {
    $('#kpi-total-companies').textContent = 'Error';
  }
}


/* GET /prompts */
$('#btn-prompts')?.addEventListener('click', async () => {
  const btn = $('#btn-prompts'), res = $('#res-prompts');
  setEndpointLoading(btn, res);
  try {
    const r = await fetch(`${API}/prompts`);
    renderJson(res, await r.json());
  } catch (e) { res.textContent = `Error: ${e.message}`; res.classList.add('has-data'); }
  finally { resetBtn(btn, 'Load Prompts'); }
});

/* DELETE /index/jd/{company} */
$('#dash-delete-form')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formEl = event.currentTarget;
  const btn = formEl.querySelector('button');
  const res = $('#res-delete');
  const company = $('#dash-delete-company').value.trim();
  if(!company) return;
  setEndpointLoading(btn, res);
  try {
    const r = await fetch(`${API}/index/jd/${encodeURIComponent(company)}`, { method: 'DELETE' });
    renderJson(res, await r.json());
    formEl.reset();
    showToast(`JD for ${company} deleted`);
    refreshDashboardKPIs(); // Refresh KPIs
  } catch (e) { res.textContent = `Error: ${e.message}`; res.classList.add('has-data'); }
  finally { resetBtn(btn, 'Delete JD'); }
});

/* POST /index/jd (Dashboard) */
$('#dash-jd-form')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formEl = event.currentTarget;
  const btn = formEl.querySelector('button');
  const res = $('#res-jd');
  setEndpointLoading(btn, res);
  try {
    const r = await fetch(`${API}/index/jd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company: $('#dash-company').value.trim(),
        jd_text: $('#dash-jd').value.trim()
      })
    });
    renderJson(res, await r.json());
    formEl.reset();
    showToast('JD indexed successfully');
  } catch (e) { res.textContent = `Error: ${e.message}`; res.classList.add('has-data'); }
  finally { resetBtn(btn, 'Index JD'); }
});

/* POST /index/resume (Dashboard) */
$('#dash-resume-file')?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) $('#dash-file-label').textContent = file.name;
});

$('#dash-resume-form')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formEl = event.currentTarget;
  const btn = formEl.querySelector('button');
  const res = $('#res-resume');
  const file = $('#dash-resume-file').files[0];
  if (!file) return showToast('Choose a PDF first.', true);
  setEndpointLoading(btn, res);
  const data = new FormData();
  data.append('file', file);
  try {
    const r = await fetch(`${API}/index/resume`, { method: 'POST', body: data });
    renderJson(res, await r.json());
    formEl.reset();
    $('#dash-file-label').textContent = 'Choose a PDF';
    showToast('Resume indexed successfully');
  } catch (e) { res.textContent = `Error: ${e.message}`; res.classList.add('has-data'); }
  finally { resetBtn(btn, 'Upload Resume'); }
});

/* ──────────────────── Init ──────────────────── */

checkApi();
