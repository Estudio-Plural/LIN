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

## Monitor de crecimiento (PAUSADO desde 2026-07-08 · activo 2026-06-12→07-08)

Mide la curva de vida de videos frescos de creadores manosfera curados.

- Task Apify: `lin-monitor-growth` · Schedule: `lin-monitor-growth-daily` (id `T8G7ETTvYOnh5cOpW`,
  diario 13:00 UTC) — **PAUSADO 2026-07-08** (`is_enabled=False`); el Task y el historial de snapshots
  siguen intactos (`build_curves_apify` funciona con lo ya capturado). Reactivar:
  `.venv/bin/python -c "from src.scrape._common import get_client; get_client().schedule('T8G7ETTvYOnh5cOpW').update(is_enabled=True)"`
- Handles curados: `data/processed/monitor_handles.txt` (12 cuentas, hispanas, sinceras/ambiguas;
  se eliminó una granja de reposteo `#countryboy #hombrealfa` de ~6 cuentas `user...`)
- Curvas: `python -m src.monitor.build_curves_apify` — lee TODOS los runs del task desde la API
  de Apify (no necesita archivos locales previos; solo APIFY_TOKEN). Con <2 snapshots no hay curva.
- `setup_apify_schedule.py` es DRY-RUN por defecto; tocar la nube requiere flags explícitos
  (`--create-task`, `--first-run`, `--create-schedule`, `--enable`)

## Validación de la clasificación (EN CURSO — Camino dio OK 2026-06-25; Fase 1 enviada)

El 35% "señal real" es estimación de gemini sin validar (ver caveat en Convenciones). Plan en dos
fases para darle respaldo; Camino respondió OK el 2026-06-25 y la Fase 1 ya está armada y enviada
(plazo de marcado pedido: martes 30/06):

- **Fase 1 (~30 videos, ~20 min):** dos personas etiquetan a mano una muestra **estratificada por
  etiqueta y cargada a los casos de frontera** (`manosfera_sincera ↔ ambiguo ↔ contra_critica`, donde
  el modelo más duda y donde los errores mueven el 35%). Valida instrucciones + lectura direccional.
- **Fase 2 (~70 más):** completar hasta ~100–150 videos para un κ estable y accuracy reportable (~±6–8pp).

Claves de método (no negociar): **estratificar, no muestrear al azar** (clases raras como `satira_humor`
~4% no aparecen en una muestra chica aleatoria); **doble anotación** del mismo set para separar error del
modelo de ambigüedad de la tarea (κ humano-humano + acuerdo humano-modelo). 25 videos NO alcanzan para un
número reportable (IC demasiado ancho con 6 clases).

Set de Fase 1 (generado): `python -m src.analyze.build_validation_set` → escribe en
`data/processed/validacion_fase1/` (gitignored): `LIN_validacion_fase1.xlsx` (planilla de ver-y-marcar,
**anotación CIEGA** — a propósito NO muestra la etiqueta del modelo, para no anclar al anotador) +
`CLAVE_fase1.csv` (id→etiqueta+confianza del modelo; local, para medir el acuerdo después). Muestra
estratificada y cargada a frontera por **menor `confianza`** (de `classified.json`): 30 videos
(8 sincera / 7 ambiguo / 5 crítica / 5 sátira / 3 FP / 2 medio), ~28 hispanos, intercalados. Para Fase 2:
subir cupos en `STRATA`. La planilla pide mirar el video (no solo el texto) y una casilla "la cuenta entera
parece parodia" (señal a nivel de actor — clasificamos contenido por video sobre el texto, no cuentas ni audio).

### Hilos abiertos por Camino (respuesta 2026-06-25, contestada por correo el mismo día)

Además de la validación (punto 1), su correo abrió 4 frentes con seguimiento pendiente:

- **Comportamental / narrativo:** la escucha da el quién/qué; la lectura de emociones/necesidades sale
  mejor con un **codebook compartido** + un pase del modelo que alimente la lectura narrativa de Juan Diego.
  Lo comportamental por Plural lo lleva **Juan**.
- **Formato / algoritmo:** extraíbles del raw pero aún sin exponer — duración (`videoMeta.duration`),
  slideshow vs. video (`isSlideshow`), frecuencia de publicación. Lo visual (rostro vs. generado) es
  lane audiovisual de Camino. La curva de vida (~72h, alcance concentrado) ya conecta con inmunización.
- **Ecosistemas adyacentes** (apuestas / trading-cripto / emprendimiento / productividad): HOY **no
  cubiertos** (keywords no los incluyen; no hay comunidad financiera en la red). Comprometido sin ampliar
  alcance aún: (a) **sondeo barato** sobre el corpus actual (¿creadores/hashtags ya pisan finanzas/apuestas/
  hustle?); (b) barrido acotado de esas keywords **solo si (a) pinta**, decisión conjunta. Puente más cercano
  ya visible: monk mode / sigma grindset. Precedente de método: el cruce fitness→manosfera NO vive en los
  hashtags (2/37) — estas adyacencias se prueban con datos, no se asumen.

## Convenciones

- Ejecutar módulos desde la raíz del repo: `python -m src.modulo.script`
- Los conteos por mes del barrido están sesgados por el scraping (sort LATEST) — no leer como
  crecimiento; para dinámica temporal usar el monitor
- Volumen crudo de keywords sobreestima el fenómeno ~3× — usar la capa clasificada (solo ~35%
  es manosfera sincera). Ese 35% es estimación de gemini **sin validación humana** (plan de validación
  en dos fases arriba: §Validación de la clasificación); no presentarlo como medición con margen de error
- Geo "Latinoamérica" del dashboard = país incl. **Brasil**, excl. **España** (decisión 2026-06-17);
  por idioma el peso hispano es más conservador (~29% es/pt, ~26% sin idioma detectado)
