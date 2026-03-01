import React, { useState } from 'react';
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
 * Navbar — mobile-first com Tailwind. Hamburger em mobile, links em desktop.
 */
function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  function isActive(to) {
    if (to === '/') return pathname === '/';
    return pathname.startsWith(to);
  }

  function linkClass(to) {
    return isActive(to)
      ? 'font-bold text-[var(--coral)]'
      : 'text-gray-500 hover:text-gray-900';
  }

  const navLinks = NAV_LINKS.filter(l => l.to !== '/');

  return (
    <header className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur border-b border-gray-100 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between gap-4">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0 no-underline">
          <span className="w-8 h-8 bg-[var(--coral)] rounded-lg flex items-center justify-center text-sm shadow-sm">📖</span>
          <span className="font-bold text-gray-900 text-sm hidden sm:block">Comic Creator</span>
        </Link>

        {/* Links — desktop */}
        <nav className="hidden md:flex items-center gap-1 flex-1">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-4 py-2 rounded-full text-sm font-bold transition-all no-underline ${linkClass(link.to)}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* User + Sair — desktop */}
        {user && (
          <div className="hidden md:flex items-center gap-3">
            <span className="text-sm text-gray-500 truncate max-w-[120px]">👋 {user.username}</span>
            <button onClick={logout} className="btn btn-sm btn-outline">Sair</button>
          </div>
        )}

        {/* Hamburger — mobile */}
        <button
          className="md:hidden p-3 w-11 h-11 flex items-center justify-center text-gray-700 text-xl leading-none"
          onClick={() => setMenuOpen(o => !o)}
          aria-label="Menu"
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Dropdown mobile */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-4 py-3 flex flex-col gap-3">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-sm font-bold py-3 no-underline ${linkClass(link.to)}`}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          {user && (
            <>
              <span className="text-sm text-gray-400">👋 {user.username}</span>
              <button
                onClick={() => { logout(); setMenuOpen(false); }}
                className="btn btn-sm btn-outline w-full justify-center"
              >
                Sair
              </button>
            </>
          )}
        </div>
      )}
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
