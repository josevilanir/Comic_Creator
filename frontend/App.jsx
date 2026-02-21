import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import LandingPage from './LandingPage';
import Library from './Library';
import ChapterList from './ChapterList';
import Downloader from './Downloader';

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
      <Navbar />
      <main>
        <Routes>
          <Route path="/"                       element={<LandingPage />} />
          <Route path="/library"                element={<Library />} />
          <Route path="/manga/:mangaName"       element={<ChapterList />} />
          <Route path="/download"               element={<Downloader />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;