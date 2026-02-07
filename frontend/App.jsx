import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Library from './Library';
import ChapterList from './ChapterList';
import Downloader from './Downloader';

function App() {
  return (
    <Router>
      <div className="container">
        <header>
          <h1 style={{ marginRight: 'auto' }}>Comic Creator</h1>
          <nav style={{ display: 'flex', gap: '20px' }}>
            <Link to="/" style={{ fontWeight: 'bold' }}>Início (Baixar)</Link>
            <Link to="/library" style={{ fontWeight: 'bold' }}>Biblioteca</Link>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<Downloader />} />
          <Route path="/library" element={<Library />} />
          <Route path="/manga/:mangaName" element={<ChapterList />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
