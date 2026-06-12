import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import meta from "@/public/data/meta.json";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

const pctSignal = Math.round((100 * (meta.label_dist?.manosfera_sincera ?? 0)) / meta.total_videos);
const description = `${meta.total_videos} videos de TikTok (${meta.period.start} → ${meta.period.end}). Solo el ${pctSignal}% de lo que matchea keywords es manosfera real. Piloto de escucha digital Estudio Plural × Camino.`;

export const metadata: Metadata = {
  metadataBase: new URL("https://lin-manosfera.vercel.app"),
  title: "LIN · Radiografía de la manosfera hispana",
  description,
  openGraph: {
    title: "Radiografía de la manosfera hispana",
    description,
    url: "/",
    siteName: "LIN · Estudio Plural × Camino",
    locale: "es",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Radiografía de la manosfera hispana",
    description,
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <body className="min-h-screen bg-[#09090b] text-zinc-100">{children}</body>
    </html>
  );
}
