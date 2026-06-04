"""Genera informe PDF ejecutivo del piloto LIN con gráficas.

Uso:
    .venv/bin/python -m src.analyze.informe_pdf
"""
from __future__ import annotations

import base64
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"

# Colores Plural (del brandbook oficial)
PLURAL_BLACK = "#1a1a1a"
PLURAL_GRAY = "#808080"
PLURAL_LIGHT_GRAY = "#cccccc"
PLURAL_CREAM = "#fff7f0"
# Acentos pasteles
PLURAL_YELLOW = "#fff8ae"
PLURAL_PINK = "#fabbf7"
PLURAL_LILAC = "#c2d1ed"
PLURAL_BLUE = "#c7eafb"
PLURAL_LIME = "#e1fdc5"


def b64img(path: Path) -> str:
    """Convierte imagen a base64 para embed en HTML."""
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{data}"


def generate_charts(tk: pd.DataFrame, rd: pd.DataFrame, yt: pd.DataFrame) -> dict[str, Path]:
    """Genera gráficas y retorna paths."""
    charts_dir = PROCESSED / "charts"
    charts_dir.mkdir(exist_ok=True)

    plt.style.use('seaborn-v0_8-darkgrid')

    # 1. Volumen por plataforma (pie chart)
    fig, ax = plt.subplots(figsize=(6, 4))
    sizes = [len(tk), len(rd), len(yt)]
    labels = ['TikTok', 'Reddit', 'YouTube']
    colors = [PLURAL_YELLOW, PLURAL_LILAC, PLURAL_BLUE]
    ax.pie(sizes, labels=labels, autopct='%1.0f%%', colors=colors, startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
    ax.set_title('Distribución por Plataforma', fontsize=14, fontweight='bold', color=PLURAL_BLACK)
    plt.tight_layout()
    path_pie = charts_dir / 'volumen_plataforma.png'
    plt.savefig(path_pie, dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Top keywords TikTok (horizontal bar)
    top_kw = tk.groupby('keyword').size().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.barh(range(len(top_kw)), top_kw.values, color=PLURAL_PINK)
    ax.set_yticks(range(len(top_kw)))
    ax.set_yticklabels(top_kw.index, fontsize=9, color=PLURAL_BLACK)
    ax.set_xlabel('Posts capturados', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Top 10 Keywords en TikTok', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    plt.tight_layout()
    path_kw = charts_dir / 'top_keywords_tiktok.png'
    plt.savefig(path_kw, dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Geo LATAM vs No-LATAM en TikTok
    latam = tk['is_latam'].fillna(False).sum()
    no_latam = (tk['is_latam'] == False).sum()
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(['LATAM', 'Resto del mundo'], [latam, no_latam], color=[PLURAL_LIME, PLURAL_LIGHT_GRAY])
    ax.set_ylabel('Posts con geo conocido', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Distribución Geográfica LATAM (TikTok)', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    plt.tight_layout()
    path_geo = charts_dir / 'geo_latam.png'
    plt.savefig(path_geo, dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Subreddits por upvotes
    top_subs = rd[rd['mode'] == 'subreddit'].groupby('subreddit_input')['upvotes'].sum().nlargest(8).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(range(len(top_subs)), top_subs.values, color=PLURAL_LILAC)
    ax.set_yticks(range(len(top_subs)))
    ax.set_yticklabels([f"r/{s}" for s in top_subs.index], fontsize=9, color=PLURAL_BLACK)
    ax.set_xlabel('Upvotes acumulados', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Subreddits por Engagement', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    plt.tight_layout()
    path_subs = charts_dir / 'subreddits_engagement.png'
    plt.savefig(path_subs, dpi=150, bbox_inches='tight')
    plt.close()

    # 5. Top Creators TikTok (horizontal bar con plays)
    tk_copy = tk.copy()
    tk_copy['plays'] = pd.to_numeric(tk_copy['plays'], errors='coerce').fillna(0)
    top_creators = tk_copy.groupby('author').agg({'id': 'count', 'plays': 'sum'}).rename(columns={'id': 'posts'})
    top_creators = top_creators[top_creators['posts'] >= 2].nlargest(10, 'plays')  # Min 2 posts

    fig, ax = plt.subplots(figsize=(7, 5))
    y_pos = range(len(top_creators))
    bars = ax.barh(y_pos, top_creators['plays'].values / 1e6, color=PLURAL_YELLOW)  # En millones
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"@{a}" for a in top_creators.index], fontsize=9, color=PLURAL_BLACK)
    ax.set_xlabel('Plays acumulados (millones)', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Top 10 Creadores TikTok', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    # Agregar labels con número de posts
    for i, (idx, row) in enumerate(top_creators.iterrows()):
        ax.text(row['plays'] / 1e6, i, f"  {int(row['posts'])} posts",
                va='center', fontsize=8, color=PLURAL_BLACK, weight='bold')
    plt.tight_layout()
    path_creators = charts_dir / 'top_creators.png'
    plt.savefig(path_creators, dpi=150, bbox_inches='tight')
    plt.close()

    # 6. Timeline de actividad (line chart por día)
    tk_copy['created_at'] = pd.to_datetime(tk_copy['created_at'], errors='coerce')
    tk_timeline = tk_copy.dropna(subset=['created_at']).groupby(tk_copy['created_at'].dt.date).size()

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(tk_timeline.index, tk_timeline.values, color=PLURAL_PINK, linewidth=2.5, marker='o', markersize=5)
    ax.fill_between(tk_timeline.index, tk_timeline.values, alpha=0.2, color=PLURAL_PINK)
    ax.set_xlabel('Fecha', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_ylabel('Posts TikTok', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Actividad Diaria TikTok', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    ax.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    path_timeline = charts_dir / 'timeline.png'
    plt.savefig(path_timeline, dpi=150, bbox_inches='tight')
    plt.close()

    # 7. Engagement Rate por keyword (scatter o bar)
    # Calculamos engagement rate = (likes + comments) / plays
    kw_engagement = tk_copy.groupby('keyword').apply(
        lambda g: ((g['likes'].sum() + g['comments'].sum()) / g['plays'].sum() * 100)
        if g['plays'].sum() > 0 else 0
    ).nlargest(10).sort_values()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.barh(range(len(kw_engagement)), kw_engagement.values, color=PLURAL_LILAC)
    ax.set_yticks(range(len(kw_engagement)))
    ax.set_yticklabels(kw_engagement.index, fontsize=9, color=PLURAL_BLACK)
    ax.set_xlabel('Engagement Rate (%)', fontsize=10, fontweight='bold', color=PLURAL_BLACK)
    ax.set_title('Top Keywords por Engagement Rate', fontsize=12, fontweight='bold', color=PLURAL_BLACK)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PLURAL_GRAY)
    ax.spines['bottom'].set_color(PLURAL_GRAY)
    for i, val in enumerate(kw_engagement.values):
        ax.text(val, i, f'  {val:.2f}%', va='center', fontsize=8, color=PLURAL_BLACK, weight='bold')
    plt.tight_layout()
    path_engagement = charts_dir / 'engagement_rate.png'
    plt.savefig(path_engagement, dpi=150, bbox_inches='tight')
    plt.close()

    return {
        'volumen': path_pie,
        'keywords': path_kw,
        'geo': path_geo,
        'subreddits': path_subs,
        'creators': path_creators,
        'timeline': path_timeline,
        'engagement': path_engagement,
    }


TEMPLATE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>
  @page { size: A4; margin: 11mm 12mm; }
  * { box-sizing: border-box; }
  body { font-family: 'FK Grotesk', 'Helvetica Neue', Arial, sans-serif; color: {{BLACK}}; font-size: 10px; line-height: 1.4; margin: 0; }
  h1,h2,h3 { margin: 0; }
  .head { border-bottom: 2px solid {{BLACK}}; padding-bottom: 7px; margin-bottom: 9px; }
  .brand { font-size: 10px; letter-spacing: 3px; color: {{GRAY}}; font-weight: 600; text-transform: uppercase; }
  .title { font-size: 19px; font-weight: 700; margin-top: 3px; line-height: 1.15; color: {{BLACK}}; }
  .sub { color: {{GRAY}}; font-size: 9.5px; margin-top: 4px; }
  .lead { background: {{CREAM}}; border-left: 3px solid {{YELLOW}}; padding: 7px 11px; margin: 8px 0 9px;
          font-size: 10.2px; color: {{BLACK}}; }
  .kpis { display: flex; gap: 8px; margin: 9px 0; }
  .kpi { flex: 1; border-radius: 6px; padding: 8px 10px; }
  .kpi .n { font-size: 19px; font-weight: 800; line-height: 1; color: {{BLACK}}; }
  .kpi .l { font-size: 8px; margin-top: 4px; text-transform: uppercase; letter-spacing: .4px; color: {{BLACK}}; opacity: .7; }
  .kpi:nth-child(1) { background: {{YELLOW}}; }
  .kpi:nth-child(2) { background: {{PINK}}; }
  .kpi:nth-child(3) { background: {{LILAC}}; }
  .kpi:nth-child(4) { background: {{BLUE}}; }
  h2 { font-size: 12px; color: {{BLACK}}; margin: 11px 0 5px; padding-bottom: 3px; border-bottom: 1px solid {{GRAY}}; font-weight: 700; }
  .row { display: flex; gap: 12px; align-items: flex-start; }
  .col { flex: 1; }
  img.chart { width: 100%; border: 1px solid #eee; border-radius: 5px; }
  p { margin: 6px 0; }
  .tag { display:inline-block; background: {{LIME}}; color: {{BLACK}}; border-radius: 10px; padding: 1px 8px;
         font-size: 8.4px; font-weight:600; margin: 2px 3px 2px 0;}
  ul { margin: 5px 0; padding-left: 16px; }
  li { margin: 3px 0; }
  .highlight { background: {{CREAM}}; border-radius: 6px; padding: 9px 12px; margin-top: 6px; border: 1px solid {{LIGHT_GRAY}}; }
  .highlight h3 { color: {{BLACK}}; font-size: 10.5px; margin-bottom: 4px; font-weight: 700; }
  .small { font-size: 8.8px; color: {{GRAY}}; }
  .foot { margin-top: 12px; border-top: 1px solid {{LIGHT_GRAY}}; padding-top: 7px; color: {{GRAY}}; font-size: 8px; }
  .caso { border-left: 3px solid {{PINK}}; padding-left: 8px; margin: 6px 0; background: {{CREAM}}; padding: 8px; border-radius: 4px; }
  .caso h4 { color: {{BLACK}}; font-size: 10px; margin: 0 0 2px; font-weight: 700; }
  .caso p { font-size: 9px; margin: 2px 0; color: {{BLACK}}; }
  .caso a { color: {{GRAY}}; text-decoration: underline; font-size: 8px; word-break: break-all; }
</style></head><body>

<div class="head">
  <div class="brand">PLURAL + CAMINO</div>
  <div class="title">Piloto Social Listening · Manosfera en Colombia</div>
  <div class="sub"><b>Proyecto:</b> LIN para propuesta Banco Mundial &nbsp;·&nbsp; <b>Ventana:</b> {{ window }}</div>
  <div class="sub" style="margin-top:2px"><b>Elaborado:</b> {{ generated }} por Daniel Otero (Plural)</div>
</div>

<div class="lead">
  <b>Validamos la factibilidad técnica</b> de un sistema de social listening enfocado en narrativas de la manosfera,
  capturando <b>{{ total }} items</b> en <b>11 días</b> a través de TikTok, Reddit y YouTube.
  Las keywords hispanas muestran <b>75-86% penetración LATAM</b>, validando la tesis de migración inglés→español.
</div>

<div class="kpis">
  <div class="kpi"><div class="n">{{ tk_count }}</div><div class="l">TikTok Posts</div></div>
  <div class="kpi alt"><div class="n">{{ rd_count }}</div><div class="l">Reddit Items</div></div>
  <div class="kpi"><div class="n">{{ yt_count }}</div><div class="l">YouTube Videos</div></div>
  <div class="kpi alt"><div class="n">{{ latam_pct }}%</div><div class="l">Geo LATAM (TikTok)</div></div>
</div>

<h2>Distribución por Plataforma</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.volumen }}"></div>
  <div class="col">
    <p><b>TikTok ({{ tk_count }} posts):</b> contenido viral con geo-localización y detección de idioma.
       Keywords hispanas como <em>hombre alfa</em> (86% LATAM) y <em>pildora roja</em> (85% LATAM) validan la tesis.</p>
    <p><b>Reddit ({{ rd_count }} items):</b> conversaciones profundas (242 posts + 735 comentarios).
       Ángulo gamer anti-woke activo en r/KotakuInAction (369 upvotes, controversia James Bond).</p>
    <p><b>YouTube ({{ yt_count }} videos):</b> contenido analítico largo-forma.
       Transcripciones automáticas disponibles para análisis de discurso verbal.</p>
  </div>
</div>

<h2>TikTok — Creadores Emergentes LATAM</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.keywords }}"></div>
  <div class="col">
    <div class="caso">
      <h4>@growingmind.arg (Argentina)</h4>
      <p><b>2.85M plays</b> en "hipergamia" (9 días) · 163K likes · 256 comentarios</p>
      <p>Creador emergente con alcance viral sobre narrativas manosfera en español.</p>
    </div>
    <p class="small"><b>Top keywords hispanas:</b></p>
    <ul class="small">
      <li><b>hombre alfa:</b> 64 posts · 2.6M plays · <b>86% geo LATAM</b></li>
      <li><b>hombre de alto valor:</b> 64 posts · 1.1M plays · <b>75% geo LATAM</b></li>
      <li><b>crisis de masculinidad:</b> 30 posts · 1.7M plays · <b>70% LATAM, 83% español</b></li>
    </ul>
  </div>
</div>

<h2>Penetración LATAM Cuantificable</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.geo }}"></div>
  <div class="col">
    <p>De los <b>{{ geo_total }} posts con geo conocido</b>, <b>{{ latam_count }} ({{ latam_pct }}%) son LATAM</b>.
       Top países: México (113 posts), España (29), Brasil (18).</p>
    <p><b>Comparación anglo vs hispano:</b></p>
    <ul class="small">
      <li><em>hombre alfa</em>: <b>86% LATAM</b> vs <em>alpha male</em>: 6% LATAM</li>
      <li><em>pildora roja</em>: <b>85% LATAM</b> vs <em>red pill</em>: 19% LATAM</li>
    </ul>
    <p><b>Conclusión:</b> la migración de narrativas manosfera de inglés a español es medible y significativa.</p>
  </div>
</div>

<h2>Reddit — Ángulo Gamer Activo</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.subreddits }}"></div>
  <div class="col">
    <p><b>r/Gaming + r/KotakuInAction:</b> 103 items, <b>3,280 upvotes</b> (52% del total Reddit).</p>
    <div class="caso">
      <h4>Controversia James Bond 2026</h4>
      <p><b>369 upvotes</b> · 96 comentarios · r/KotakuInAction</p>
      <p>"Actual screenshot of a James Bond game in 2026" — discurso anti-woke sobre diseño de personajes.</p>
    </div>
    <p class="small"><b>Keywords gamer:</b> 96 items en Reddit vs solo 31 en TikTok.
       El ángulo gamer anti-woke vive en Reddit, no TikTok.</p>
  </div>
