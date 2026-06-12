# LIN — Piloto de Social Listening

Piloto exploratorio de escucha digital sobre la conversación de la manosfera en redes sociales (TikTok, Reddit y YouTube), desarrollado por [Estudio Plural](https://estudio-plural.co) en colaboración con [Camino](https://www.somoscamino.co) para una propuesta al Banco Mundial.

El piloto captura contenido público por keywords, lo clasifica con IA para separar señal de ruido, y lo presenta en tres entregables: un dashboard interactivo, un informe web y un monitor de crecimiento que corre a diario en la nube.

---

## 📊 Entregables

**🔗 Dashboard — Radiografía de la manosfera hispana:** https://lin-manosfera.vercel.app

Barrido TikTok de 4 meses (feb–may 2026, 742 videos únicos), cada video clasificado con IA en señal vs ruido. Hallazgo rector: **solo el 35% de lo que matchea las keywords es manosfera sincera** — medir el fenómeno por volumen crudo lo sobreestima ~3×. Incluye red de hashtags y creadores, geografía, engagement por tema, subtemas de la señal y un explorador del corpus video por video con la razón de cada clasificación.

**🔗 Informe del barrido inicial:** https://docs-green-xi.vercel.app

Primer barrido multiplataforma (1,947 items en 11 días: TikTok, Reddit, YouTube), con análisis por plataforma, hallazgos clave y conclusiones técnicas.

**📈 Monitor de crecimiento** (activo desde 2026-06-12): captura diaria de los videos frescos de 12 creadores manosfera curados (Apify Schedule en la nube), para medir la curva de vida del contenido — cuándo despega y cuándo muere un video.

---

## Stack

- Python 3.11+ · pandas · PyYAML
- [Apify](https://apify.com) — actors `clockworks/tiktok-scraper` y `trudax/reddit-scraper-lite`
- Clasificación: `gemini-2.5-flash` vía OpenRouter
- Dashboard: Next.js + Recharts (en `dashboard/`, deploy en Vercel)
- Informe: Docusaurus (en `docs/`)

## Setup

```bash
git clone https://github.com/Estudio-Plural/LIN.git
cd LIN
python3.11 -m venv .venv
.venv/bin/pip install -e .
```

Crear `.env` con los tokens:

```bash
cp .env.example .env
# APIFY_TOKEN=apify_api_xxx        (console.apify.com/account/integrations)
# OPENROUTER_API_KEY=sk-or-xxx     (solo para clasificar)
```

Ajustar `config.yaml` según el alcance del barrido: keywords (agrupadas por categoría), subreddits, ventana temporal y límites de captura.

## Uso

### 1. Scrapers

```bash
# Barrido completo TikTok (todas las keywords del config)
.venv/bin/python -m src.scrape.tiktok

# Smoke test con una keyword
.venv/bin/python -m src.scrape.tiktok --keyword "looksmaxxing" --limit 20

# Reddit y YouTube
.venv/bin/python -m src.scrape.reddit
.venv/bin/python -m src.scrape.youtube
```

Los outputs crudos van a `data/raw/{tiktok,reddit,youtube}/` como JSON con timestamp UTC.

### 2. Análisis y clasificación

```bash
# Reporte ejecutivo del barrido (CSVs + report.md)
.venv/bin/python -m src.analyze.report

# Clasificación señal vs ruido con IA (requiere OPENROUTER_API_KEY)
.venv/bin/python -m src.analyze.classify
```

### 3. Dashboard

```bash
.venv/bin/python -m src.analyze.build_dashboard_data
.venv/bin/python -m src.analyze.build_network
cp data/dashboard/*.json dashboard/public/data/
npx vercel deploy --prod --yes --cwd dashboard
```

### 4. Monitor de crecimiento

```bash
# Ranking de creadores → data/processed/monitor_handles.txt (curar a mano)
.venv/bin/python -m src.analyze.top_creators

# Crear Task + Schedule en Apify (DRY-RUN sin flags; tocar la nube exige flags explícitos)
.venv/bin/python -m src.monitor.setup_apify_schedule --create-task --first-run
.venv/bin/python -m src.monitor.setup_apify_schedule --create-schedule --enable

# Reconstruir curvas desde los runs de Apify (no necesita archivos locales)
.venv/bin/python -m src.monitor.build_curves_apify
```

## Estructura

```
LIN/
├── src/
│   ├── scrape/              # scrapers Apify (tiktok, reddit, youtube)
│   ├── analyze/             # report, classify, top_creators, build_dashboard_data, build_network
│   └── monitor/             # snapshot, setup_apify_schedule, build_curves[_apify]
├── dashboard/               # dashboard Next.js (Vercel)
├── docs/                    # informe Docusaurus (Vercel)
├── config.yaml              # keywords, subreddits, ventana, límites
├── data/                    # outputs (gitignored)
└── brief/                   # contexto del cliente (gitignored, solo local)
```

## Notas técnicas

- **Señal vs ruido:** el volumen crudo de keywords sobreestima el fenómeno ~3× (incluye crítica, sátira, periodismo y falsos positivos). Usar siempre la capa clasificada para cifras.
- **Sesgo temporal del barrido:** el sort `LATEST` sobre-muestrea lo reciente — los conteos por mes no se leen como crecimiento. Para dinámica temporal está el monitor.
- **Filtro temporal en TikTok:** el actor solo acepta ventanas predefinidas; el filtrado exacto se hace en post-procesamiento con `createTime`.
- **Reddit:** `trudax/reddit-scraper-lite` devuelve posts y comentarios en una pasada (`dataType: "comment"`, asociados vía `postId`/`parentId`).
- **Fuera de scope inicial:** Discord (comunidades cerradas, ToS estricto) y Twitch live (frágil vía scraping). Se evalúan en una segunda fase con otro approach.

## Licencia

Proyecto interno de Estudio Plural. El código es público pero el material del cliente (briefs, keywords detalladas, hallazgos del piloto) no está incluido en el repo.
