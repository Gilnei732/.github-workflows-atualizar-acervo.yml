# Mapa de NEABs e NEABIs — pacote para site

Componente estático, sem build e sem framework. Copie a pasta para o seu site
e use como página inteira, dentro de um `iframe` ou instanciando o componente.

## Arquivos

```
web/
├── index.html                 demonstração em tela cheia
├── embed.html                 versão mínima, sem título, para iframe
├── assets/
│   ├── mapa-neabs.css         estilos (tudo sob .neabs-mapa)
│   └── mapa-neabs.js          componente + auto-inicialização
├── dados/
│   ├── neabs.js               window.NEABS_DADOS (usado pela página)
│   ├── neabs.json             os mesmos dados em JSON
│   └── neabs.geojson          pontos com propriedades, para GIS/outros mapas
└── vendor/leaflet/            Leaflet 1.9.4 local (sem CDN)
```

## 1. Como página inteira

Publique a pasta `web/` e abra `/web/index.html`.

## 2. Dentro de um iframe

```html
<iframe src="/web/embed.html" title="Mapa de NEABs e NEABIs"
        style="width:100%;height:600px;border:0"
        loading="lazy"></iframe>
```

## 3. Instanciando no seu layout

Inclua os estilos e os scripts e marque o container:

```html
<link rel="stylesheet" href="/web/vendor/leaflet/leaflet.css">
<link rel="stylesheet" href="/web/assets/mapa-neabs.css">

<div id="mapa-neabs" style="height:560px"></div>

<script src="/web/vendor/leaflet/leaflet.js"></script>
<script src="/web/dados/neabs.js"></script>
<script src="/web/assets/mapa-neabs.js"></script>
<script>
  NEABSMapa.criar(document.getElementById('mapa-neabs'), {
    titulo: 'NEABs e NEABIs no Brasil',
    mostrarTitulo: false,          // o site já tem título próprio
    modoInicial: 'categoria'       // ou 'regiao'
  });
</script>
```

O container precisa de altura definida (CSS). Se não tiver, o componente aplica
`560px` como padrão.

### Opções

| Opção | Padrão | Efeito |
|---|---|---|
| `dados` | `window.NEABS_DADOS` | array de registros; permite carregar de API |
| `titulo` | nome completo | texto do painel de título |
| `subtitulo` | contagens automáticas | HTML da linha abaixo do título |
| `mostrarTitulo` | `true` | exibe o painel de título |
| `mostrarLegenda` | `true` | exibe o painel de camadas/filtros |
| `modoInicial` | `'categoria'` | `'categoria'` ou `'regiao'` |
| `limites` | Brasil | `[[sul, oeste], [norte, leste]]` do enquadramento |
| `recolherEmTelasPequenas` | `true` | inicia o painel recolhido abaixo de 760 px |

### API

```js
const mapa = NEABSMapa.criar(el, opcoes);
mapa.definirModo('regiao');         // troca a cor
mapa.filtrar(['NEAB', 'NEABI']);    // esconde correlatos
mapa.recolherPainel(true);          // recolhe os quadros
mapa.destruir();                    // remove o mapa e libera o container
```

Também é possível usar só com atributos, sem escrever JS:

```html
<div class="neabs-mapa" data-neabs-mapa
     data-neabs-opcoes='{"mostrarTitulo": false}'></div>
```

## Comportamento dos painéis

Os dois quadros são compactos, **arrastáveis pelo cabeçalho** e **recolhíveis**
pelo botão `−`/`+`. Duplo clique no cabeçalho devolve o quadro ao canto
original. Em telas estreitas o painel de camadas já inicia recolhido e o painel
de título é ocultado por CSS.

## Dados

`dados/neabs.geojson` usa `[longitude, latitude]` (ordem GeoJSON) e traz sigla,
nome, instituição, cidade, UF, região, site, categoria, confiança e fonte.
Para atualizar a base, regenere com `gerar_mapa_html.py` na pasta do projeto.

## Publicação

- Não precisa de build, servidor de aplicação nem banco: são arquivos estáticos.
- **Mapa de base:** usa tiles do OpenStreetMap. Para produção com tráfego alto,
  troque por um provedor próprio (MapTiler, Mapbox, Stadia) ou por tiles
  servidos pela instituição — a política de uso do OSM não cobre uso intenso.
  A troca é uma linha em `assets/mapa-neabs.js` (`L.tileLayer(...)`).
- A atribuição ao OpenStreetMap é obrigatória e já está no controle do Leaflet.
- Todas as classes começam com `nm-` e ficam sob `.neabs-mapa`, então o CSS não
  interfere no restante do site.
- O arquivo `mapa_neabs_brasil.html`, na pasta do projeto, é a versão de arquivo
  único (Leaflet, dados e estilos embutidos) para enviar por e-mail ou abrir
  direto do disco, sem depender desta pasta.