</div>

<h2>YouTube — Cobertura Mainstream</h2>
<p>Keyword destacada: <b>"crisis de masculinidad"</b> con 22 videos (44% del total YouTube capturado).</p>
<div class="highlight">
  <h3>Documentales BBC (93K + 80K views)</h3>
  <ul class="small">
    <li><b>BBC World Service:</b> "My brother copied everything from Andrew Tate" (93K views, 1.2K comentarios)</li>
    <li><b>BBC News Mundo:</b> "Los mesías de la machosfera" (80K views, 2K comentarios, <b>español</b>)</li>
  </ul>
  <p class="small"><b>Valor diferencial YouTube:</b> transcripciones automáticas disponibles → análisis de discurso verbal largo-forma (vs clips cortos TikTok).</p>
</div>

<h2>Top Creadores TikTok</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.creators }}"></div>
  <div class="col">
    <p><b>10 creadores con más impacto</b> (mínimo 2 posts en ventana).</p>
    <p class="small"><b>Ejemplos destacados:</b></p>
{{ top_creators_examples }}
    <p class="small">La concentración en pocos creadores indica que la narrativa manosfera tiene <b>portavoces consistentes</b> en TikTok,
       no solo viralidad ocasional.</p>
  </div>
</div>

<h2>Análisis Temporal</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.timeline }}"></div>
  <div class="col">
    <p>Actividad diaria en TikTok durante la ventana 18-29 mayo.</p>
    <p class="small"><b>Observación:</b> {{ timeline_observation }}</p>
    <p class="small">El timeline permite detectar momentos virales o reacción a eventos externos
       (controversias, tendencias globales). Útil para análisis de coyuntura en fases futuras.</p>
  </div>
