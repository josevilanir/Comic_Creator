import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Pagination from './Pagination';

const ITEMS_PER_PAGE = 20;
const API = 'http://localhost:5000';

// ─── ChapterRow ───────────────────────────────────────────────────────────────
/**
 * ChapterRow — linha individual de capítulo.
 * UI pura, recebe dados e callbacks via props.
 */
function ChapterRow({ chapter, onDelete, onRead, isDeleting }) {
  return (
    <div
      className="chapter-row animate-in"
      style={{ opacity: isDeleting ? 0.45 : 1, transition: 'opacity 0.2s' }}
    >
      {/* Thumbnail */}
      {chapter.thumbnail ? (
        <img
          className="chapter-thumb"
          src={chapter.thumbnail}
          alt={chapter.title}
          loading="lazy"
        />
      ) : (
        <div className="chapter-thumb-placeholder">📄</div>
      )}

      {/* Info */}
      <div className="chapter-info">
        <span className="chapter-title">{chapter.title}</span>
        {chapter.read && (
          <span className="chapter-read-badge">✓ Lido</span>
        )}
      </div>

      {/* Ações */}
      <div className="chapter-actions" style={{ display: 'flex', gap: '8px' }}>
        <button
          className="btn btn-sm btn-coral"
          onClick={() => onRead(chapter)}
          title="Ler capítulo"
        >
          📖 Ler
        </button>
        <button
          className="btn btn-sm btn-danger"
          onClick={() => onDelete(chapter.filename)}
          disabled={isDeleting}
          title="Excluir capítulo"
          aria-label={`Excluir ${chapter.title}`}
        >
          {isDeleting ? '⏳' : '🗑'}
        </button>
      </div>
    </div>
  );
}

// ─── ChapterList ──────────────────────────────────────────────────────────────
/**
 * ChapterList — página de detalhes de um mangá com lista de capítulos.
 */
function ChapterList() {
  const { mangaName } = useParams();
  const navigate      = useNavigate();
  const decodedName   = decodeURIComponent(mangaName);

  const [chapters,     setChapters]     = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [sortOrder,    setSortOrder]    = useState('asc');
  const [currentPage,  setCurrentPage]  = useState(1);
  const [deletingFile, setDeletingFile] = useState(null);
  const [alert,        setAlert]        = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 4000);
  }

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/library/${encodeURIComponent(decodedName)}?ordem=${sortOrder}`)
      .then(res => res.json())
      .then(data => {
        const lista = data.chapters ?? data.capitulos ?? [];
        setChapters(Array.isArray(lista) ? lista : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erro ao carregar capítulos:', err);
        setLoading(false);
      });
  }, [decodedName, sortOrder]);

  // Ordena localmente (já vem ordenado da API, mas mantemos para toggle instantâneo)
  const sorted = useMemo(() => {
    return [...chapters].sort((a, b) => {
      const numA = parseInt(a.title?.match(/\d+/)?.[0] ?? 0);
      const numB = parseInt(b.title?.match(/\d+/)?.[0] ?? 0);
      return sortOrder === 'asc' ? numA - numB : numB - numA;
    });
  }, [chapters, sortOrder]);

  const totalPages = Math.ceil(sorted.length / ITEMS_PER_PAGE);

  const paginated = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return sorted.slice(start, start + ITEMS_PER_PAGE);
  }, [sorted, currentPage]);

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function toggleSort() {
    setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  }

  function handleRead(chapter) {
    // Passa a lista COMPLETA de capítulos ordenados para o reader
    // permitir navegação prev/next entre capítulos sem voltar para esta tela
    navigate(
      `/manga/${encodeURIComponent(decodedName)}/ler/${encodeURIComponent(chapter.filename)}`,
      { state: { chapters: sorted } }
    );
  }

  async function handleDelete(filename) {
    if (!window.confirm(`Excluir o capítulo "${filename.replace('.pdf', '')}"?\n\nEsta ação não pode ser desfeita.`)) return;

    setDeletingFile(filename);
    try {
      const res  = await fetch(
        `${API}/api/library/${encodeURIComponent(decodedName)}/${encodeURIComponent(filename)}`,
        { method: 'DELETE' }
      );
      const data = await res.json();

      if (data.success) {
        setChapters(prev => prev.filter(c => c.filename !== filename));
        showAlert(data.message || 'Capítulo excluído!');
      } else {
        showAlert(data.message || 'Erro ao excluir capítulo.', 'error');
      }
    } catch (err) {
      showAlert(`Erro de conexão: ${err.message}`, 'error');
    } finally {
      setDeletingFile(null);
    }
  }

  // ── Loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <>
        <div className="page-header">
          <div className="page-header-inner">
            <button className="back-btn" onClick={() => navigate('/library')}>
              ← Voltar
            </button>
            <h1 style={{ marginTop: '16px' }}>{decodedName}</h1>
            <p>Carregando capítulos...</p>
          </div>
        </div>
        <div className="container">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton-card" style={{ height: '80px', marginBottom: '10px', aspectRatio: 'unset' }}>
              <div className="skeleton-line" style={{ height: '100%', margin: 0 }} />
            </div>
          ))}
        </div>
      </>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Header */}
      <div className="page-header">
        <div className="page-header-inner">
          <button className="back-btn" onClick={() => navigate('/library')}>
            ← Voltar para Biblioteca
          </button>
          <h1 style={{ marginTop: '16px' }}>
            <span>{decodedName}</span>
          </h1>
          <p>
            {chapters.length === 0
              ? 'Nenhum capítulo baixado ainda.'
              : `${chapters.length} ${chapters.length === 1 ? 'capítulo disponível' : 'capítulos disponíveis'}`}
          </p>
        </div>
      </div>

      <div className="container">
        {/* Alert */}
        {alert.message && (
          <div className={`alert alert-${alert.type}`}>
            <span>{alert.type === 'success' ? '✓' : '✕'}</span>
            {alert.message}
          </div>
        )}

        {/* Controls */}
        {chapters.length > 0 && (
          <div className="section-header">
            <span className="section-header-title">Capítulos</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {totalPages > 1 && (
                <span className="section-header-count">
                  Pág. {currentPage}/{totalPages}
                </span>
              )}
              <button className="sort-btn" onClick={toggleSort}>
                {sortOrder === 'asc' ? '↑ Crescente' : '↓ Decrescente'}
              </button>
            </div>
          </div>
        )}

        {/* Empty state */}
        {chapters.length === 0 && (
          <div className="empty-state">
            <span className="empty-state-emoji">📂</span>
            <h3>Sem capítulos</h3>
            <p>
              Nenhum capítulo de <strong>{decodedName}</strong> foi baixado ainda.{' '}
              <span
                style={{ color: 'var(--coral)', cursor: 'pointer', fontWeight: 700 }}
                onClick={() => navigate('/download')}
              >
                Baixar agora →
              </span>
            </p>
          </div>
        )}

        {/* Lista */}
        {paginated.map(chapter => (
          <ChapterRow
            key={chapter.filename}
            chapter={chapter}
            onDelete={handleDelete}
            onRead={handleRead}
            isDeleting={deletingFile === chapter.filename}
          />
        ))}

        {/* Paginação */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </div>
    </>
  );
}

export default ChapterList;