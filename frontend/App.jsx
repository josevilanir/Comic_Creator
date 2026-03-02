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
 * Navbar — Floating pill layout (Bento Box style)
 */
function BentoNavbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  function isActive(to) {
    if (to === '/') return pathname === '/';
    return pathname.startsWith(to);
  }

  function linkClass(to) {
    return isActive(to) ? 'bento-nav-link active' : 'bento-nav-link';
  }

  const navLinks = NAV_LINKS;

  return (
    <>
      <div className="bento-header-wrapper">
        {/* Logo Left */}
        <Link to="/" className="navbar-logo no-underline">
          <span className="navbar-logo-text" style={{ fontSize: '1.4rem' }}>comic creator</span>
          <span className="navbar-logo-icon">❤</span>
        </Link>
        
        {/* Actions Right */}
        <div className="flex items-center gap-3">
          {user ? (
            <button onClick={logout} className="btn bg-white text-black hover:bg-gray-100 rounded-full px-6 shadow-sm border border-gray-200">
              Sair
            </button>
          ) : (
             <Link to="/login" className="btn bg-white text-black hover:bg-gray-100 rounded-full px-6 shadow-sm border border-gray-200">
              Join Us
            </Link>
          )}
        </div>
      </div>

      {/* Floating Center Pill - Hidden on very small screens, shown as hamburger menu */}
      <nav className="hidden md:flex bento-nav-pill">
        {navLinks.map(link => (
          <Link
            key={link.to}
            to={link.to}
            className={linkClass(link.to)}
          >
            {link.label}
          </Link>
        ))}
        {user && (
           <span className="text-gray-400 text-xs ml-4">👋 {user.username}</span>
        )}
      </nav>
      
      {/* Mobile nav logic (simplified for brevity, can still use old hamburger logic if needed) */}
      <div className="md:hidden absolute top-4 left-1/2 -translate-x-1/2 z-[100]">
         <button
          className="bg-black text-white px-4 py-2 rounded-full text-sm font-bold"
          onClick={() => setMenuOpen(o => !o)}
        >
           Menu {menuOpen ? '✕' : '☰'}
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden absolute top-16 left-1/2 -translate-x-1/2 bg-black text-white rounded-xl p-4 flex flex-col gap-3 z-[100] shadow-xl border border-gray-800 w-48 text-center">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-sm font-bold py-2 no-underline ${isActive(link.to) ? 'text-white' : 'text-gray-400'}`}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </>
  );
}

/**
 * AppContent — separado para poder usar useLocation dentro do Router
 */
function AppContent() {
  const { pathname } = useLocation();
  const isReader = pathname.includes('/ler/');
  const isAuthPage = pathname === '/login';

  if (isReader || isAuthPage) {
    return (
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route path="/manga/:mangaName/ler/:filename" element={<PrivateRoute><MangaReader /></PrivateRoute>} />
      </Routes>
    );
  }

  return (
    <div className="bento-app-container">
      <div className="bento-board shadow-2xl">
        <BentoNavbar />
        <main className="bento-inner">
          <Routes>
            <Route path="/" element={<PrivateRoute><LandingPage /></PrivateRoute>} />
            <Route path="/library" element={<PrivateRoute><Library /></PrivateRoute>} />
            <Route path="/manga/:mangaName" element={<PrivateRoute><ChapterList /></PrivateRoute>} />
            <Route path="/download" element={<PrivateRoute><Downloader /></PrivateRoute>} />
          </Routes>
        </main>
      </div>
    </div>
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
