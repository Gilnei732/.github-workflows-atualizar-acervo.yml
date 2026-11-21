(function () {
  const container = document.getElementById('destaques-carousel');
  const statusEl = document.getElementById('destaques-status');
  if (!container) return;

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  fetch('dados/acervo.json?v=' + Date.now())
    .then(function (r) { return r.json(); })
    .then(function (json) {
      const destaques = (Array.isArray(json) ? json : []).filter(function (it) { return it.destaque === true; });
      if (!destaques.length) {
        if (statusEl) statusEl.textContent = 'Nenhum destaque cadastrado no momento.';
        container.innerHTML = '<p class="destaque">Os destaques do acervo aparecerão aqui quando itens forem marcados como destaque.</p>';
        return;
      }
      if (statusEl) statusEl.textContent = destaques.length + ' destaque(s).';

      let idx = 0;
      function show(i) {
        const item = destaques[i];
        const citacao = item.citacao_abnt && item.citacao_abnt.trim()
          ? item.citacao_abnt.trim()
          : ((item.autor || 'AUTOR, Não informado') + '. ' + (item.titulo || 'Título não informado') + '. ' + (item.ano || 's/d') + '.');
        const pdfLink = item.pdf && item.pdf.trim()
          ? '<p><a href="' + escapeHtml(item.pdf) + '" target="_blank" rel="noopener noreferrer">Clique aqui para baixar</a></p>'
          : '<p style="color:#555;"><em>Arquivo não disponível no momento.</em></p>';
        const bibLink = item.link_biblioteca && item.link_biblioteca.trim()
          ? '<p style="font-size:0.85rem;"><a href="' + escapeHtml(item.link_biblioteca) + '" target="_blank" rel="noopener noreferrer">Ver localização na biblioteca</a></p>'
          : '';
        container.innerHTML =
          '<div class="destaque-card">' +
            '<p style="font-size:0.95rem;">' + escapeHtml(citacao) + '</p>' +
            pdfLink + bibLink +
          '</div>' +
          (destaques.length > 1 ? '<div class="destaque-nav">' +
            '<button type="button" id="dest-prev" style="padding:0.4rem 0.8rem; cursor:pointer;">« Anterior</button>' +
            '<span style="margin:0 1rem;">' + (i + 1) + ' / ' + destaques.length + '</span>' +
            '<button type="button" id="dest-next" style="padding:0.4rem 0.8rem; cursor:pointer;">Próximo »</button>' +
          '</div>' : '');
        const prev = document.getElementById('dest-prev');
        const next = document.getElementById('dest-next');
        if (prev) prev.addEventListener('click', function () { idx = (idx - 1 + destaques.length) % destaques.length; show(idx); });
        if (next) next.addEventListener('click', function () { idx = (idx + 1) % destaques.length; show(idx); });
      }
      show(0);
      // auto-rotate every 8s if more than one
      if (destaques.length > 1) {
        setInterval(function () { idx = (idx + 1) % destaques.length; show(idx); }, 8000);
      }
    })
    .catch(function () {
      if (statusEl) statusEl.textContent = 'Não foi possível carregar os destaques.';
    });
})();