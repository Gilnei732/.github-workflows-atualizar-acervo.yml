(function () {
  const container = document.getElementById('acervo-lista');
  const statusEl = document.getElementById('acervo-status');
  const buscaInput = document.getElementById('acervo-busca');
  const tipoSelect = document.getElementById('acervo-tipo');
  const anoSelect = document.getElementById('acervo-ano');
  const btnLimpar = document.getElementById('acervo-limpar');

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

  function render(items) {
    if (!items.length) {
      container.innerHTML = '<p class="destaque">Nenhum registro encontrado com os filtros atuais. Ajuste a busca ou os filtros.</p>';
      statusEl.textContent = '0 registro(s) exibido(s).';
      return;
    }
    statusEl.textContent = items.length + ' registro(s) exibido(s).';
    container.innerHTML = items.map(function (item) {
      const citacao = item.citacao_abnt && item.citacao_abnt.trim()
        ? item.citacao_abnt.trim()
        : ((item.autor || 'AUTOR, Não informado') + '. ' + (item.titulo || 'Título não informado') + '. ' + (item.ano || 's/d') + '.');
      const pdfLink = item.pdf && item.pdf.trim()
        ? '<p style="margin-top:0.6rem;"><a href="' + escapeHtml(item.pdf) + '" target="_blank" rel="noopener noreferrer">Clique aqui para baixar</a></p>'
        : '<p style="margin-top:0.6rem; color:#555;"><em>Arquivo não disponível no momento.</em></p>';
      const bibLink = item.link_biblioteca && item.link_biblioteca.trim()
        ? '<p style="margin-top:0.4rem; font-size:0.85rem;"><a href="' + escapeHtml(item.link_biblioteca) + '" target="_blank" rel="noopener noreferrer">Ver localização na biblioteca</a></p>'
        : '';
      return '<article class="card" style="margin-bottom:1rem;">' +
        '<p style="margin:0; font-size:0.95rem;">' + escapeHtml(citacao) + '</p>' +
        pdfLink +
        bibLink +
        '</article>';
    }).join('');
  }

  function aplicarFiltros() {
    const q = (buscaInput && buscaInput.value ? buscaInput.value : '').trim().toLowerCase();
    const tipo = tipoSelect && tipoSelect.value ? tipoSelect.value : '';
    const ano = anoSelect && anoSelect.value ? anoSelect.value : '';

    const filtrados = dados.filter(function (item) {
      const matchTipo = !tipo || item.tipo === tipo;
      const matchAno = !ano || String(item.ano) === ano;
      if (!matchTipo || !matchAno) return false;
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
      const autorA = ((a.autor || '') + '').toLowerCase();
      const autorB = ((b.autor || '') + '').toLowerCase();
      if (autorA < autorB) return -1;
      if (autorA > autorB) return 1;
      const tituloA = ((a.titulo || '') + '').toLowerCase();
      const tituloB = ((b.titulo || '') + '').toLowerCase();
      if (tituloA < tituloB) return -1;
      if (tituloA > tituloB) return 1;
      return 0;
    });
    render(filtrados);
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

  fetch('dados/acervo.json')
    .then(function (r) {
      if (!r.ok) throw new Error('Erro ao carregar acervo.');
      return r.json();
    })
    .then(function (json) {
      dados = Array.isArray(json) ? json : [];
      preencherAnos(dados);
      aplicarFiltros();
    })
    .catch(function () {
      statusEl.textContent = 'Não foi possível carregar o acervo (dados/acervo.json).';
      container.innerHTML = '<p class="destaque">O arquivo de dados não foi encontrado ou não pôde ser lido. Se você abriu o site apenas clicando no arquivo (file://), alguns navegadores bloqueiam o carregamento. Use um servidor local (ex.: extensão Live Server) ou publique o site.</p>';
    });

  if (buscaInput) buscaInput.addEventListener('input', aplicarFiltros);
  if (tipoSelect) tipoSelect.addEventListener('change', aplicarFiltros);
  if (anoSelect) anoSelect.addEventListener('change', aplicarFiltros);
  if (btnLimpar) {
    btnLimpar.addEventListener('click', function () {
      if (buscaInput) buscaInput.value = '';
      if (tipoSelect) tipoSelect.value = '';
      if (anoSelect) anoSelect.value = '';
      aplicarFiltros();
    });
  }
})();
