function switchTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  btn.classList.add('active');
  document.getElementById('panel-' + name).classList.remove('hidden');
  const input = document.querySelector('#panel-' + name + ' input');
  if (input) input.focus();
}

function lookupAsset() {
  const tag = document.getElementById('tag-input').value.trim();
  if (tag) window.location.href = '/assets/' + encodeURIComponent(tag) + '/preview';
}

function lookupUser() {
  const user = document.getElementById('user-input').value.trim();
  if (user) window.location.href = '/users/' + encodeURIComponent(user) + '/preview';
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
