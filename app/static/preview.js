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
  fetch('/forms/' + type + '?fmt=' + fmt + '&template=' + encodeURIComponent(tmpl), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  .then(resp => {
    if (!resp.ok) return resp.json().then(d => { throw new Error(d.detail || 'Error'); });
    return resp.blob().then(blob => {
      const cd = resp.headers.get('Content-Disposition') || '';
      const match = cd.match(/filename="(.+?)"/);
      const filename = match ? match[1] : type + '_form';
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    });
  })
  .catch(err => alert('Error: ' + err.message));
}
