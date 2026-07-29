/* Pageantry App — SPA Client */
const API = '';
let tenantId = 1;

function api(path, opts = {}) {
  const headers = { 'X-Tenant-ID': tenantId, ...opts.headers };
  if (!(opts.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  return fetch(`${API}${path}`, { ...opts, headers })
    .then(r => r.ok ? r.json().catch(() => ({})) : r.json().then(e => { throw new Error(e.detail || 'Request failed'); }));
}

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById(`page-${name}`);
  if (page) page.classList.add('active');
  // Load data
  switch(name) {
    case 'dashboard': loadDashboard(); break;
    case 'pageants': loadPageants(); break;
    case 'contestants': loadContestantFilters(); break;
    case 'scoring': loadScoringFilters(); break;
    case 'venues': loadVenues(); break;
    case 'sponsors': loadSponsorFilters(); break;
    case 'marketing': loadMarketingFilters(); break;
    case 'titleholders': loadTitleholderFilters(); break;
    case 'finances': loadFinanceFilters(); break;
  }
}

// ── Dashboard ────────────────────────────────────────────────────────

function loadDashboard() {
  api('/pageants').then(pageants => {
    document.getElementById('stat-pageants').textContent = pageants.length;
    let contestants = 0, checkedIn = 0, sponsors = 0, revenue = 0, expenses = 0;
    return Promise.all(pageants.map(p =>
      api(`/pageants/${p.id}/financial-summary`).then(f => {
        revenue += f.total_revenue || 0; expenses += f.total_expenses || 0;
      }).catch(() => {})
      .then(() => api(`/pageants/${p.id}/contestants`).then(c => {
        contestants += c.length;
        checkedIn += c.filter(x => x.status === 'checked_in').length;
      }).catch(() => {}))
      .then(() => api(`/pageants/${p.id}/sponsors`).then(s => {
        sponsors += s.length;
      }).catch(() => {}))
    )).then(() => {
      document.getElementById('stat-contestants').textContent = contestants;
      document.getElementById('stat-checked-in').textContent = checkedIn;
      document.getElementById('stat-sponsors').textContent = sponsors;
      document.getElementById('stat-revenue').textContent = `$${revenue.toFixed(0)}`;
      document.getElementById('stat-expenses').textContent = `$${expenses.toFixed(0)}`;
    });
  }).catch(() => {});
}

// ── Pageants ─────────────────────────────────────────────────────────

function loadPageants() {
  api('/pageants').then(pageants => {
    const el = document.getElementById('pageant-list');
    if (!pageants.length) { el.innerHTML = '<div class="card"><p class="text-muted">No pageants yet. Create one to get started.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Created</th><th></th></tr></thead><tbody>
      ${pageants.map(p => `<tr>
        <td><strong>${p.name}</strong><br><small class="text-muted">${p.slug}</small></td>
        <td><span class="badge ${p.pageant_type === 'representative' ? 'badge-active' : 'badge-pending'}">${p.pageant_type}</span></td>
        <td><span class="badge badge-${p.status}">${p.status}</span></td>
        <td>${new Date(p.created_at).toLocaleDateString()}</td>
        <td><button onclick="viewPageant(${p.id})" class="btn btn-sm">View</button></td>
      </tr>`).join('')}</tbody></table>`;
  });
}

function viewPageant(id) {
  api(`/pageants/${id}`).then(p => {
    const el = document.getElementById('pageant-list');
    el.innerHTML = `<div class="detail-panel">
      <h4>${p.name}</h4>
      <div class="detail-grid">
        <span class="label">Slug:</span><span>${p.slug}</span>
        <span class="label">Type:</span><span>${p.pageant_type}</span>
        <span class="label">Status:</span><span><span class="badge badge-${p.status}">${p.status}</span></span>
        <span class="label">Mission:</span><span>${p.mission_statement || '—'}</span>
        <span class="label">Business:</span><span>${p.business_structure || '—'}</span>
      </div>
      <div class="mt-1">
        <button onclick="api('/pageants/${p.id}', {method:'PATCH',body:JSON.stringify({status:'active'})}).then(()=>viewPageant(${p.id}))" class="btn btn-sm btn-success">Activate</button>
        <button onclick="loadPageants()" class="btn btn-sm">Back</button>
      </div>
    </div>`;
  });
}

function showPageantForm() { document.getElementById('pageant-form').style.display = 'block'; }
function hidePageantForm() { document.getElementById('pageant-form').style.display = 'none'; }

function createPageant() {
  const data = {
    name: document.getElementById('p-name').value,
    slug: document.getElementById('p-slug').value,
    pageant_type: document.getElementById('p-type').value,
    mission_statement: document.getElementById('p-mission').value
  };
  api('/pageants', { method: 'POST', body: JSON.stringify(data) }).then(() => {
    hidePageantForm();
    document.getElementById('p-name').value = '';
    document.getElementById('p-slug').value = '';
    document.getElementById('p-mission').value = '';
    loadPageants();
  }).catch(e => alert(e.message));
}

// ── Contestants ──────────────────────────────────────────────────────

function loadContestantFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('c-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    loadContestants();
  });
}

function loadContestants() {
  const pid = document.getElementById('c-pageant-filter').value;
  if (!pid) { document.getElementById('contestant-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/contestants`).then(contestants => {
    const el = document.getElementById('contestant-list');
    if (!contestants.length) { el.innerHTML = '<div class="card"><p class="text-muted">No contestants registered.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>#</th><th>Name</th><th>Age</th><th>Status</th><th>Checked In</th><th></th></tr></thead><tbody>
      ${contestants.map(c => `<tr>
        <td>${c.contestant_number || '—'}</td>
        <td><strong>${c.first_name} ${c.last_name}</strong></td>
        <td>${c.age || '—'}</td>
        <td><span class="badge badge-${c.status}">${c.status}</span></td>
        <td>${c.checked_in_at ? new Date(c.checked_in_at).toLocaleTimeString() : '—'}</td>
        <td>
          <button onclick="checkInContestant(${c.id})" class="btn btn-sm btn-success" ${c.status === 'checked_in' ? 'disabled' : ''}>Check In</button>
        </td>
      </tr>`).join('')}</tbody></table>`;
  });
}

function showContestantForm() {
  const pid = document.getElementById('c-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  // Load divisions
  api(`/pageants/${pid}/divisions`).then(divs => {
    const sel = document.getElementById('c-division');
    sel.innerHTML = '<option value="">Select division</option>' + divs.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  });
  document.getElementById('contestant-form').style.display = 'block';
}
function hideContestantForm() { document.getElementById('contestant-form').style.display = 'none'; }

function registerContestant() {
  const pid = document.getElementById('c-pageant-filter').value;
  const data = {
    division_id: parseInt(document.getElementById('c-division').value),
    first_name: document.getElementById('c-first').value,
    last_name: document.getElementById('c-last').value,
    age: parseInt(document.getElementById('c-age').value) || null,
    email: document.getElementById('c-email').value,
    phone: document.getElementById('c-phone').value
  };
  api(`/pageants/${pid}/contestants`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    hideContestantForm();
    ['c-first','c-last','c-age','c-email','c-phone'].forEach(id => document.getElementById(id).value = '');
    loadContestants();
  }).catch(e => alert(e.message));
}

function checkInContestant(id) {
  api(`/contestants/${id}/check-in`, { method: 'POST' }).then(() => loadContestants());
}

// ── Scoring ──────────────────────────────────────────────────────────

function loadScoringFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('s-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    loadScoringPanels();
  });
}

function loadScoringPanels() {
  const pid = document.getElementById('s-pageant-filter').value;
  if (!pid) { document.getElementById('panel-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/panels`).then(panels => {
    const el = document.getElementById('panel-list');
    if (!panels.length) { el.innerHTML = '<div class="card"><p class="text-muted">No judge panels yet.</p></div>'; return; }
    el.innerHTML = panels.map(p => `<div class="card">
      <h3>${p.name || 'Panel #' + p.id} ${p.head_judge_id ? '<span class="badge badge-active">Head Judge Assigned</span>' : ''}</h3>
      <div>Judges: ${p.judges ? p.judges.map(j => `${j.first_name} ${j.last_name}${j.is_head_judge ? ' (Head)' : ''}`).join(', ') : 'None'}</div>
      <div class="mt-1">
        <button onclick="showScoreEntry(${pid}, ${p.id})" class="btn btn-sm btn-primary">Enter Scores</button>
        <button onclick="runTabulation(${pid})" class="btn btn-sm btn-success">Tabulate</button>
      </div>
    </div>`).join('');
  });
}

function showPanelForm() { document.getElementById('panel-form').style.display = 'block'; }
function hidePanelForm() { document.getElementById('panel-form').style.display = 'none'; }

function addJudgeRow() {
  const div = document.createElement('div');
  div.className = 'judge-row';
  div.innerHTML = '<input placeholder="First Name" class="jf"><input placeholder="Last Name" class="jl"><input placeholder="Email" class="je">';
  document.getElementById('judge-inputs').appendChild(div);
}

function createPanel() {
  const pid = document.getElementById('s-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  const name = document.getElementById('panel-name').value;
  const judges = Array.from(document.querySelectorAll('.judge-row')).map(row => ({
    first_name: row.querySelector('.jf').value,
    last_name: row.querySelector('.jl').value,
    email: row.querySelector('.je').value
  })).filter(j => j.first_name && j.last_name);

  api(`/pageants/${pid}/panels`, { method: 'POST', body: JSON.stringify({ name, judges }) }).then(() => {
    hidePanelForm();
    document.getElementById('panel-name').value = '';
    document.querySelectorAll('.judge-row').forEach((r,i) => { if (i > 0) r.remove(); });
    loadScoringPanels();
  }).catch(e => alert(e.message));
}

function showScoreEntry(pid, panelId) {
  // Load categories and contestants
  Promise.all([
    api(`/pageants/${pid}/divisions`).then(divs => {
      const cats = [];
      return Promise.all(divs.map(d => api(`/pageants/${pid}/divisions/${d.id}/categories`).then(c => cats.push(...c)))).then(() => cats);
    }),
    api(`/pageants/${pid}/contestants`),
    api(`/pageants/${pid}/panels`).then(panels => {
      const p = panels.find(x => x.id === panelId);
      return p ? p.judges || [] : [];
    })
  ]).then(([categories, contestants, judges]) => {
    const catSel = document.getElementById('score-category');
    catSel.innerHTML = '<option value="">Select category</option>' + categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    const conSel = document.getElementById('score-contestant');
    conSel.innerHTML = '<option value="">Select contestant</option>' + contestants.map(c => `<option value="${c.id}">${c.first_name} ${c.last_name}</option>`).join('');
    const jSel = document.getElementById('score-judge');
    jSel.innerHTML = '<option value="">Select judge</option>' + judges.map(j => `<option value="${j.id}">${j.first_name} ${j.last_name}</option>`).join('');
    document.getElementById('score-entry').dataset.pid = pid;
    document.getElementById('score-entry').style.display = 'block';
  });
}

function submitScore() {
  const pid = document.getElementById('score-entry').dataset.pid;
  const data = {
    contestant_id: parseInt(document.getElementById('score-contestant').value),
    judge_id: parseInt(document.getElementById('score-judge').value),
    category_id: parseInt(document.getElementById('score-category').value),
    score_value: parseFloat(document.getElementById('score-value').value),
    comment: document.getElementById('score-comment').value || null
  };
  api(`/pageants/${pid}/scores`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    document.getElementById('score-value').value = '';
    document.getElementById('score-comment').value = '';
    alert('Score submitted');
  }).catch(e => alert(e.message));
}

function runTabulation(pid) {
  api(`/pageants/${pid}/divisions`).then(divs => {
    return Promise.all(divs.map(d => api(`/pageants/${pid}/tabulate/${d.id}`, { method: 'POST' }).catch(() => {})));
  }).then(() => {
    api(`/pageants/${pid}/results`).then(results => {
      if (!results || !results.length) { alert('No results generated'); return; }
      const report = results.map(r => `#${r.rank} ${r.contestant_name} — ${r.total_score?.toFixed(1)} ${r.is_winner ? '👑' : r.is_runner_up ? '🥈' : ''}`).join('\n');
      alert('Results:\n' + report);
    });
  }).catch(e => alert(e.message));
}

// ── Venues ───────────────────────────────────────────────────────────

function loadVenues() {
  api('/venues').then(venues => {
    const el = document.getElementById('venue-list');
    if (!venues.length) { el.innerHTML = '<div class="card"><p class="text-muted">No venues yet.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Name</th><th>Capacity</th><th>Stage</th><th></th></tr></thead><tbody>
      ${venues.map(v => `<tr>
        <td><strong>${v.name}</strong></td>
        <td>${v.capacity || '—'}</td>
        <td>${v.has_built_in_stage ? '✅' : '❌'}</td>
        <td><button onclick="viewVenue(${v.id})" class="btn btn-sm">View</button></td>
      </tr>`).join('')}</tbody></table>`;
  });
}

function viewVenue(id) {
  api(`/venues/${id}`).then(v => {
    const el = document.getElementById('venue-list');
    el.innerHTML = `<div class="detail-panel">
      <h4>${v.name}</h4>
      <div class="detail-grid">
        <span class="label">Address:</span><span>${v.address || '—'}</span>
        <span class="label">Contact:</span><span>${v.contact_name || '—'} ${v.contact_phone ? '| ' + v.contact_phone : ''}</span>
        <span class="label">Capacity:</span><span>${v.capacity || '—'}</span>
        <span class="label">Stage:</span><span>${v.stage_dimensions || '—'} ${v.has_built_in_stage ? '(built-in)' : ''}</span>
        <span class="label">Parking:</span><span>${v.parking_info || '—'}</span>
      </div>
      <button onclick="loadVenues()" class="btn btn-sm mt-1">Back</button>
    </div>`;
  });
}

function showVenueForm() { document.getElementById('venue-form').style.display = 'block'; }
function hideVenueForm() { document.getElementById('venue-form').style.display = 'none'; }

function createVenue() {
  const data = {
    name: document.getElementById('v-name').value,
    address: document.getElementById('v-address').value,
    capacity: parseInt(document.getElementById('v-capacity').value) || null,
    contact_name: document.getElementById('v-contact').value,
    contact_phone: document.getElementById('v-phone').value,
    contact_email: document.getElementById('v-email').value
  };
  api('/venues', { method: 'POST', body: JSON.stringify(data) }).then(() => {
    hideVenueForm();
    ['v-name','v-address','v-capacity','v-contact','v-phone','v-email'].forEach(id => document.getElementById(id).value = '');
    loadVenues();
  }).catch(e => alert(e.message));
}

// ── Sponsors ─────────────────────────────────────────────────────────

function loadSponsorFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('sp-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    if (pageants.length) {
      const pbSel = document.getElementById('pb-pageant-filter');
      pbSel.innerHTML = pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    }
    loadSponsors();
  });
}

function loadSponsors() {
  const pid = document.getElementById('sp-pageant-filter').value;
  if (!pid) { document.getElementById('sponsor-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/sponsors`).then(sponsors => {
    const el = document.getElementById('sponsor-list');
    if (!sponsors.length) { el.innerHTML = '<div class="card"><p class="text-muted">No sponsors yet.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Business</th><th>Contact</th><th>Email</th></tr></thead><tbody>
      ${sponsors.map(s => `<tr><td><strong>${s.business_name}</strong></td><td>${s.contact_name || '—'}</td><td>${s.contact_email || '—'}</td></tr>`).join('')}</tbody></table>`;
  });
}

function showSponsorForm() {
  const pid = document.getElementById('sp-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  document.getElementById('sponsor-form').style.display = 'block';
}
function hideSponsorForm() { document.getElementById('sponsor-form').style.display = 'none'; }

function createSponsor() {
  const pid = document.getElementById('sp-pageant-filter').value;
  const data = {
    business_name: document.getElementById('sp-business').value,
    contact_name: document.getElementById('sp-contact').value,
    contact_email: document.getElementById('sp-email').value,
    contact_phone: document.getElementById('sp-phone').value,
    website: document.getElementById('sp-website').value
  };
  api(`/pageants/${pid}/sponsors`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    hideSponsorForm();
    ['sp-business','sp-contact','sp-email','sp-phone','sp-website'].forEach(id => document.getElementById(id).value = '');
    loadSponsors();
  }).catch(e => alert(e.message));
}

function showDonationForm() { document.getElementById('donation-form').style.display = 'block'; }

function recordDonation() {
  const pid = document.getElementById('sp-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  const data = {
    donor_name: document.getElementById('d-name').value,
    amount: parseFloat(document.getElementById('d-amount').value) || null,
    in_kind_description: document.getElementById('d-kind').value || null
  };
  api(`/pageants/${pid}/donations`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    document.getElementById('d-name').value = '';
    document.getElementById('d-amount').value = '';
    document.getElementById('d-kind').value = '';
    document.getElementById('donation-form').style.display = 'none';
    alert('Donation recorded');
  });
}

// ── Marketing ────────────────────────────────────────────────────────

function loadMarketingFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('m-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    loadCampaigns();
  });
}

function loadCampaigns() {
  const pid = document.getElementById('m-pageant-filter').value;
  if (!pid) { document.getElementById('campaign-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/campaigns`).then(campaigns => {
    const el = document.getElementById('campaign-list');
    if (!campaigns.length) { el.innerHTML = '<div class="card"><p class="text-muted">No campaigns yet.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Budget</th></tr></thead><tbody>
      ${campaigns.map(c => `<tr><td><strong>${c.name}</strong></td><td>${c.campaign_type}</td><td><span class="badge badge-${c.status}">${c.status}</span></td><td>${c.budget ? '$' + c.budget : '—'}</td></tr>`).join('')}</tbody></table>`;
  });
}

function showCampaignForm() { document.getElementById('campaign-form').style.display = 'block'; }

function createCampaign() {
  const pid = document.getElementById('m-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  const data = {
    name: document.getElementById('camp-name').value,
    campaign_type: document.getElementById('camp-type').value,
    start_date: document.getElementById('camp-start').value || null,
    budget: parseFloat(document.getElementById('camp-budget').value) || null
  };
  api(`/pageants/${pid}/campaigns`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    document.getElementById('camp-name').value = '';
    document.getElementById('camp-budget').value = '';
    document.getElementById('campaign-form').style.display = 'none';
    loadCampaigns();
  }).catch(e => alert(e.message));
}

function createProgramBook() {
  const pid = document.getElementById('pb-pageant-filter').value;
  if (!pid) { alert('Select a pageant'); return; }
  api(`/pageants/${pid}/program-book`, { method: 'POST', body: JSON.stringify({}) }).then(() => {
    api(`/pageants/${pid}/program-book`).then(pb => {
      document.getElementById('program-book-info').innerHTML = `<div class="detail-panel">
        <h4>Program Book</h4>
        <div>Format: ${pb.format} | Distribution: ${pb.distribution_strategy}</div>
      </div>`;
    });
    api(`/pageants/${pid}/ads`).then(ads => {
      document.getElementById('ad-list').innerHTML = ads.length ? `<table><thead><tr><th>Advertiser</th><th>Size</th><th>Fee</th><th>Status</th></tr></thead><tbody>
        ${ads.map(a => `<tr><td>${a.advertiser_name}</td><td>${a.ad_size}</td><td>$${a.fee}</td><td>${a.status}</td></tr>`).join('')}</tbody></table>` : '';
    });
  }).catch(e => alert(e.message));
}

// ── Titleholders ─────────────────────────────────────────────────────

function loadTitleholderFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('t-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    loadTitleholders();
  });
}

function loadTitleholders() {
  const pid = document.getElementById('t-pageant-filter').value;
  if (!pid) { document.getElementById('titleholder-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/titleholders`).then(holders => {
    const el = document.getElementById('titleholder-list');
    if (!holders.length) { el.innerHTML = '<div class="card"><p class="text-muted">No titleholders yet. Crown winners to create them.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Title</th><th>Contestant</th><th>Reign Start</th><th>Status</th></tr></thead><tbody>
      ${holders.map(h => `<tr><td><strong>${h.title || '—'}</strong></td><td>#${h.contestant_id}</td><td>${h.reign_start_date}</td><td><span class="badge badge-${h.status}">${h.status}</span></td></tr>`).join('')}</tbody></table>`;
  });
}

// ── Finances ─────────────────────────────────────────────────────────

function loadFinanceFilters() {
  api('/pageants').then(pageants => {
    const sel = document.getElementById('f-pageant-filter');
    sel.innerHTML = '<option value="">Select pageant</option>' + pageants.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    loadBudget();
  });
}

function loadBudget() {
  const pid = document.getElementById('f-pageant-filter').value;
  if (!pid) { document.getElementById('budget-list').innerHTML = ''; return; }
  api(`/pageants/${pid}/financial-summary`).then(f => {
    document.getElementById('fin-revenue').textContent = `$${(f.total_revenue || 0).toFixed(0)}`;
    document.getElementById('fin-expenses').textContent = `$${(f.total_expenses || 0).toFixed(0)}`;
    document.getElementById('fin-net').textContent = `$${((f.total_revenue || 0) - (f.total_expenses || 0)).toFixed(0)}`;
  });
  api(`/pageants/${pid}/budget`).then(items => {
    const el = document.getElementById('budget-list');
    if (!items.length) { el.innerHTML = '<div class="card"><p class="text-muted">No budget items yet.</p></div>'; return; }
    el.innerHTML = `<table><thead><tr><th>Category</th><th>Description</th><th>Estimated</th><th>Actual</th><th>Status</th></tr></thead><tbody>
      ${items.map(i => `<tr><td><span class="badge badge-pending">${i.category}</span></td><td>${i.description}</td><td>${i.estimated_cost ? '$' + i.estimated_cost : '—'}</td><td>${i.actual_cost ? '$' + i.actual_cost : '—'}</td><td>${i.status}</td></tr>`).join('')}</tbody></table>`;
  });
}

function showBudgetForm() {
  const pid = document.getElementById('f-pageant-filter').value;
  if (!pid) { alert('Select a pageant first'); return; }
  document.getElementById('budget-form').style.display = 'block';
}

function createBudgetItem() {
  const pid = document.getElementById('f-pageant-filter').value;
  const data = {
    category: document.getElementById('b-cat').value,
    description: document.getElementById('b-desc').value,
    estimated_cost: parseFloat(document.getElementById('b-estimated').value) || null,
    vendor_name: document.getElementById('b-vendor').value || null
  };
  api(`/pageants/${pid}/budget`, { method: 'POST', body: JSON.stringify(data) }).then(() => {
    document.getElementById('b-desc').value = '';
    document.getElementById('b-estimated').value = '';
    document.getElementById('b-vendor').value = '';
    document.getElementById('budget-form').style.display = 'none';
    loadBudget();
  }).catch(e => alert(e.message));
}

// ── Init ─────────────────────────────────────────────────────────────

loadDashboard();