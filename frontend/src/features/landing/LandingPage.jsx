import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * CircleTextBadge — cria um texto circular rodando em volta do centro
 */
function CircleTextBadge({ text, onClick }) {
  const letters = text.split('');
  return (
    <div className="bento-circle-badge">
      <div className="bento-circle-badge-text">
        {letters.map((char, i) => (
          <span key={i} style={{ transform: `rotate(${i * (360 / letters.length)}deg)` }}>
            {char}
          </span>
        ))}
      </div>
      <div className="bento-circle-badge-inner" onClick={onClick}>
        <span>Start<br/>Generate</span>
      </div>
    </div>
  );
}

/**
 * LandingPage — Bento Box Style
 */
function LandingPage() {
  const navigate = useNavigate();

  return (
    <div>
      {/* ── BENTO HERO ───────────────────────────────────── */}
      <section className="bento-hero">
        
        {/* HUGE HEADLINE */}
        <h1 className="bento-hero-header">
          MANGA LIBRARY &<br />
          DOWNLOADING
        </h1>

        <div className="bento-hero-grid relative">
          
          {/* Main big image card (bottom-left area equivalent) */}
          <div className="bento-layout-card bento-hero-main-card">
            {/* We don't have anime images, so we'll use a nice placeholder gradient or real manga imagery if any. Using a vibrant gradient/cover for now */}
            <div className="w-full h-full bg-gradient-to-tr from-orange-200 to-rose-200 flex items-center justify-center relative overflow-hidden">
               {/* Decorative floating bits inside */}
               <div className="absolute top-10 left-10 w-20 h-20 bg-white/30 rounded-full blur-xl"></div>
               <span className="text-4xl">📚</span>
            </div>
            
            {/* Floating Action Sticker */}
            <div 
              className="bento-action-sticker"
              onClick={() => navigate('/download')}
            >
              <span className="bento-action-sticker-icon">🎲</span>
              <span>Create<br/>Library</span>
            </div>
          </div>

          {/* Right side area container */}
          <div className="flex flex-col gap-6 relative">
            
            {/* Right vertical image card */}
            <div className="bento-layout-card bento-hero-side-card ml-auto w-[65%] sm:w-[50%]">
              <div className="w-full h-full bg-gradient-to-b from-indigo-100 to-purple-200 flex items-center justify-center">
                 <span className="text-4xl">✨</span>
              </div>
              <div className="bento-strip-y">
                <span>★</span>
                <span>★</span>
                <span className="mt-auto">↑</span>
              </div>
            </div>

            {/* Smartphone App Promo Card */}
            <div className="bento-promo-card">
              <div className="bento-promo-header">
                <span>Desktop App</span>
                <span className="flex gap-1">
                  <span className="w-2 h-2 bg-black rounded-full"></span>
                  <span className="w-2 h-2 bg-black rounded-full"></span>
                  <span className="w-2 h-2 bg-black rounded-full"></span>
                </span>
              </div>
              <p className="bento-promo-desc">
                The desktop application for Comic Creator, where you can download and read all your favorite mangas directly.
              </p>
              <div className="bento-promo-footer">
                <div className="bento-store-icons">
                  <span className="text-xl leading-none">🖥️</span>
                  <span className="text-xl leading-none">▶</span>
                </div>
                <button 
                  className="bento-download-btn"
                  onClick={() => navigate('/library')}
                >
                  Enter Library
                  <span className="bento-download-btn-icon">↓</span>
                </button>
              </div>
            </div>
          </div>
          
          {/* Center Badge positioned absolutely in the grid */}
          <CircleTextBadge 
            text="★ OFFICIAL RELEASE ★ COMIC CREATOR V1.0 ★ "
            onClick={() => navigate('/download')}
          />

        </div>
      </section>

    </div>
  );
}

export default LandingPage;