</div>

<h2>Engagement Rate — Qué Funciona</h2>
<div class="row">
  <div class="col"><img class="chart" src="{{ img.engagement }}"></div>
  <div class="col">
    <p><b>Engagement rate = (likes + comentarios) / plays × 100</b></p>
    <p class="small">Ir más allá del volumen: identificar qué keywords generan <b>interacción real</b>, no solo vistas pasivas.</p>
{{ top_engagement_examples }}
    <p class="small">Keywords con alto engagement indican temas que <b>resuenan emocionalmente</b> con la audiencia,
       no solo viralidad algorítmica.</p>
  </div>
</div>

<h2>Conclusiones</h2>
<div class="highlight">
  <h3>✅ Validaciones Técnicas</h3>
  <ul class="small">
    <li><b>Keywords hispanas funcionan:</b> 75-86% geo LATAM, validación cuantitativa de la tesis de Camino</li>
    <li><b>Multi-plataforma es crítica:</b> TikTok (viral), Reddit (conversacional), YouTube (analítico) se complementan</li>
    <li><b>Casos narrables identificados:</b> @growingmind.arg (2.85M plays), controversia James Bond, BBC documentales</li>
    <li><b>Volumen robusto:</b> 1,947 items en 11 días → proyección ~7,000 items/mes</li>
  </ul>

  <h3>⚠️ Limitaciones Detectadas (Solucionables)</h3>
  <ul class="small">
    <li><b>Reddit rate limiting:</b> requiere proxies residential (~$10-15/mes adicionales)</li>
    <li><b>YouTube bajo volumen reciente:</b> solo 4% en ventana → aumentar límite 50→150 videos/kw</li>
    <li><b>TikTok 30% idioma sin detectar:</b> inferencia post-hoc con fastText/langdetect</li>
  </ul>
