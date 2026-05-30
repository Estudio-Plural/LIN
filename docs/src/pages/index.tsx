import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Ver Análisis →
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <div className="col col--4">
            <div className="text--center padding-horiz--md">
              <Heading as="h3">📊 1,947 Items</Heading>
              <p>
                Capturados en 11 días a través de TikTok (920), Reddit (977) y YouTube (50).
                Volumen robusto para análisis estadístico.
              </p>
            </div>
          </div>
          <div className="col col--4">
            <div className="text--center padding-horiz--md">
              <Heading as="h3">🌎 75-86% LATAM</Heading>
              <p>
                Keywords hispanas (<em>hombre alfa</em>, <em>pildora roja</em>) muestran penetración
                LATAM cuantificable vs anglosajonas.
              </p>
            </div>
          </div>
          <div className="col col--4">
            <div className="text--center padding-horiz--md">
              <Heading as="h3">🎯 Multi-Plataforma</Heading>
              <p>
                TikTok (viral), Reddit (conversacional) y YouTube (analítico) capturan aspectos complementarios.
              </p>
            </div>
          </div>
        </div>
        <div className="row margin-top--lg">
          <div className="col col--12 text--center">
            <Heading as="h3">Casos Narrables Identificados</Heading>
            <ul className="text--left" style={{maxWidth: '600px', margin: '0 auto'}}>
              <li><strong>@growingmind.arg</strong> (Argentina): 2.85M plays en "hipergamia"</li>
              <li><strong>Controversia James Bond 2026</strong> (r/KotakuInAction): 369 upvotes, ángulo gamer</li>
              <li><strong>BBC documentales</strong>: "mesías de la machosfera" (80K views en español)</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Análisis de social listening sobre la manosfera en Colombia">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
