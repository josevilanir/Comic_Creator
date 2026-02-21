import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Pagination from './Pagination';

const ITEMS_PER_PAGE = 20;

/**
 * ChapterRow - linha de capítulo individual (componente base)
 */
function ChapterRow({ chapter, onDelete, isDeleting }) {
  return (
    <div className="chapter-row animate-in" style={{ opacity: isDeleting ? 0.5 : 1, transition: 'opacity 0.2s' }}>
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
        <a
          href={chapter.url}
          target="_blank"
          rel="noopener noreferrer"
          className="chapter-title"
        >
          {chapter.title}
        </a>
        {chapter.read && (
          <span className="chapter-read-badge">✓ Lido</span>
        )}
      </div>

      {/* Actions */}
      <div className="chapter-actions">
        <button
          className="btn btn-danger"
          onClick={() => onDelete(chapter.filename)}
          disabled={isDeleting}
          aria-label={`Deletar ${chapter.title}`}
          title="Excluir capítulo"
        >
          {isDeleting ? '⏳' : '🗑'}
        </button>
      </div>
    </div>
  );
}

/**
 * ChapterList - página de detalhes de um mangá com seus capítulos
 */
function ChapterList() {
  const { mangaName } = useParams();
  const navigate = useNavigate();
  const decodedName = decodeURIComponent(mangaName);

  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingFile, setDeletingFile] = useState(null);
  const [alert, setAlert] = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 4000);
  }

  useEffect(() => {
    fetch(`http://localhost:5000/api/library/${encodeURIComponent(decodedName)}`)
      .then(res => res.json())
      .then(data => {
        // A API retorna { manga, total, chapters: [...] }
        const lista = data.chapters ?? data.capitulos ?? [];
        setChapters(Array.isArray(lista) ? lista : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erro ao carregar capítulos:', err);
        setLoading(false);
      });
  }, [decodedName]);

  // Ordena capítulos
  const sorted = useMemo(() => {
    return [...chapters].sort((a, b) => {
      const numA = parseInt(a.title?.match(/\d+/)?.[0] || 0);
      const numB = parseInt(b.title?.match(/\d+/)?.[0] || 0);
      return sortOrder === 'asc' ? numA - numB : numB - numA;
    });
  }, [chapters, sortOrder]);

  // Paginação
  const totalPages = Math.ceil(sorted.length / ITEMS_PER_PAGE);
  const paginated = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return sorted.slice(start, start + ITEMS_PER_PAGE);
  }, [sorted, currentPage]);

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function handleDelete(filename) {
    if (!window.confirm(`Deletar o capítulo "${filename.replace('.pdf', '')}"?\n\nEsta ação não pode ser desfeita.`)) return;

    // Marca capítulo como "deletando" para feedback visual imediato
    setDeletingFile(filename);
    try {
      const res = await fetch(
        `http://localhost:5000/api/library/${encodeURIComponent(decodedName)}/${encodeURIComponent(filename)}`,
        { method: 'DELETE' }
      );
      const data = await res.json();

      if (data.success) {
        // Remove da lista local — sem precisar recarregar a página
        setChapters(prev => prev.filter(c => c.filename !== filename));
        showAlert(data.message || 'Capítulo excluído!', 'success');
      } else {
        showAlert(data.message || 'Erro ao excluir capítulo.', 'error');
      }
    } catch (err) {
      showAlert(`Erro de conexão: ${err.message}`, 'error');
    } finally {
      setDeletingFile(null);
    }
  }

  function toggleSort() {
    setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  }

  // ---- RENDER ----

  if (loading) {
    return (
      <div className="container">
        <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
          Carregando capítulos...
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Hero do mangá */}
      <div className="page-hero">
        <button className="back-btn" onClick={() => navigate('/library')}>
          ← Voltar
        </button>
        <h1 style={{ marginTop: '20px' }}>{decodedName.toUpperCase()}</h1>
        <p>{chapters.length} {chapters.length === 1 ? 'capítulo disponível' : 'capítulos disponíveis'}</p>
      </div>

      {/* Header da lista */}
      <div className="section-header">
        <h2 className="section-title">Capítulos</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {totalPages > 1 && (
            <span className="section-count">Pág. {currentPage}/{totalPages}</span>
          )}
          <button className="sort-btn" onClick={toggleSort}>
            {sortOrder === 'asc' ? '↑ Crescente' : '↓ Decrescente'}
          </button>
        </div>
      </div>

      {/* Alert de feedback */}
      {alert.message && (
        <div className={`alert alert-${alert.type}`}>
          <span>{alert.type === 'success' ? '✓' : '✕'}</span>
          {alert.message}
        </div>
      )}

      {/* Empty */}
      {chapters.length === 0 && (
        <div className="empty-state">
          <span className="empty-state-emoji">📂</span>
          <h3>Sem capítulos</h3>
          <p>Baixe capítulos de {decodedName} na aba Baixar.</p>
        </div>
      )}

      {/* Lista */}
      {paginated.map(chapter => (
        <ChapterRow
          key={chapter.filename}
          chapter={chapter}
          onDelete={handleDelete}
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
  );
}

export default ChapterList;