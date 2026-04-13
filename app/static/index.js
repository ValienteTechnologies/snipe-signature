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
    status.textContent = `Printing ${i - start + 1} / ${total} (${tag})…`;
    try {
      const resp = await fetch(ROOT_PATH + '/rfid/print', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag }),
      });
      if (!resp.ok) {
        const d = await resp.json().catch(() => ({}));
        status.textContent = `Error at ${tag}: ${d.detail || 'unknown error'}`;
        status.className = 'rfid-status rfid-error';
        return;
      }
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

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('tag-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') lookupAsset();
  });
  document.getElementById('user-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') lookupUser();
  });
  document.getElementById('tag-input').focus();
});
