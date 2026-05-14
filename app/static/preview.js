function switchFormTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  ['panel-checkout', 'panel-return'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  btn.classList.add('active');
  document.getElementById('panel-' + name).classList.remove('hidden');
}

function toggleAll(cb, formType) {
  document.querySelectorAll('.asset-check-' + formType).forEach(c => c.checked = cb.checked);
}

function submitForm(type, fmt) {
  const ids = Array.from(document.querySelectorAll('.asset-check-' + type + ':checked'))
    .map(c => parseInt(c.value));
  if (!ids.length) { alert('Select at least one asset.'); return; }

  const body = { asset_ids: ids };
  if (typeof userId !== 'undefined' && userId !== null) body.user_id = userId;

  const tmpl = localStorage.getItem('doc-template') || 'uwagi';
  const formsBase = (typeof IS_DEMO !== 'undefined' && IS_DEMO)
    ? ROOT_PATH + '/forms/demo/' + type
    : ROOT_PATH + '/forms/' + type;
  fetch(formsBase + '?fmt=' + fmt + '&template=' + encodeURIComponent(tmpl), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  .then(resp => {
    if (!resp.ok) return resp.json().then(d => { throw new Error(d.detail || 'Error'); });
    return resp.blob().then(blob => {
      const url = URL.createObjectURL(blob);
      if (fmt === 'pdf') {
        window.open(url, '_blank');
        setTimeout(() => URL.revokeObjectURL(url), 30000);
      } else {
        const cd = resp.headers.get('Content-Disposition') || '';
        const match = cd.match(/filename="(.+?)"/);
        const filename = match ? match[1] : type + '_form';
        const a = document.createElement('a');
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
      }
    });
  })
  .catch(err => alert('Error: ' + err.message));
}

function printRfid(tag, btn) {
  btn.disabled = true;
  btn.classList.remove('btn-rfid--ok', 'btn-rfid--error');

  fetch(ROOT_PATH + '/rfid/print', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag }),
  })
  .then(resp => resp.json().then(d => {
    if (!resp.ok) throw new Error(d.detail || 'Error');
    btn.classList.add('btn-rfid--ok');
    const status = btn.nextElementSibling;
    if (status && status.classList.contains('rfid-btn-status')) {
      status.textContent = d.printer_response || '✓';
      status.className = 'rfid-btn-status rfid-btn-ok';
    }
  }))
  .catch(err => {
    btn.classList.add('btn-rfid--error');
    const status = btn.nextElementSibling;
    if (status && status.classList.contains('rfid-btn-status')) {
      status.textContent = err.message;
      status.className = 'rfid-btn-status rfid-btn-err';
    }
  })
  .finally(() => { btn.disabled = false; });
}
