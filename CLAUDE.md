# LIN — Piloto de Social Listening (Estudio Plural × Camino)

Escucha digital de la manosfera hispana en redes (foco TikTok), insumo para una propuesta
al Banco Mundial. Todo el texto orientado a usuario va en español.

## Layout

- `src/scrape/` — scrapers vía Apify (TikTok `clockworks/tiktok-scraper`, Reddit, YouTube)
- `src/analyze/` — análisis y clasificación del barrido (`classify.py` usa gemini-2.5-flash vía OpenRouter)
- `src/monitor/` — monitor de crecimiento de videos frescos (ver abajo)
- `dashboard/` — dashboard Next.js (tiene su propio CLAUDE.md/AGENTS.md — leerlo antes de tocar)
- `docs/` — sitio Docusaurus del informe
- `data/` — raw/processed **gitignorados** (solo locales); excepción: `data/dashboard/*.json` (los que alimentan el dashboard) sí están versionados
- `config.yaml` — keywords y ventanas del barrido

## Setup

- Python 3.11+ con `.venv` (`.venv/bin/python`); deps en `pyproject.toml`
- `.env` (gitignorado): `APIFY_TOKEN` (scrapers/monitor) y `OPENROUTER_API_KEY` (clasificación)

## Pipeline del dashboard

1. `python -m src.analyze.classify` → etiqueta cada video (señal vs ruido)
2. `build_dashboard_data.py` (videos.json + meta.json) y `build_network.py` (red de **comunidades
   temáticas** por modularidad, requiere `networkx`) → JSONs en `data/dashboard/`
2.5. `python -m src.monitor.build_growth_data` → `growth.json` (curva de vida del monitor; reusa los
   CSV de `build_curves_apify`). Alimenta la sección "Curva de vida" del dashboard; carga tolerante
   (si falta el JSON, el resto del dashboard igual renderiza)
3. Copiar `data/dashboard/*.json` → `dashboard/public/data/`
4. Deploy: `npx vercel deploy --prod --yes --cwd dashboard`

Dashboard vivo: https://lin-manosfera.vercel.app (proyecto Vercel `lin-manosfera`).
Los metadatos OG y el stat "señal real" se generan desde `dashboard/public/data/meta.json`
en build — basta regenerar datos y redeployar.

## Monitor de crecimiento (ACTIVO desde 2026-06-12)

Mide la curva de vida de videos frescos de creadores manosfera curados.

- Task Apify: `lin-monitor-growth` · Schedule: `lin-monitor-growth-daily` (diario 13:00 UTC, enabled)
- Handles curados: `data/processed/monitor_handles.txt` (12 cuentas, hispanas, sinceras/ambiguas;
  se eliminó una granja de reposteo `#countryboy #hombrealfa` de ~6 cuentas `user...`)
- Curvas: `python -m src.monitor.build_curves_apify` — lee TODOS los runs del task desde la API
  de Apify (no necesita archivos locales previos; solo APIFY_TOKEN). Con <2 snapshots no hay curva.
- `setup_apify_schedule.py` es DRY-RUN por defecto; tocar la nube requiere flags explícitos
  (`--create-task`, `--first-run`, `--create-schedule`, `--enable`)

## Validación de la clasificación (PENDIENTE — propuesto a Camino 2026-06-18)

El 35% "señal real" es estimación de gemini sin validar (ver caveat en Convenciones). Plan acordado
para darle respaldo, en dos fases (pedido a Camino por correo el 2026-06-18, a la espera de su OK):

- **Fase 1 (~30 videos, ~20 min):** dos personas etiquetan a mano una muestra **estratificada por
  etiqueta y cargada a los casos de frontera** (`manosfera_sincera ↔ ambiguo ↔ contra_critica`, donde
  el modelo más duda y donde los errores mueven el 35%). Valida instrucciones + lectura direccional.
- **Fase 2 (~70 más):** completar hasta ~100–150 videos para un κ estable y accuracy reportable (~±6–8pp).

Claves de método (no negociar): **estratificar, no muestrear al azar** (clases raras como `satira_humor`
~4% no aparecen en una muestra chica aleatoria); **doble anotación** del mismo set para separar error del
modelo de ambigüedad de la tarea (κ humano-humano + acuerdo humano-modelo). 25 videos NO alcanzan para un
número reportable (IC demasiado ancho con 6 clases).

Pendiente operativo cuando den el OK: generar el set de fase 1 (link + texto + etiqueta del modelo) en
una planilla de ver-y-marcar.

## Convenciones

- Ejecutar módulos desde la raíz del repo: `python -m src.modulo.script`
- Los conteos por mes del barrido están sesgados por el scraping (sort LATEST) — no leer como
  crecimiento; para dinámica temporal usar el monitor
- Volumen crudo de keywords sobreestima el fenómeno ~3× — usar la capa clasificada (solo ~35%
  es manosfera sincera). Ese 35% es estimación de gemini **sin validación humana** (plan de validación
  en dos fases arriba: §Validación de la clasificación); no presentarlo como medición con margen de error
- Geo "Latinoamérica" del dashboard = país incl. **Brasil**, excl. **España** (decisión 2026-06-17);
  por idioma el peso hispano es más conservador (~29% es/pt, ~26% sin idioma detectado)
