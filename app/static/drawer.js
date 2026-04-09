function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : null;
}

function setCookie(name, val) {
  document.cookie = name + '=' + val + ';path=/;max-age=31536000;SameSite=Lax';
}

function setLang(lang) {
  setCookie('lang', lang);
  location.reload();
}

function setTemplate(tmpl) {
  localStorage.setItem('doc-template', tmpl);
}

document.addEventListener('DOMContentLoaded', () => {
  const langSel = document.getElementById('lang-select');
  if (langSel) langSel.value = getCookie('lang') || 'en';

  const tmplSel = document.getElementById('tmpl-select');
  if (tmplSel) {
    const stored = localStorage.getItem('doc-template');
    if (stored && tmplSel.querySelector('option[value="' + stored + '"]')) {
      tmplSel.value = stored;
    }
    localStorage.setItem('doc-template', tmplSel.value);
  }
});
