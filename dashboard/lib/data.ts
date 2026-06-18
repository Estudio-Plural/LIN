// Tipos + constantes + helpers de agregación para el dashboard LIN.

export type Video = {
  id: string;
  category: string;
  keyword: string;
  author: string | null;
  nick: string | null;
  fans: number | null;
  created: string;
  month: string;
  plays: number;
  likes: number;
  comments: number;
  shares: number;
  loc: string | null;
  is_latam: boolean;
  lang: string | null;
  text: string;
  hashtags: string[];
  url: string;
  label: string | null;
  subtema: string | null;
  razon: string | null;
};

export type Meta = {
  total_videos: number;
  period: { start: string; end: string };
  total_plays: number;
  n_creators: number;
  pct_latam: number | null;
  classified: boolean;
  label_dist: Record<string, number>;
  generated_at: string;
  caveats: string[];
};

export type GraphNode = {
  id: string;
  freq: number;
  community: number;
  color: string;
  x?: number;
  y?: number;
};
export type GraphLink = { source: string; target: string; weight: number };
export type Community = {
  id: number;
  anchor: string;
  name: string;
  auto: string;
  color: string;
  hashtags: string[];
  n_hashtags: number;
  n_videos: number;
  share: number;
  plays: number;
  label_dist: Record<string, number>;
  dominant_label: string | null;
  top_creators: string[];
  desc: string;
};
export type NetworkData = {
  hashtag: { nodes: GraphNode[]; links: GraphLink[] };
  communities: Community[];
  meta: { n_videos: number; assigned: number; coverage_pct: number; n_communities: number };
};

// Orden de etiquetas para barras señal→ruido (señal primero).
export const LABEL_ORDER = [
  "manosfera_sincera",
  "contra_critica",
  "satira_humor",
  "ambiguo",
  "medio_periodismo",
  "falso_positivo",
];

export const CATEGORY_LABELS: Record<string, string> = {
  identitarias: "Identitarias",
  emocionales: "Emocionales",
  esteticas: "Estéticas",
  gamer: "Gamer",
};

export const CATEGORY_COLORS: Record<string, string> = {
  identitarias: "#fb7185",
  emocionales: "#fbbf24",
  esteticas: "#a78bfa",
  gamer: "#22d3ee",
};

export const LABEL_META: Record<string, { es: string; color: string; noise: boolean }> = {
  manosfera_sincera: { es: "Manosfera sincera", color: "#ef4444", noise: false },
  contra_critica: { es: "Contra-crítica", color: "#34d399", noise: true },
  satira_humor: { es: "Sátira / humor", color: "#fbbf24", noise: true },
  medio_periodismo: { es: "Medio / periodismo", color: "#60a5fa", noise: true },
  falso_positivo: { es: "Falso positivo", color: "#71717a", noise: true },
  ambiguo: { es: "Ambiguo", color: "#a1a1aa", noise: true },
};

export const SUBTEMA_LABELS: Record<string, string> = {
  alto_valor: "Alto valor",
  alfa: "Alfa / sigma",
  looksmax: "Looksmaxxing",
  red_pill: "Red pill",
  hipergamia: "Hipergamia",
  antifeminismo: "Antifeminismo",
  fitness: "Fitness / disciplina",
  gaming: "Gaming",
  otro: "Otro",
};

export function fmtNum(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + "k";
  return String(Math.round(n));
}

export function median(nums: number[]): number {
  if (!nums.length) return 0;
  const s = [...nums].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
}

export function aggregateByCategory(videos: Video[]) {
  const cats = ["identitarias", "emocionales", "esteticas", "gamer"];
  return cats
    .map((c) => {
      const vs = videos.filter((v) => v.category === c);
      const geo = vs.filter((v) => v.loc);
      return {
        category: c,
        label: CATEGORY_LABELS[c] ?? c,
        color: CATEGORY_COLORS[c],
        videos: vs.length,
        plays: vs.reduce((s, v) => s + v.plays, 0),
        playsMedian: median(vs.map((v) => v.plays)),
        pctLatam: geo.length ? Math.round((100 * geo.filter((v) => v.is_latam).length) / geo.length) : 0,
        pctEsPt: vs.length
          ? Math.round((100 * vs.filter((v) => v.lang === "es" || v.lang === "pt").length) / vs.length)
          : 0,
      };
    })
    .filter((c) => c.videos > 0);
}

