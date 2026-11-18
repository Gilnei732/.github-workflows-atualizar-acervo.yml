(function (global) {
  'use strict';

  var CORES_REG = {"Norte": "#1B7F79", "Nordeste": "#C8553D", "Centro-Oeste": "#D9A21B", "Sudeste": "#6A4C93", "Sul": "#3A7D44"};
  var CORES_CAT = {"NEAB": "#1F3B57", "NEABI": "#C8553D", "Correlato": "#9AA7AE"};
  var CATS = ['NEAB', 'NEABI', 'Correlato'];
  var REGS = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
  var CLASSE = { NEAB: 'nm-circulo', NEABI: 'nm-quadrado', Correlato: 'nm-pequeno' };
  var DESC = {
    NEAB: 'nome é apenas Núcleo de Estudos Afro-Brasileiros',
    NEABI: 'nome traz complemento (indígenas, africanos…)',
    Correlato: 'laboratório, programa, centro ou grupo'
  };
  var FONTE = "Fonte: Rede NEAB/I's (UFSCar, 2024) e CONNEABS/ABPN.";

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function contar(lista, campo, valor) {
    return lista.filter(function (d) { return d[campo] === valor; }).length;
  }

  function formaTexto() {
    return 'Forma = categoria: círculo NEAB · quadrado NEABI · pequeno correlato.';
  }

  function criar(container, opcoes) {
    if (!container || container.neabsMapa) return null;

    var o = Object.assign({
      dados: null,
      modoInicial: 'categoria',
      mostrarTitulo: true,
      mostrarLegenda: true,
      titulo: 'Núcleos de Estudos Afro-Brasileiros e Indígenas no Brasil',
      subtitulo: null,
      limites: [[-33.8, -74.0], [5.3, -34.7]],
      recolherEmTelasPequenas: true
    }, opcoes || {});

    var dados = o.dados || global.NEABS_DADOS || [];
    if (!dados.length) {
      container.innerHTML = '<p style="padding:24px;font:14px sans-serif">' +
        'Base de dados do mapa não carregada.</p>';
      return null;
    }
    if (!global.L) {
      container.innerHTML = '<p style="padding:24px;font:14px sans-serif">' +
        'Leaflet não carregado.</p>';
      return null;
    }

    container.classList.add('neabs-mapa');
    if (!container.style.height && container.clientHeight < 80) {
      container.style.height = '560px';
    }

    var total = dados.length;
    var cCat = {};
    var cReg = {};
    CATS.forEach(function (c) { cCat[c] = contar(dados, 'categoria', c); });
    REGS.forEach(function (r) { cReg[r] = contar(dados, 'regiao', r); });
    var nMunicipios = new Set(dados.map(function (d) { return d.cidade + '|' + d.uf; })).size;

    var canvas = document.createElement('div');
    canvas.className = 'nm-canvas';
    container.appendChild(canvas);

    var mapa = global.L.map(canvas, {
      zoomControl: false,
      scrollWheelZoom: true,
      minZoom: 3,
      maxZoom: 18
    });
    global.L.control.zoom({ position: 'topright' }).addTo(mapa);
    global.L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(mapa);
    global.L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                   '&copy; <a href="https://carto.com/attributions">CARTO</a>'
    }).addTo(mapa);
    mapa.fitBounds(o.limites, { padding: [12, 12] });

    var modo = o.modoInicial === 'regiao' ? 'regiao' : 'categoria';
    var ativos = new Set(CATS);
    var camada = global.L.layerGroup().addTo(mapa);
    var paineis = [];

    function corDe(d) {
      return modo === 'categoria' ? CORES_CAT[d.categoria] : CORES_REG[d.regiao];
    }

    function popup(d) {
      var cls = d.categoria === 'NEAB' ? 'neab'
              : d.categoria === 'NEABI' ? 'neabi' : 'corr';
      var rot = d.categoria === 'NEAB' ? 'NEAB'
              : d.categoria === 'NEABI' ? 'NEABI' : 'CORRELATO';
      var site = d.site
        ? '<a class="nm-pop-site" href="' + esc(d.site) + '" target="_blank" ' +
          'rel="noopener">' + esc(String(d.site).replace(/^https?:\/\//, '')
            .replace(/\/$/, '')) + '</a>'
        : '<div class="nm-pop-lin" style="color:#8A99A3;margin-top:8px">' +
          'Site não localizado nas fontes</div>';
      return '<div class="nm-pop-sigla">' + esc(d.sigla) + '</div>' +
        '<div class="nm-pop-nome">' + esc(d.nome) + '</div>' +
        '<div class="nm-pop-lin"><b>Instituição:</b> ' + esc(d.instituicao) + '</div>' +
        '<div class="nm-pop-lin"><b>Sede:</b> ' + esc(d.cidade) + '/' +
          esc(d.uf) + ' · ' + esc(d.regiao) + '</div>' +
        '<div class="nm-pop-lin"><b>Coordenadas:</b> ' + d.lat.toFixed(4) +
          ', ' + d.lon.toFixed(4) + '</div>' +
        '<div class="nm-pop-lin"><b>Confiança:</b> ' + esc(d.confianca) +
          ' · <b>Fonte:</b> ' + esc(d.fonte) + '</div>' +
        site + '<div class="nm-pop-tag ' + cls + '">' + rot + '</div>';
    }

    function desenhar() {
      camada.clearLayers();
      var ordem = ['Correlato', 'NEABI', 'NEAB'];
      ordem.forEach(function (cat) {
        if (!ativos.has(cat)) return;
        dados.forEach(function (d) {
          if (d.categoria !== cat) return;
          var icone = global.L.divIcon({
            className: 'nm-pt ' + CLASSE[d.categoria],
            html: '<span style="background:' + corDe(d) + '"></span>',
            iconSize: [18, 18],
            iconAnchor: [9, 9],
            popupAnchor: [0, -9]
          });
          global.L.marker([d.lat, d.lon], {
            icon: icone,
            title: d.sigla,
            riseOnHover: true
          }).bindPopup(popup(d)).addTo(camada);
        });
      });
    }

    function definirRecolhido(painel, recolhido) {
      var btn = painel.querySelector('.nm-btn-min');
      painel.classList.toggle('nm-recolhido', recolhido);
      btn.textContent = recolhido ? '+' : '−';
      btn.setAttribute('aria-expanded', String(!recolhido));
      var rot = recolhido ? 'Expandir painel' : 'Recolher painel';
      btn.setAttribute('aria-label', rot);
      btn.title = rot;
    }

    function arrastavel(painel) {
      var cab = painel.querySelector('.nm-cab');
      var movendo = false;
      var dx = 0;
      var dy = 0;

      cab.addEventListener('pointerdown', function (ev) {
        if (ev.target.closest('button, a, input, label')) return;
        if (ev.button !== undefined && ev.button !== 0) return;
        var c = container.getBoundingClientRect();
        var r = painel.getBoundingClientRect();
        painel.style.left = (r.left - c.left) + 'px';
        painel.style.top = (r.top - c.top) + 'px';
        painel.style.right = 'auto';
        painel.style.bottom = 'auto';
        dx = ev.clientX - r.left;
        dy = ev.clientY - r.top;
        movendo = true;
        painel.classList.add('nm-arrastando');
        try { cab.setPointerCapture(ev.pointerId); } catch (e) { /* ignore */ }
        ev.preventDefault();
      });

      cab.addEventListener('pointermove', function (ev) {
        if (!movendo) return;
        var c = container.getBoundingClientRect();
        var r = painel.getBoundingClientRect();
        var x = ev.clientX - c.left - dx;
        var y = ev.clientY - c.top - dy;
        x = Math.min(Math.max(6, x), Math.max(6, c.width - r.width - 6));
        y = Math.min(Math.max(6, y), Math.max(6, c.height - r.height - 6));
        painel.style.left = x + 'px';
        painel.style.top = y + 'px';
      });

      function soltar(ev) {
        if (!movendo) return;
        movendo = false;
        painel.classList.remove('nm-arrastando');
        try { cab.releasePointerCapture(ev.pointerId); } catch (e) { /* ignore */ }
      }
      cab.addEventListener('pointerup', soltar);
      cab.addEventListener('pointercancel', soltar);

      cab.addEventListener('dblclick', function (ev) {
        if (ev.target.closest('button, a, input, label')) return;
        painel.style.left = painel.style.top = '';
        painel.style.right = painel.style.bottom = '';
      });
    }

    function novoPainel(classe, tituloHtml, corpoHtml, rotulo) {
      var sec = document.createElement('section');
      sec.className = 'nm-painel ' + classe;
      sec.setAttribute('aria-label', rotulo);
      sec.innerHTML =
        '<div class="nm-cab" title="Arraste para mover · clique duas vezes para ' +
        'voltar ao canto">' + tituloHtml +
        '<button type="button" class="nm-btn-min" aria-expanded="true" ' +
        'aria-label="Recolher painel" title="Recolher painel">−</button></div>' +
        '<div class="nm-corpo">' + corpoHtml + '</div>';
      container.appendChild(sec);
      sec.querySelector('.nm-btn-min').addEventListener('click', function () {
        definirRecolhido(sec, !sec.classList.contains('nm-recolhido'));
      });
      arrastavel(sec);
      paineis.push(sec);
      return sec;
    }

    // ------------------------------------------------------------- título
    if (o.mostrarTitulo) {
      var sub = o.subtitulo ||
        ('<strong>' + cCat.NEAB + ' NEAB</strong> · ' +
         '<strong>' + cCat.NEABI + ' NEABI</strong> · ' +
         '<strong>' + cCat.Correlato + ' correlatos</strong>');
      novoPainel('nm-titulo',
        '<h1 class="nm-h1">' + esc(o.titulo) + '</h1>',
        '<p class="nm-sub">' + sub + '</p>' +
        '<p class="nm-sub nm-fraco">' + total + ' registros em ' +
        nMunicipios + ' municípios-sede</p>',
        'Título e totais');
    }

    // ------------------------------------------------------------ legenda
    var legenda = null;
    var itensEl = null;
    var notaEl = null;

    function atualizarItens() {
      itensEl.innerHTML = '';
      if (modo === 'categoria') {
        CATS.forEach(function (cat) {
          var ativo = ativos.has(cat);
          var lab = document.createElement('label');
          lab.className = 'nm-linha' + (ativo ? '' : ' nm-desligado');
          lab.innerHTML =
            '<input type="checkbox"' + (ativo ? ' checked' : '') + '>' +
            '<span class="nm-marca ' + CLASSE[cat] + '" style="background:' +
              CORES_CAT[cat] + '"></span>' +
            '<span class="nm-nome" title="' + esc(DESC[cat]) + '">' + cat +
              '</span><small>' + cCat[cat] + '</small>';
          var input = lab.querySelector('input');
          input.addEventListener('change', function () {
            if (input.checked) ativos.add(cat); else ativos.delete(cat);
            lab.classList.toggle('nm-desligado', !input.checked);
            desenhar();
          });
          itensEl.appendChild(lab);
        });
        notaEl.innerHTML = 'Marque para filtrar.<br>' + FONTE;
      } else {
        REGS.forEach(function (r) {
          var div = document.createElement('div');
          div.className = 'nm-linha nm-fixa';
          div.innerHTML = '<span class="nm-marca nm-circulo" style="background:' +
            CORES_REG[r] + '"></span><span class="nm-nome">' + r +
            '</span><small>' + cReg[r] + '</small>';
          itensEl.appendChild(div);
        });
        notaEl.innerHTML = 'Cor = região. ' + formaTexto() + '<br>' + FONTE;
      }
    }

    if (o.mostrarLegenda) {
      legenda = novoPainel('nm-legenda',
        '<h2 class="nm-h2">Camadas</h2>',
        '<div class="nm-seg" role="group" aria-label="Colorir por">' +
          '<button type="button" data-modo="categoria" aria-pressed="' +
            (modo === 'categoria') + '">Categoria</button>' +
          '<button type="button" data-modo="regiao" aria-pressed="' +
            (modo === 'regiao') + '">Região</button>' +
        '</div><div class="nm-itens"></div><p class="nm-nota"></p>',
        'Legenda e filtros');

      itensEl = legenda.querySelector('.nm-itens');
      notaEl = legenda.querySelector('.nm-nota');

      Array.prototype.forEach.call(
        legenda.querySelectorAll('.nm-seg button'),
        function (btn) {
          btn.addEventListener('click', function () {
            modo = btn.getAttribute('data-modo');
            Array.prototype.forEach.call(
              legenda.querySelectorAll('.nm-seg button'),
              function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
            atualizarItens();
            desenhar();
          });
        });

      atualizarItens();

      if (o.recolherEmTelasPequenas && global.innerWidth < 760) {
        definirRecolhido(legenda, true);
      }
    }

    // --------------------------------------------------- limites / resize
    function reposicionar() {
      paineis.forEach(function (p) {
        if (!p.style.left) return;
        var c = container.getBoundingClientRect();
        var r = p.getBoundingClientRect();
        var x = Math.min(Math.max(6, parseFloat(p.style.left) || 0),
                         Math.max(6, c.width - r.width - 6));
        var y = Math.min(Math.max(6, parseFloat(p.style.top) || 0),
                         Math.max(6, c.height - r.height - 6));
        p.style.left = x + 'px';
        p.style.top = y + 'px';
      });
    }
    global.addEventListener('resize', reposicionar);

    desenhar();

    var api = {
      mapa: mapa,
      dados: dados,
      definirModo: function (m) {
        if (m !== 'categoria' && m !== 'regiao') return;
        if (!legenda) return;
        var alvo = legenda.querySelector('.nm-seg button[data-modo="' + m + '"]');
        if (alvo) alvo.click();
      },
      filtrar: function (cats) {
        ativos = new Set(cats.filter(function (c) { return CATS.indexOf(c) >= 0; }));
        if (legenda) atualizarItens();
        desenhar();
        return Array.from(ativos);
      },
      recolherPainel: function (recolhido) {
        paineis.forEach(function (p) { definirRecolhido(p, recolhido !== false); });
      },
      destruir: function () {
        global.removeEventListener('resize', reposicionar);
        mapa.remove();
        container.innerHTML = '';
        container.classList.remove('neabs-mapa');
        container.neabsMapa = null;
      }
    };
    container.neabsMapa = api;
    return api;
  }

  function iniciar() {
    var alvos = document.querySelectorAll('[data-neabs-mapa]');
    Array.prototype.forEach.call(alvos, function (el) {
      if (el.neabsMapa) return;
      var cfg = {};
      if (el.dataset.neabsOpcoes) {
        try { cfg = JSON.parse(el.dataset.neabsOpcoes); }
        catch (e) { if (global.console) console.warn('Opções inválidas:', e); }
      }
      criar(el, cfg);
    });
  }

  global.NEABSMapa = { criar: criar, versao: '1.0.0' };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
}(window));
