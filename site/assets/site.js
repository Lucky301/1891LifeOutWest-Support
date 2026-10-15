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
