const languageKey = 'west-support-language';
document.querySelectorAll('a[data-language]').forEach(link => {
  link.addEventListener('click', () => {
    const language = link.dataset.language;
    if (language !== 'ko' && language !== 'en') return;
    try { localStorage.setItem(languageKey, language); } catch { /* ordinary links still work */ }
  });
});

// Only the language landing page redirects. Direct policy/support links always open as requested.
if (document.querySelector('[data-language-home]') && !new URL(location.href).searchParams.has('choose-language')) {
  try {
    const language = localStorage.getItem(languageKey);
    if (language === 'ko' || language === 'en') location.replace(new URL(`${language}/support/`, document.baseURI));
  } catch { /* blocked storage keeps the language chooser available */ }
}

document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const area = document.getElementById(button.dataset.copy);
    const status = document.getElementById('copy-status');
    let copied = false;
    try {
      await navigator.clipboard.writeText(area.value);
      copied = true;
    } catch {
      area.focus();
      area.select();
      try { copied = document.execCommand('copy'); } catch { /* selected text remains available */ }
    }
    status.textContent = copied ? button.dataset.success : button.dataset.fallback;
  });
});