export function byCountry(videos: Video[], topN = 12) {
  const counts = new Map<string, number>();
  for (const v of videos) if (v.loc) counts.set(v.loc, (counts.get(v.loc) ?? 0) + 1);
  return [...counts.entries()]
    .map(([country, count]) => ({ country, count, isLatam: videos.find((v) => v.loc === country)?.is_latam ?? false }))
    .sort((a, b) => b.count - a.count)
    .slice(0, topN);
}

export function byKeywordEngagement(videos: Video[]) {
  const map = new Map<string, Video[]>();
  for (const v of videos) {
    if (!map.has(v.keyword)) map.set(v.keyword, []);
    map.get(v.keyword)!.push(v);
  }
  return [...map.entries()]
    .map(([keyword, vs]) => ({
      keyword,
      category: vs[0].category,
      n: vs.length,
      playsMedian: median(vs.map((v) => v.plays)),
      playsTotal: vs.reduce((s, v) => s + v.plays, 0),
    }))
    .sort((a, b) => b.playsMedian - a.playsMedian);
}

export function labelDistribution(videos: Video[]) {
  const counts = new Map<string, number>();
  for (const v of videos) if (v.label) counts.set(v.label, (counts.get(v.label) ?? 0) + 1);
  return [...counts.entries()]
    .map(([label, count]) => ({ label, count, ...LABEL_META[label] }))
    .sort((a, b) => b.count - a.count);
}

// Para "señal vs ruido": por keyword, conteo de cada label (stacked).
export function labelByKeyword(videos: Video[]) {
  const map = new Map<string, Record<string, number>>();
  for (const v of videos) {
    if (!v.label) continue;
    if (!map.has(v.keyword)) map.set(v.keyword, {});
    const row = map.get(v.keyword)!;
    row[v.label] = (row[v.label] ?? 0) + 1;
  }
  return [...map.entries()]
    .map(([keyword, counts]) => ({ keyword, total: Object.values(counts).reduce((a, b) => a + b, 0), ...counts }))
    .sort((a, b) => b.total - a.total);
}

// Subtemas dentro de los videos clasificados como manosfera sincera.
export function subtopicsOfSignal(videos: Video[]) {
  const sinceras = videos.filter((v) => v.label === "manosfera_sincera");
  const map = new Map<string, Video[]>();
  for (const v of sinceras) {
    const s = v.subtema ?? "otro";
    if (!map.has(s)) map.set(s, []);
    map.get(s)!.push(v);
  }
  const total = sinceras.length;
  return [...map.entries()]
    .map(([subtema, vs]) => ({
      subtema,
      label: SUBTEMA_LABELS[subtema] ?? subtema,
      count: vs.length,
      share: total ? Math.round((100 * vs.length) / total) : 0,
      playsMedian: median(vs.map((v) => v.plays)),
    }))
    .sort((a, b) => b.count - a.count);
}

export function topCreators(videos: Video[], topN = 12) {
  const map = new Map<string, Video[]>();
  for (const v of videos) {
    if (!v.author) continue;
    if (!map.has(v.author)) map.set(v.author, []);
    map.get(v.author)!.push(v);
  }
  return [...map.entries()]
    .map(([author, vs]) => {
      const top = vs.reduce((a, b) => (b.plays > a.plays ? b : a));
      const labels = vs.map((v) => v.label).filter(Boolean) as string[];
      const labelCounts = new Map<string, number>();
      for (const l of labels) labelCounts.set(l, (labelCounts.get(l) ?? 0) + 1);
      const majority = [...labelCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
      return {
        author,
        nick: top.nick,
        videos: vs.length,
        plays: vs.reduce((s, v) => s + v.plays, 0),
        pctLatam: Math.round((100 * vs.filter((v) => v.is_latam).length) / vs.length),
        keywords: [...new Set(vs.map((v) => v.keyword))],
        topUrl: top.url,
        topText: top.text,
        topPlays: top.plays,
        label: majority,
      };
    })
    .sort((a, b) => b.plays - a.plays)
    .slice(0, topN);
}
