function switchTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  btn.classList.add('active');
  document.getElementById('panel-' + name).classList.remove('hidden');
  const input = document.querySelector('#panel-' + name + ' input');
  if (input) input.focus();
}

function lookupAsset() {
  const val = document.getElementById('tag-input').value.trim();
  if (!val) return;

  if (RFID_ENABLED) {
    const m = val.match(/^(\d+)-(\d+)$/);
    if (m) { printRfidRange(m[1], m[2]); return; }
  }

  window.location.href = ROOT_PATH + '/assets/' + encodeURIComponent(val) + '/preview';
}

async function printRfidRange(startTag, endTag) {
  const padLen = Math.max(startTag.length, endTag.length);
  const start = parseInt(startTag, 10);
  const end = parseInt(endTag, 10);
  const total = end - start + 1;

  const status = document.getElementById('rfid-status');

  if (end < start || total > 1000) {
    status.textContent = 'Invalid range (max 1000 tags).';
    status.className = 'rfid-status rfid-error';
    return;
  }

  status.textContent = 'Starting...';
  status.className = 'rfid-status rfid-progress';

  for (let i = start; i <= end; i++) {
    const tag = String(i).padStart(padLen, '0');
    try {
      const resp = await fetch(ROOT_PATH + '/rfid/print', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag }),
      });
      const d = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        status.textContent = `Error at ${tag}: ${d.detail || 'unknown error'}`;
        status.className = 'rfid-status rfid-error';
        return;
      }
      status.textContent = d.mesaj || `Printing ${i - start + 1} / ${total} (${tag})…`;
    } catch (e) {
      status.textContent = `Error at ${tag}: ${e.message}`;
      status.className = 'rfid-status rfid-error';
      return;
    }
    if (i < end) await new Promise(r => setTimeout(r, 100));
  }

  status.textContent = `Done! Printed ${total} tag(s).`;
  status.className = 'rfid-status rfid-done';
}

function lookupUser() {
  const user = document.getElementById('user-input').value.trim();
  if (user) window.location.href = ROOT_PATH + '/users/' + encodeURIComponent(user) + '/preview';
}

function navigateToUser(username) {
  window.location.href = ROOT_PATH + '/users/' + encodeURIComponent(username) + '/preview';
}

(function initUserSearch() {
  let debounceTimer = null;
  let activeIndex = -1;

  function showDropdown(users) {
    const ul = document.getElementById('user-dropdown');
    ul.innerHTML = '';
    activeIndex = -1;
    if (!users.length) { ul.classList.add('hidden'); return; }
    users.forEach((u, i) => {
      const li = document.createElement('li');
      li.className = 'user-dropdown-item';
      li.dataset.username = u.username || '';
      li.innerHTML = `<span class="udd-name">${u.display_name}</span>`
        + (u.username ? `<span class="udd-meta">${u.username}</span>` : '')
        + (u.department ? `<span class="udd-meta">${u.department}</span>` : '');
      li.addEventListener('mousedown', e => {
        e.preventDefault();
        navigateToUser(u.username || String(u.id));
      });
      ul.appendChild(li);
    });
    ul.classList.remove('hidden');
  }

  function hideDropdown() {
    document.getElementById('user-dropdown').classList.add('hidden');
    activeIndex = -1;
  }

  function setActive(items, index) {
    items.forEach(el => el.classList.remove('active'));
    if (index >= 0 && index < items.length) items[index].classList.add('active');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('user-input');

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const q = input.value.trim();
      if (q.length < 2) { hideDropdown(); return; }
      debounceTimer = setTimeout(async () => {
        try {
          const resp = await fetch(ROOT_PATH + '/users/search?q=' + encodeURIComponent(q));
          if (!resp.ok) { hideDropdown(); return; }
          showDropdown(await resp.json());
        } catch { hideDropdown(); }
      }, 280);
    });

    input.addEventListener('keydown', e => {
      const ul = document.getElementById('user-dropdown');
      const items = [...ul.querySelectorAll('.user-dropdown-item')];
      if (ul.classList.contains('hidden') || !items.length) {
        if (e.key === 'Enter') lookupUser();
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        setActive(items, activeIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, -1);
        setActive(items, activeIndex);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIndex >= 0) navigateToUser(items[activeIndex].dataset.username);
        else lookupUser();
      } else if (e.key === 'Escape') {
        hideDropdown();
      }
    });

    input.addEventListener('blur', () => setTimeout(hideDropdown, 150));
  });
}());

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('tag-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') lookupAsset();
  });
  document.getElementById('tag-input').focus();
});