</div>

<div class="foot">
  <b>Metodología.</b> Captura de contenido público en TikTok, Reddit y YouTube mediante scraping vía Apify
  (actores clockworks/tiktok-scraper, trudax/reddit-scraper-lite, streamers/youtube-scraper).
  20 keywords agrupadas en categorías (identitarias, emocionales, estéticas, gamer) + 8 subreddits.
  Filtrado por ventana temporal {{ window }}. Análisis de geo-localización, idioma y engagement.
  CSVs estructurados disponibles en data/processed/. Costo real del barrido: $6.13 USD (59 runs Apify).
  <br><br>
  <b>Elaborado por:</b> Daniel Otero (Estudio Plural) para propuesta Banco Mundial en colaboración con Camino
  (Laura Franco, Directora de Estrategia Digital). Contacto: hola@plural-estudio.co
</div>

</body></html>"""


def main() -> int:
    # Cargar datos
    tk = pd.read_csv(PROCESSED / "tiktok_posts.csv")
    rd = pd.read_csv(PROCESSED / "reddit_items.csv")
    yt = pd.read_csv(PROCESSED / "youtube_videos.csv")

    print("[informe_pdf] generando gráficas...")
    charts = generate_charts(tk, rd, yt)

    # Métricas
    total = len(tk) + len(rd) + len(yt)
    latam_count = int(tk['is_latam'].fillna(False).sum())
    geo_total = int(tk['location'].notna().sum())
    latam_pct = round(100 * latam_count / geo_total) if geo_total else 0

    # Top creators examples (top 3 con links)
    tk_copy = tk.copy()
    tk_copy['plays'] = pd.to_numeric(tk_copy['plays'], errors='coerce').fillna(0)
    top_creators_df = tk_copy.groupby('author').agg({'id': 'count', 'plays': 'sum'}).rename(columns={'id': 'posts'})
    top_creators_df = top_creators_df[top_creators_df['posts'] >= 2].nlargest(3, 'plays')

    creators_html = ""
    for author, row in top_creators_df.iterrows():
        author_posts = tk_copy[tk_copy['author'] == author].nlargest(1, 'plays')
        if not author_posts.empty:
            top_post = author_posts.iloc[0]
            url = top_post.get('url', '#')
            plays_m = row['plays'] / 1e6
            creators_html += f"""    <div class="caso">
      <h4>@{author}</h4>
      <p><b>{plays_m:.2f}M plays acumulados</b> · {int(row['posts'])} posts</p>
      <p class="small"><a href="{url}" target="_blank">{url[:60]}...</a></p>
    </div>\n"""

    # Timeline observation
    tk_copy['created_at'] = pd.to_datetime(tk_copy['created_at'], errors='coerce')
    tk_timeline = tk_copy.dropna(subset=['created_at']).groupby(tk_copy['created_at'].dt.date).size()
    if not tk_timeline.empty:
        peak_day = tk_timeline.idxmax()
        peak_count = tk_timeline.max()
        timeline_obs = f"Pico de actividad el {peak_day.strftime('%d %b')} con {peak_count} posts."
    else:
        timeline_obs = "Actividad distribuida uniformemente."

    # Engagement rate examples (top 3 keywords con posts destacados)
    kw_engagement = tk_copy.groupby('keyword').apply(
        lambda g: ((g['likes'].sum() + g['comments'].sum()) / g['plays'].sum() * 100)
        if g['plays'].sum() > 0 else 0
    ).nlargest(3)

    engagement_html = ""
    for kw, rate in kw_engagement.items():
        kw_posts = tk_copy[tk_copy['keyword'] == kw].nlargest(1, 'plays')
        if not kw_posts.empty:
            top_post = kw_posts.iloc[0]
            url = top_post.get('url', '#')
            engagement_html += f"""    <div class="caso">
      <h4>{kw} ({rate:.2f}% engagement)</h4>
      <p class="small">Top post: <a href="{url}" target="_blank">{url[:60]}...</a></p>
    </div>\n"""

    # Render HTML
    html = Template(TEMPLATE).render(
        BLACK=PLURAL_BLACK, GRAY=PLURAL_GRAY, LIGHT_GRAY=PLURAL_LIGHT_GRAY,
        CREAM=PLURAL_CREAM, YELLOW=PLURAL_YELLOW, PINK=PLURAL_PINK,
        LILAC=PLURAL_LILAC, BLUE=PLURAL_BLUE, LIME=PLURAL_LIME,
        total=f"{total:,}",
        tk_count=f"{len(tk):,}",
        rd_count=f"{len(rd):,}",
        yt_count=len(yt),
        latam_count=latam_count,
        geo_total=geo_total,
        latam_pct=latam_pct,
        window="18-29 mayo 2026",
        generated=datetime.now().strftime("%d %b %Y"),
        img={k: b64img(v) for k, v in charts.items()},
        top_creators_examples=creators_html,
        timeline_observation=timeline_obs,
        top_engagement_examples=engagement_html,
    )

    html_path = PROCESSED / "informe_lin.html"
    html_path.write_text(html, encoding="utf-8")

    print("[informe_pdf] generando PDF...")
    from weasyprint import HTML
    pdf_path = PROCESSED / "informe_lin.pdf"
    HTML(string=html).write_pdf(str(pdf_path))

    print(f"[informe_pdf] → {html_path}")
    print(f"[informe_pdf] → {pdf_path}  ({pdf_path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
