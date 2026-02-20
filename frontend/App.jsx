import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Library from './Library';
import ChapterList from './ChapterList';
import Downloader from './Downloader';

/**
 * Navbar - componente de navegação separado (responsabilidade única)
 */
function Navbar() {
  const location = useLocation();

  const links = [
    { to: '/', label: 'Baixar' },
    { to: '/library', label: 'Biblioteca' },
  ];

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/library" className="navbar-logo">
          Comic<span>Creator</span>
        </Link>

        <nav className="navbar-links">
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
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
 * App - componente raiz; apenas composição e roteamento
 */
function App() {
  return (
    <Router>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Downloader />} />
          <Route path="/library" element={<Library />} />
          <Route path="/manga/:mangaName" element={<ChapterList />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;