import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import LandingPage from './src/features/landing/LandingPage';
import Library from './src/features/library/Library';
import ChapterList from './src/features/library/ChapterList';
import MangaReader from './src/features/reader/MangaReader';
import Downloader from './src/features/downloader/Downloader';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { PrivateRoute } from './src/components/PrivateRoute';
import { AuthPage } from './src/pages/AuthPage';

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
  const { user, logout } = useAuth();

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
          
          {user && (
              <div style={{ display: 'flex', alignItems: 'center', marginLeft: '16px', gap: '12px' }}>
                  <span style={{
                color: 'var(--text-light)',
                fontSize: '0.85rem',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '80px',
              }}>👋 {user.username}</span>
                  <button onClick={logout} className="btn btn-sm btn-outline">Sair</button>
              </div>
          )}
        </nav>
      </div>
    </header>
  );
}

/**
 * AppContent — separado para poder usar useLocation dentro do Router
 * e ocultar a navbar na página de leitura (reader ocupa tela toda)
 */
function AppContent() {
  const { pathname } = useLocation();
  const isReader = pathname.includes('/ler/');
  const isAuthPage = pathname === '/login';

  return (
    <>
      {!isReader && !isAuthPage && <Navbar />}
      <main>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          
          <Route path="/" element={<PrivateRoute><LandingPage /></PrivateRoute>} />
          <Route path="/library" element={<PrivateRoute><Library /></PrivateRoute>} />
          <Route path="/manga/:mangaName" element={<PrivateRoute><ChapterList /></PrivateRoute>} />
          <Route path="/manga/:mangaName/ler/:filename" element={<PrivateRoute><MangaReader /></PrivateRoute>} />
          <Route path="/download" element={<PrivateRoute><Downloader /></PrivateRoute>} />
        </Routes>
      </main>
    </>
  );
}

/**
 * App — composição de rotas e layout global
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
