# LIN — Resumen Ejecutivo para Propuesta Banco Mundial

**Fecha:** 2026-05-30  
**Piloto:** Social Listening Manosfera Colombia (Plural + Camino)  
**Ventana analizada:** 2026-05-18 a 2026-05-29 (11 días efectivos)

---

## 🎯 Objetivo del Barrido

Validar **factibilidad técnica** y **volumen de datos** para piloto LIN antes de comprometernos con Camino y el Banco Mundial en la propuesta final.

---

## ✅ Resultados — Validación Exitosa

### Volumen Capturado
| Plataforma | Items | Keywords | Cobertura |
|------------|-------|----------|-----------|
| **TikTok** | 920 posts | 20 | ✅ Alta (40-50% en ventana) |
| **Reddit** | 977 items | 19 | ✅ Completa (242 posts + 735 comentarios) |
| **YouTube** | 50 videos | 20 | ⚠️ Baja (4% en ventana — plataforma evergreen) |
| **TOTAL** | **1,947 items** | **20** | **11 días** |

**Costo real:** $6.13 USD (59 runs Apify)

---

## 📊 Hallazgos Clave

### 1. Las keywords hispanas validan la tesis de Camino
**Penetración LATAM:**
- `hombre alfa`: **86% geo LATAM** (vs 6% en `alpha male`)
- `pildora roja`: **85% geo LATAM** (vs 19% en `red pill`)
- `crisis de masculinidad`: **70% geo LATAM**, **83% idioma español**

**Conclusión:** La migración inglés→español de narrativas manosfera es cuantificable.

### 2. Caso narrable: @growingmind.arg
- **Creador:** argentino emergente
- **Video top:** "hipergamia" con **2.85M plays** en 9 días
- **Engagement:** 163K likes, 256 comentarios
- **Idioma detectado:** `un` (sin detectar — requiere inferencia, oportunidad de mejora)

**Uso para propuesta:** ejemplifica creador hispano con alcance viral sobre narrativas manosfera.

### 3. Ángulo gamer activo en Reddit (no TikTok)
- **r/KotakuInAction + r/Gaming:** 103 items, 3,280 upvotes acumulados
- **Top post:** controversia James Bond 2026 (369 upvotes, 96 comentarios)
- **Keywords gamer** (`simp`, `soyboy`, `e-girl`): 31 posts TikTok vs 96 items Reddit

**Conclusión:** el ángulo gamer anti-woke vive en Reddit, no TikTok — cobertura multi-plataforma es crítica.

### 4. YouTube = oro para análisis de discurso
- **Bajo volumen reciente** (50 videos en 11 días) PERO
- **Transcripciones automáticas disponibles** → acceso a contenido verbal largo-forma
- **Top videos:** BBC documentales (93K + 80K views) sobre "mesías de la machosfera"

**Keyword destacada:** `crisis de masculinidad` con **22 videos** (44% del total YouTube capturado)

---

## 💰 Proyección de Costos (Mes Completo)

### Opción recomendada: TikTok + Reddit + YouTube
- **Volumen:** ~7,300 items/mes (2,500 TikTok + 2,700 Reddit + 150 YouTube)
- **Costo:** **$21-27/mes** (Apify compute)
- **Con comentarios YouTube:** +$4.50/mes → **$26-32/mes** (~12,300 items/mes)

### Comparación brutal:
- **Apify (nuestra opción):** $21-32/mes
- **X API Pro:** $5,000/mes
- **Ahorro:** **156-239× más barato**

---

## 🚀 Entregables para el Banco Mundial

### 1. Volumen estadísticamente robusto
- 7,000-12,000 items/mes
- Distribuido en 3 plataformas (visual, conversacional, largo-forma)

### 2. Cobertura multi-modal diferenciada
- **TikTok:** tendencias virales + geo/idioma + creadores emergentes
- **Reddit:** conversaciones gamer + discurso explícito manosfera + threads completos
- **YouTube:** análisis verbal profundo vía transcripciones automáticas

### 3. Casos narrables identificados
- @growingmind.arg (2.85M plays)
- BBC documentales (93K + 80K views)
- r/KotakuInAction (369 upvotes, controversia James Bond)
- Keywords hispanas con 75-86% penetración LATAM

### 4. Argumento de eficiencia brutal
- **$21-32/mes** vs $5,000/mes (X API)
- Mismo valor analítico, **1/200 del costo**

---

## ⚠️ Limitaciones Técnicas Detectadas (Y Soluciones)

### 1. Reddit — Rate Limiting
**Problema:** 403s al intentar scraping intenso  
**Solución:** Proxies residential (~$10-15/mes adicionales)  
**Estado:** solucionable, costo bajo

### 2. YouTube — Bajo Volumen Reciente
**Problema:** solo 4% de videos caen en ventana de 12 días  
**Solución:** aumentar límite a 150 videos/keyword (vs 50 actual)  
**Costo adicional:** $0.03/mes (despreciable)

### 3. TikTok — 30% sin idioma detectado
**Problema:** campo `language: "un"` requiere inferencia post-hoc  
**Solución:** usar modelo de detección de idioma (fastText/langdetect) en procesamiento  
**Costo:** $0 (open source)

---

## 🎯 Recomendación Final

### Scope del piloto 4 semanas:
✅ **TikTok + Reddit + YouTube**  
❌ **Twitch** (fuera — sin acceso a chat, ROI bajo)  
❌ **Discord** (fuera — requiere bot custom, scope futuro)

### Presupuesto mes piloto:
- **Captura:** $21-32/mes (Apify)
- **Proxies Reddit:** $10-15/mes
- **TOTAL técnico:** **$31-47/mes**
- **Tiempo análisis/reportería:** (a definir con Juan)

### Entregable para Camino/Banco Mundial:
- **Volumen:** 7,000-12,000 items/mes
- **Cobertura:** 3 plataformas complementarias
- **Costo:** <$50/mes (vs $5,000/mes alternativas)
- **Narrativas:** casos concretos ya identificados

---

## 📎 Archivos Generados

### Datos estructurados:
- `data/processed/tiktok_posts.csv` (920 rows)
- `data/processed/reddit_items.csv` (977 rows)
- `data/processed/youtube_videos.csv` (50 rows)

### Reportes:
- `data/processed/report.md` (análisis completo con tablas)
- `ANALISIS_AMPLIADO_0530.md` (hallazgos técnicos + proyecciones)

### Scripts reproducibles:
- `src/scrape/tiktok.py`
- `src/scrape/reddit.py`
- `src/scrape/youtube.py`
- `src/analyze/report.py`

---

**Siguiente paso:** Enviar actualización a Laura Franco (Camino) con estos números + casos narrables + propuesta de scope final.

**Contacto Laura:**  
lfranco@somoscamino.co (Especialista en estrategia e innovación digital)
