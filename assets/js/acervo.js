(function () {
  const container = document.getElementById('acervo-lista');
  const statusEl = document.getElementById('acervo-status');
  const buscaInput = document.getElementById('acervo-busca');
  const tipoSelect = document.getElementById('acervo-tipo');
  const instSelect = document.getElementById('acervo-instituicao');
  const anoSelect = document.getElementById('acervo-ano');
  const btnLimpar = document.getElementById('acervo-limpar');
  const pagDiv = document.getElementById('acervo-paginacao');

  const PAGE_SIZE = 20;
  let currentPage = 1;
  let filteredCache = [];
  let showAllMode = false;

  if (!container || !statusEl) return;
  const tipoLabels = {
    tese: 'Tese',
    dissertacao: 'Dissertação',
    tcc: 'TCC',
    monografia: 'Monografia',
    artigo: 'Artigo',
    outro: 'Outro'
  };

  let dados = [];
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  function sortKey(item) {
    const cit = (item.citacao_abnt || '').trim();
    const autor = (item.autor || '').trim();
    const base = cit || autor || (item.titulo || '');
    return base.toLowerCase();
  }

  function render(items) {
    if (!items.length) {
      container.innerHTML = '<p class="destaque">Nenhum registro encontrado com os filtros atuais. Ajuste a busca ou os filtros.</p>';
      statusEl.textContent = '0 registro(s) exibido(s).';
      if (pagDiv) pagDiv.innerHTML = '';
      return;
    }
    statusEl.textContent = items.length + ' registro(s) exibido(s).';
    // paginate
    const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;
    const start = (currentPage - 1) * PAGE_SIZE;
    const pageItems = items.slice(start, start + PAGE_SIZE);

    let htmlStr = '';
    for (let i = 0; i < pageItems.length; i++) {
      const item = pageItems[i];
      const citacao = item.citacao_abnt && item.citacao_abnt.trim()
        ? item.citacao_abnt.trim()
        : ((item.autor || 'AUTOR, Não informado') + '. ' + (item.titulo || 'Título não informado') + '. ' + (item.ano || 's/d') + '.');
      const pdfLink = item.pdf && item.pdf.trim()
        ? '<a href="' + escapeHtml(item.pdf) + '" target="_blank" rel="noopener noreferrer" style="margin-right:1rem;">Clique aqui para baixar</a>'
        : '<span style="color:#555; margin-right:1rem;"><em>Arquivo não disponível no momento.</em></span>';
      const bibLink = item.link_biblioteca && item.link_biblioteca.trim()
        ? '<a href="' + escapeHtml(item.link_biblioteca) + '" target="_blank" rel="noopener noreferrer" style="margin-right:1rem;">Ver localização na biblioteca</a>'
        : '';
      const shareUrl = window.location.origin + window.location.pathname.replace('repositorio.html','') + 'repositorio.html?q=' + encodeURIComponent(item.titulo || '');
      const shareText = encodeURIComponent(citacao + (item.pdf ? ' ' + item.pdf : ''));
      const shareLinks =
        '<a href="#" data-share="copy" data-url="' + escapeHtml(shareUrl) + '" style="margin-right:1rem;">Copiar link</a>' +
        '<a href="https://wa.me/?text=' + shareText + '" target="_blank" rel="noopener" style="margin-right:1rem;">WhatsApp</a>';
      htmlStr += '<article class="card fade-in" style="margin-bottom:1rem;">' +
        '<p style="margin:0; font-size:0.95rem;">' + escapeHtml(citacao) + '</p>' +
        '<p style="margin-top:0.6rem; font-size:0.9rem;">' + pdfLink + bibLink + shareLinks + '</p>' +
        '</article>';
    }
    container.innerHTML = htmlStr;
    renderPaginacao(totalPages);
  }

  function renderPaginacao(totalPages) {
    if (!pagDiv) return;
    if (totalPages <= 1) { pagDiv.innerHTML = ''; return; }
    let html = '';
    html += '<button type="button" data-page="prev" style="padding:0.4rem 0.8rem; margin:0 0.2rem; cursor:pointer;"' + (currentPage <= 1 ? ' disabled' : '') + '>« Anterior</button>';
    // page numbers (show window)
    const windowSize = 5;
    let startP = Math.max(1, currentPage - 2);
    let endP = Math.min(totalPages, startP + windowSize - 1);
    if (endP - startP < windowSize - 1) startP = Math.max(1, endP - windowSize + 1);
    if (startP > 1) html += '<button type="button" data-page="1" style="padding:0.4rem 0.7rem; margin:0 0.1rem; cursor:pointer;">1</button>';
    if (startP > 2) html += '<span style="margin:0 0.3rem;">…</span>';
    for (let p = startP; p <= endP; p++) {
      html += '<button type="button" data-page="' + p + '" style="padding:0.4rem 0.7rem; margin:0 0.1rem; cursor:pointer;' + (p === currentPage ? ' background:#2c3e50; color:#fff;' : '') + '">' + p + '</button>';
    }
    if (endP < totalPages - 1) html += '<span style="margin:0 0.3rem;">…</span>';
    if (endP < totalPages) html += '<button type="button" data-page="' + totalPages + '" style="padding:0.4rem 0.7rem; margin:0 0.1rem; cursor:pointer;">' + totalPages + '</button>';
    html += '<button type="button" data-page="next" style="padding:0.4rem 0.8rem; margin:0 0.2rem; cursor:pointer;"' + (currentPage >= totalPages ? ' disabled' : '') + '>Próxima »</button>';
    pagDiv.innerHTML = html;
    // bind
    pagDiv.querySelectorAll('button[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const val = btn.getAttribute('data-page');
        if (val === 'prev') currentPage--;
        else if (val === 'next') currentPage++;
        else currentPage = parseInt(val, 10);
        render(filteredCache);
        window.scrollTo({ top: container.offsetTop - 80, behavior: 'smooth' });
      });
    });
  }

  function aplicarFiltros() {
    const q = (buscaInput && buscaInput.value ? buscaInput.value : '').trim().toLowerCase();
    const tipo = tipoSelect && tipoSelect.value ? tipoSelect.value : '';
    const inst = instSelect && instSelect.value ? instSelect.value : '';
    const ano = anoSelect && anoSelect.value ? anoSelect.value : '';

    // Modo inicial: nenhum item exibido ate o usuario buscar ou clicar em "Mostrar todos"
    const hasFilter = q || tipo || inst || ano;
    if (!hasFilter && !showAllMode) {
      filteredCache = [];
      container.innerHTML = '<p class="destaque">Digite um termo na busca ou use os filtros para consultar o acervo. Ou clique em <strong>Mostrar todos os registros</strong> para listar todos (' + dados.length + ' itens).</p>';
      statusEl.textContent = 'Nenhum registro exibido. Use a busca ou os filtros.';
      if (pagDiv) pagDiv.innerHTML = '';
      return;
    }

    const filtrados = dados.filter(function (item) {
      const matchTipo = !tipo || item.tipo === tipo;
      const matchInst = !inst || item.instituicao === inst;
      const matchAno = !ano || String(item.ano) === ano;
      if (!matchTipo || !matchInst || !matchAno) return false;
      if (!q) return true;
      const texto = [
        item.titulo,
        item.autor,
        item.instituicao,
        item.nucleo,
        item.regiao,
        item.tema,
        item.resumo
      ].map(function (v) { return (v || '').toLowerCase(); }).join(' ');
      return texto.indexOf(q) !== -1;
    });

    filtrados.sort(function (a, b) {
      const ka = (a.citacao_abnt || a.autor || a.titulo || '').toLowerCase();
      const kb = (b.citacao_abnt || b.autor || b.titulo || '').toLowerCase();
      if (ka < kb) return -1;
      if (ka > kb) return 1;
      return 0;
    });

    filteredCache = filtrados;
    currentPage = 1;
    render(filteredCache);
    if (typeof window.observeFadeIn === 'function') window.observeFadeIn();
  }

  function preencherAnos(lista) {
    if (!anoSelect) return;
    const anos = Array.from(new Set(lista.map(function (d) { return d.ano; }).filter(Boolean)));
    anos.sort(function (a, b) { return b - a; });
    anos.forEach(function (a) {
      const opt = document.createElement('option');
      opt.value = String(a);
      opt.textContent = String(a);
      anoSelect.appendChild(opt);
    });
  }

  function preencherInstituicoes(lista) {
    if (!instSelect) return;
    const insts = Array.from(new Set(lista.map(function (d) { return d.instituicao; }).filter(Boolean)));
    insts.sort();
    insts.forEach(function (inst) {
      const opt = document.createElement('option');
      opt.value = inst;
      opt.textContent = inst;
      instSelect.appendChild(opt);
    });
  }

  fetch('dados/acervo.json')
    .then(function (r) {
      if (!r.ok) throw new Error('Erro ao carregar acervo.');
      return r.json();
    })
    .then(function (json) {
      dados = Array.isArray(json) ? json : [];
      preencherAnos(dados);
      preencherInstituicoes(dados);
      // Global search via URL param ?q=
      try {
        const params = new URLSearchParams(window.location.search);
        const q = params.get('q');
        if (q && buscaInput) buscaInput.value = q;
      } catch (e) {}
      aplicarFiltros();
      renderStats(dados);
    })
    .catch(function () {
      statusEl.textContent = 'Não foi possível carregar o acervo (dados/acervo.json).';
      container.innerHTML = '<p class="destaque">O arquivo de dados não foi encontrado ou não pôde ser lido. Se você abriu o site apenas clicando no arquivo (file://), alguns navegadores bloqueiam o carregamento. Use um servidor local (ex.: extensão Live Server) ou publique o site.</p>';
    });

  function renderStats(dados) {
    var el = document.getElementById('stats-total');
    if (el) el.textContent = dados.length;
    if (typeof Chart === 'undefined') return;
    // Tipo
    const tipoCounts = {};
    dados.forEach(function (d) { const t = d.tipo || 'outro'; tipoCounts[t] = (tipoCounts[t] || 0) + 1; });
    const tipoLabels = Object.keys(tipoCounts);
    const tipoData = tipoLabels.map(function (t) { return tipoCounts[t]; });
    const tipoColors = ['#2c3e50','#3498db','#e74c3c','#f39c12','#2ecc71','#9b59b6'];
    new Chart(document.getElementById('chart-tipo'), {
      type: 'doughnut',
      data: { labels: tipoLabels.map(function(t){return t.charAt(0).toUpperCase()+t.slice(1);}), datasets: [{ data: tipoData, backgroundColor: tipoColors }] },
      options: { responsive: true, plugins: { title: { display: true, text: 'Por tipo' }, legend: { position: 'bottom' } } }
    });
    // Ano (top 15)
    const anoCounts = {};
    dados.forEach(function (d) { if (d.ano) anoCounts[d.ano] = (anoCounts[d.ano] || 0) + 1; });
    const anos = Object.keys(anoCounts).sort().slice(-15);
    new Chart(document.getElementById('chart-ano'), {
      type: 'bar',
      data: { labels: anos, datasets: [{ label: 'Registros', data: anos.map(function(a){return anoCounts[a];}), backgroundColor: '#3498db' }] },
      options: { responsive: true, plugins: { title: { display: true, text: 'Por ano (últimos 15)' }, legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });
    // Instituição (top 8)
    const instCounts = {};
    dados.forEach(function (d) { const inst = d.instituicao || 'Não informado'; instCounts[inst] = (instCounts[inst] || 0) + 1; });
    const insts = Object.keys(instCounts).sort(function(a,b){return instCounts[b]-instCounts[a];}).slice(0, 8);
    new Chart(document.getElementById('chart-inst'), {
      type: 'bar',
      data: { labels: insts.map(function(i){return i.length>22?i.slice(0,20)+'…':i;}), datasets: [{ label: 'Registros', data: insts.map(function(i){return instCounts[i];}), backgroundColor: '#2ecc71' }] },
      options: { indexAxis: 'y', responsive: true, plugins: { title: { display: true, text: 'Por instituição (top 8)' }, legend: { display: false } }, scales: { x: { beginAtZero: true } } }
    });
  }

  if (buscaInput) buscaInput.addEventListener('input', function () { showAllMode = false; aplicarFiltros(); });

  const btnMostrarTodos = document.getElementById('acervo-mostrar-todos');
  if (btnMostrarTodos) {
    btnMostrarTodos.addEventListener('click', function () {
      showAllMode = true;
      if (buscaInput) buscaInput.value = '';
      if (tipoSelect) tipoSelect.value = '';
      if (instSelect) instSelect.value = '';
      if (anoSelect) anoSelect.value = '';
      aplicarFiltros();
    });
  }
  if (tipoSelect) tipoSelect.addEventListener('change', aplicarFiltros);
  if (instSelect) instSelect.addEventListener('change', aplicarFiltros);
  if (anoSelect) anoSelect.addEventListener('change', aplicarFiltros);
  // Event delegation for share (copy link)
  if (container) {
    container.addEventListener('click', function (e) {
      const target = e.target;
      if (target && target.getAttribute && target.getAttribute('data-share') === 'copy') {
        e.preventDefault();
        const url = target.getAttribute('data-url');
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            target.textContent = 'Link copiado!';
            setTimeout(function () { target.textContent = 'Copiar link'; }, 2000);
          }).catch(function () {
            window.prompt('Copie o link:', url);
          });
        } else {
          window.prompt('Copie o link:', url);
        }
      }
    });
  }

  // Export XLS button
  const btnExportar = document.getElementById('acervo-exportar');
  if (btnExportar) {
    btnExportar.addEventListener('click', function () {
      if (!filteredCache || !filteredCache.length) {
        alert('Nenhum item para exportar.');
        return;
      }
      const cols = [
        { key: 'id', label: 'ID' },
        { key: 'autor', label: 'Autor' },
        { key: 'titulo', label: 'Título' },
        { key: 'ano', label: 'Ano' },
        { key: 'tipo', label: 'Tipo' },
        { key: 'instituicao', label: 'Instituição' },
        { key: 'citacao_abnt', label: 'Referência (ABNT)' },
        { key: 'link', label: 'Link' },
        { key: 'pdf', label: 'PDF' },
        { key: 'link_biblioteca', label: 'Localização na biblioteca' }
      ];
      // Build an HTML table that Excel opens as .xls
      let html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:excel" xmlns="http://www.w3.org/TR/REC-html40">';
      html += '<head><meta charset="UTF-8"><style>td,th{border:1px solid #999;padding:4px;font-family:Calibri;font-size:11pt;} th{background:#2c3e50;color:#fff;font-weight:bold;} tr:nth-child(even){background:#f2f2f2;}</style></head><body>';
      html += '<table><thead><tr>';
      cols.forEach(function (c) { html += '<th>' + escapeHtml(c.label) + '</th>'; });
      html += '</tr></thead><tbody>';
      filteredCache.forEach(function (item) {
        html += '<tr>';
        cols.forEach(function (c) {
          const v = item[c.key] == null ? '' : String(item[c.key]);
          html += '<td>' + escapeHtml(v) + '</td>';
        });
        html += '</tr>';
      });
      html += '</tbody></table></body></html>';
      const blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'acervo_filtrado.xls';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  if (btnLimpar) {
    btnLimpar.addEventListener('click', function () {
      if (buscaInput) buscaInput.value = '';
      if (tipoSelect) tipoSelect.value = '';
      if (instSelect) instSelect.value = '';
      if (anoSelect) anoSelect.value = '';
      aplicarFiltros();
    });
  }
})();