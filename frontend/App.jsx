import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import LandingPage from './src/features/landing/LandingPage';
import Library from './src/features/library/Library';
import ChapterList from './src/features/library/ChapterList';
import MangaReader from './src/features/reader/MangaReader';
import Downloader from './src/features/downloader/Downloader';

const NAV_LINKS = [
  { to: '/',         label: 'Home' },
  { to: '/library',  label: 'Biblioteca' },
  { to: '/download', label: 'Downloads' },
];

/**
 * Navbar — componente separado com responsabilidade única de navegação
 */
function Navbar() {
  const { pathname } = useLocation();

  // Verifica se o link está ativo (exact para '/', prefix para o resto)
  function isActive(to) {
    if (to === '/') return pathname === '/';
    return pathname.startsWith(to);
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Logo */}
        <Link to="/" className="navbar-logo" style={{ textDecoration: 'none' }}>
          <div className="navbar-logo-icon">📖</div>
          <div className="navbar-logo-text">
            <span className="navbar-logo-title">Comic Creator</span>
            <span className="navbar-logo-sub">Manga Library</span>
          </div>
        </Link>

        {/* Links */}
        <nav className="navbar-links">
          {NAV_LINKS.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${isActive(link.to) ? 'active' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

/**
 * App — composição de rotas e layout global
 */
function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

/**
 * AppContent — separado para poder usar useLocation dentro do Router
 * e ocultar a navbar na página de leitura (reader ocupa tela toda)
 */
function AppContent() {
  const { pathname } = useLocation();
  const isReader = pathname.includes('/ler/');

  return (
    <>
      {!isReader && <Navbar />}
      <main>
        <Routes>
          <Route path="/"                                    element={<LandingPage />} />
          <Route path="/library"                            element={<Library />} />
          <Route path="/manga/:mangaName"                   element={<ChapterList />} />
          <Route path="/manga/:mangaName/ler/:filename"     element={<MangaReader />} />
          <Route path="/download"                           element={<Downloader />} />
        </Routes>
      </main>
    </>
  );
}

export default App;