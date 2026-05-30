# LIN — Piloto de Social Listening

Piloto exploratorio de escucha digital sobre la conversación de la manosfera en redes sociales (TikTok, Reddit y YouTube), desarrollado por [Estudio Plural](https://estudio-plural.co) en colaboración con [Camino](https://www.somoscamino.co) para una propuesta al Banco Mundial.

El piloto captura contenido público sobre keywords y comunidades específicas vinculadas al fenómeno, filtra por ventana temporal y genera un reporte ejecutivo con métricas de volumen, geografía, idioma y engagement.

---

## 📊 Informe Interactivo

**🔗 Ver análisis completo:** https://docs-green-xi.vercel.app

El sitio incluye:
- Resumen ejecutivo (1,947 items capturados en 11 días)
- Análisis detallado por plataforma (TikTok, Reddit, YouTube)
- Hallazgos clave y casos narrables
- Conclusiones técnicas y validaciones

---

## Stack

- Python 3.11+
- [Apify](https://apify.com) — actors `clockworks/tiktok-scraper` y `trudax/reddit-scraper-lite`
- pandas, PyYAML

## Setup

```bash
git clone https://github.com/Estudio-Plural/LIN.git
cd LIN
python3.11 -m venv .venv
.venv/bin/pip install -e .
```

Crear `.env` con el token de Apify (sacarlo de [console.apify.com/account/integrations](https://console.apify.com/account/integrations)):

```bash
cp .env.example .env
# editar .env y poner APIFY_TOKEN=apify_api_xxx
```

Ajustar `config.yaml` según el alcance del barrido: keywords (agrupadas por categoría), subreddits, ventana temporal y límites de captura por keyword/subreddit.

## Uso

### Scrapers

```bash
# Barrido completo TikTok (todas las keywords del config)
.venv/bin/python -m src.scrape.tiktok

# Smoke test TikTok con una sola keyword
.venv/bin/python -m src.scrape.tiktok --keyword "looksmaxxing" --limit 20

# Barrido completo Reddit (búsquedas por keyword + captura por subreddit)
.venv/bin/python -m src.scrape.reddit

# Solo búsquedas o solo subreddits
.venv/bin/python -m src.scrape.reddit --skip-subreddits
.venv/bin/python -m src.scrape.reddit --skip-keywords

# Smoke tests Reddit
.venv/bin/python -m src.scrape.reddit --keyword "looksmaxxing"
.venv/bin/python -m src.scrape.reddit --subreddit "MensRights"
```

Los outputs crudos van a `data/raw/{tiktok,reddit}/` como JSON, un archivo por keyword/subreddit con timestamp UTC.

### Reporte ejecutivo

```bash
.venv/bin/python -m src.analyze.report
```

Procesa todo lo que haya en `data/raw/` y genera:

- `data/processed/tiktok_posts.csv` — un row por post de TikTok, con métricas planas
- `data/processed/reddit_items.csv` — posts y comentarios de Reddit
- `data/processed/report.md` — resumen ejecutivo: volumen por keyword, distribución geográfica y por idioma, top posts, costo del barrido

## Estructura

```
LIN/
├── src/
│   ├── scrape/
│   │   ├── _common.py       # config loader, Apify client, filtros temporales
│   │   ├── tiktok.py        # scraper TikTok (clockworks/tiktok-scraper)
│   │   └── reddit.py        # scraper Reddit (trudax/reddit-scraper-lite)
│   └── analyze/
│       └── report.py        # generador del reporte ejecutivo
├── config.yaml              # keywords, subreddits, ventana, límites
├── pyproject.toml
├── data/                    # outputs (gitignored)
│   ├── raw/{tiktok,reddit}/ # JSON crudos por keyword/subreddit
│   └── processed/           # CSVs + report.md
└── brief/                   # contexto del cliente (gitignored, solo local)
```

## Notas técnicas

- **Filtro temporal en TikTok:** el actor solo acepta valores predefinidos para búsquedas (`PAST_WEEK`, `PAST_MONTH`, etc.). El filtrado exacto por ventana custom se hace en post-procesamiento usando el timestamp `createTime` de cada post.
- **Reddit:** el actor `trudax/reddit-scraper-lite` devuelve posts y comentarios en una sola pasada, lo que permite análisis discursivo sin runs extra. Los comentarios se identifican con `dataType: "comment"` y se asocian al post padre vía `postId` / `parentId`.
- **Plataformas fuera de scope inicial:** Discord (comunidades cerradas, ToS estricto) y Twitch live (frágil vía scraping). Se evalúan en una segunda fase del piloto con un approach diferente al de Apify.

## Licencia

Proyecto interno de Estudio Plural. El código es público pero el material del cliente (briefs, keywords detalladas, hallazgos del piloto) no está incluido en el repo.
