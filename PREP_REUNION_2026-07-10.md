# Prep — reunión Camino, viernes 2026-07-10

Insumos para los 3 puntos que pidió Camino (correo 2026-07-08). Estado: (1) validación y
(2) sondeo adyacencias **listos**; (3) lectura comportamental **en construcción** (no la traemos cerrada).

---

## 1. Validación de la clasificación (Fase 1)

**Qué devolvió Camino:** doble anotación de los 30 videos frontera (hojas `Etiquetado 1` y `Etiquetado 2`).
El Anotador 1 dejó 8 sin etiquetar: **7 por barrera de idioma** (contenido no-hispano, portugués/Brasil) y
1 por cuenta privada → 22 usables. El Anotador 2 etiquetó los 30.

**Recordar el diseño:** el set está cargado **a propósito a la frontera de baja confianza**
(`sincera ↔ ambiguo ↔ contra_crítica ↔ falso_positivo`). Los números de abajo son el **caso más difícil**,
NO la accuracy del corpus. En el corpus completo (con los casos obvios de alta confianza) el acuerdo sería
bastante mayor.

| Comparación | Acuerdo | κ (Cohen) | Lectura |
|---|---|---|---|
| Humano ↔ Humano (6 clases) | 45% | **0.28** | *fair* — la tarea es ambigua en la frontera |
| Humano ↔ Humano (binario "sincera vs. resto") | 73% | 0.43 | mejor al simplificar la decisión |
| Humano ↔ Modelo (6 clases) | 30–36% | 0.13–0.23 | bajo, pero medido en el subconjunto más duro |

**Los tres mensajes:**

1. **La κ humano-humano baja es el hallazgo, no un fracaso.** Dos personas con las mismas instrucciones
   solo coinciden 45% en la frontera → buena parte del "error" es **ambigüedad de la tarea, no del modelo**.
   Fase 1 servía exactamente para separar esas dos cosas, y lo logró: nos dice *dónde* apretar antes de escalar.
2. **Sesgo entre anotadores:** A1 tiende a "falso positivo" (10 de 22), A2 a "manosfera sincera" (13 de 30).
   No interpretaron igual el límite → el **codebook / las instrucciones necesitan una pasada** (definiciones más
   duras, ejemplos de borde, regla para contenido no-hispano).
3. **n = 22–30 no da número reportable** (IC enorme con 6 clases). Eso siempre fue el rol de la **Fase 2**
   (~100–150 videos) para un κ estable y accuracy con margen.

**Errores claros del modelo** (donde AMBOS humanos coincidieron y el modelo difirió — 5 de 10 casos de consenso):

| # | conf. modelo | Modelo dijo | Humanos (consenso) |
|---|---|---|---|
| 2 | 0.75 | Contra-crítica | Manosfera sincera |
| 6 | 0.20 | Ambiguo | Manosfera sincera |
| 27 | 0.50 | Ambiguo | Manosfera sincera |
| 10 | 0.70 | Medio / periodismo | Contra-crítica |
| 20 | 0.70 | Sátira / humor | Falso positivo |

→ Dirección incipiente: en la frontera el modelo tiende a **sub-etiquetar "sincera"** (la manda a
contra/ambiguo). Si se confirma en Fase 2, el 35% sería un **piso**, no un techo. Con n=10 es señal, no medida.

**Acciones antes de Fase 2:** (a) afinar codebook con estos casos de borde; (b) evaluar **colapsar clases**
(p. ej. binario sincera/no) para la métrica principal; (c) regla explícita para contenido no-hispano;
(d) completar hasta ~100–150 para κ y accuracy reportables.

---

## 2. Sondeo de ecosistemas adyacentes — punto (a)

**Pregunta de Camino:** ¿los creadores/hashtags del corpus actual ya pisan **apuestas, trading/cripto,
emprendimiento, productividad**? Método: se **mide sobre el corpus ya clasificado** (742 videos), no se asume —
mismo rigor que el precedente fitness→manosfera ("2/37 hashtags"). Búsqueda por léxico en texto + hashtags,
cuantificando el cruce **con la manosfera sincera**. (`python -m src.analyze.probe_adyacencias`)

| Ecosistema | Videos (corpus) | En manosfera sincera | Creadores puente |
|---|---|---|---|
| **Productividad / mentalidad** | **57 (8%)** | **46** | **40** |
| Apuestas | 0 | 0 | 0 |
| Trading / cripto | 0 | 0 | 0 |
| Emprendimiento / dinero | 0 | 0 | 0 |

- El **único puente vivo es productividad/mentalidad**, y es fuerte: lo disparan
  `sigma ×20`, `monk mode ×19`, `disciplina`, `mindset`, `estoico/estoicismo`, `grindset`. 40 creadores mezclan
  manosfera sincera con este discurso — es el brazo "superación personal / disciplina" de la manosfera.
- Apuestas, trading/cripto y emprendimiento dan **cero**. Verificado con raíces amplias (substring): `negocio`,
  `emprend`, `invert`, `cripto`, `bitcoin`, `trading`, `apuest`, `casino`, `forex`, `hustle` → sin señal;
  solo aparecen `dinero ×3` y `rico ×3`, marginales. No es un artefacto del léxico: no está en los datos.

**Caveat clave (para no sobre-leer):** el corpus se muestreó **por keywords de manosfera**, así que solo puede
revelar adyacencias que los propios creadores manosfera hacen aflorar. La ausencia de apuestas/trading/negocio
en ESTE corpus **no prueba** ausencia del puente en el fenómeno — lo probaría el **barrido (b)** de esas keywords.

**Recomendación para decidir juntos (b):** productividad ya está *dentro*, no hace falta barrido. Para
apuestas/trading/emprendimiento el sondeo (a) dice "no aflora solo" → si a Camino le interesa esa hipótesis,
tiene sentido un **barrido acotado (b)** de esas keywords para testearla con datos; si no, no gastamos alcance.
Decisión conjunta en la reunión.

---

## 3. Lectura comportamental — en construcción

No la traemos cerrada. Encuadre: la escucha da el **quién/qué**; la lectura de emociones/creencias/vulnerabilidades
sale mejor con un **codebook compartido** + un pase del modelo que alimente la lectura narrativa, y engancha con
el rastreo de rutas del algoritmo que Camino trae. Proponer acordar el codebook en la reunión como siguiente paso.
