import React from 'react';
import { useNavigate } from 'react-router-dom';

const FEATURES = [
  {
    icon: '📥',
    title: 'Download Automático',
    desc: 'Cole a URL base e baixe capítulos inteiros convertidos em PDF automaticamente.',
  },
  {
    icon: '📚',
    title: 'Biblioteca Organizada',
    desc: 'Todos os seus mangás em um só lugar, com capas, contagem de capítulos e busca.',
  },
  {
    icon: '🖼',
    title: 'Capas Personalizadas',
    desc: 'Faça upload de qualquer imagem como capa diretamente pelo browser.',
  },
  {
    icon: '🗂',
    title: 'Gestão Completa',
    desc: 'Exclua capítulos ou mangás inteiros, ordene e navegue com paginação fluida.',
  },
];

/**
 * MockupCard — card decorativo no hero
 */
function MockupCard({ emoji, color }) {
  return (
    <div
      className="mockup-card"
      style={{ background: color || undefined }}
    >
      <div className="mockup-card-placeholder">{emoji}</div>
    </div>
  );
}

/**
 * LandingPage — tela inicial da aplicação
 */
function LandingPage() {
  const navigate = useNavigate();

  return (
    <div>
      {/* ── HERO ───────────────────────────────────── */}
      <section className="hero">
        <div className="hero-inner">
          {/* Conteúdo */}
          <div className="hero-content animate-in">
            <div className="hero-badge">
              📖 Organize sua coleção
            </div>

            <h1 className="hero-title">
              Sua Biblioteca de<br />
              Mangás em PDF —<br />
              <span>Baixe e Organize!</span>
            </h1>

            <p className="hero-desc">
              Faça download de capítulos direto pela URL, organize sua biblioteca
              com capas personalizadas e acesse tudo em um só lugar.
            </p>

            <div className="hero-actions">
              <button
                className="btn btn-coral"
                onClick={() => navigate('/library')}
              >
                📚 Ver Biblioteca
              </button>
              <button
                className="btn btn-outline"
                onClick={() => navigate('/download')}
              >
                ⬇ Baixar Capítulo
              </button>
            </div>
          </div>

          {/* Mockup visual */}
          <div className="hero-image animate-in" style={{ animationDelay: '0.15s' }}>
            <div className="hero-mockup">
              <div className="hero-mockup-header">
                <div className="mockup-dot mockup-dot-r" />
                <div className="mockup-dot mockup-dot-y" />
                <div className="mockup-dot mockup-dot-g" />
                <span className="mockup-title">Comic Creator — Biblioteca</span>
              </div>
              <div className="mockup-grid">
                <MockupCard emoji="🥷" color="#FFE8E5" />
                <MockupCard emoji="⚔️" color="#E8F0FF" />
                <MockupCard emoji="🌸" color="#FFF0F8" />
                <MockupCard emoji="🔥" color="#FFF3E5" />
                <MockupCard emoji="🐉" color="#E8FFE8" />
                <MockupCard emoji="💫" color="#F0E8FF" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FEATURES ───────────────────────────────── */}
      <section className="features">
        <div className="container">
          <div className="features-header">
            <span className="section-label">Funcionalidades</span>
            <h2 className="section-title">
              Tudo que você precisa para<br />
              <span>gerenciar sua coleção</span>
            </h2>
          </div>

          <div className="features-grid">
            {FEATURES.map((f, i) => (
              <div
                key={f.title}
                className="feature-card animate-in"
                style={{ animationDelay: `${i * 0.08}s` }}
              >
                <div className="feature-icon">{f.icon}</div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* CTA final */}
          <div style={{ textAlign: 'center', marginTop: '56px' }}>
            <button
              className="btn btn-coral"
              style={{ fontSize: '1rem', padding: '14px 36px' }}
              onClick={() => navigate('/download')}
            >
              Começar Agora →
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;