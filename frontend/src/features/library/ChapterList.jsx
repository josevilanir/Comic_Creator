import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Pagination from '../../components/shared/Pagination';
import Alert from '../../components/ui/Alert';
import { useChapters } from '../../hooks/useChapters';

/**
 * Página de listagem de capítulos de um mangá.
 * Usa o hook useChapters para encapsular toda a lógica de dados.
 */
function ChapterList() {
  const { mangaName } = useParams();
  const navigate = useNavigate();
  const decodedName = decodeURIComponent(mangaName);

  const {
    loading,
    alert,
    sorted,
    paginated,
    sortOrder,
    currentPage,
    totalPages,
    deletingFile,
    toggleSort,
    handlePageChange,
    handleDelete,
    handleToggleLido,
  } = useChapters(decodedName);

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
            <div
              key={i}
              className="skeleton-card"
              style={{ height: '80px', marginBottom: '10px', aspectRatio: 'unset' }}
            >
              <div className="skeleton-line" style={{ height: '100%', margin: 0 }} />
            </div>
          ))}
        </div>
      </>
    );
  }

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
            {sorted.length === 0
              ? 'Nenhum capítulo baixado ainda.'
              : `${sorted.length} ${sorted.length === 1 ? 'capítulo disponível' : 'capítulos disponíveis'}`}
          </p>
        </div>
      </div>

      <div className="container">
        <Alert message={alert.message} type={alert.type} />

        {sorted.length > 0 && (
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

        {sorted.length === 0 && (
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

        {paginated.map(chapter => (
          <div
            key={chapter.filename}
            className="chapter-row animate-in"
            style={{ opacity: deletingFile === chapter.filename ? 0.45 : 1, transition: 'opacity 0.2s' }}
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

            <div className="chapter-info">
              <span className="chapter-title">{chapter.title}</span>
              {chapter.read && <span className="chapter-read-badge">✓ Lido</span>}
            </div>

            <div className="chapter-actions" style={{ display: 'flex', gap: '8px' }}>
              <button
                className="btn btn-sm btn-coral"
                onClick={() => {
                  navigate(
                    `/manga/${encodeURIComponent(decodedName)}/ler/${encodeURIComponent(chapter.filename)}`,
                    { state: { chapters: sorted } }
                  );
                }}
                title="Ler capítulo"
              >
                📖 Ler
              </button>
              <button
                className={`btn btn-sm ${chapter.read ? 'btn-outline' : 'btn-success'}`}
                onClick={() => handleToggleLido(chapter.filename)}
                title={chapter.read ? 'Marcar como não lido' : 'Marcar como lido'}
              >
                {chapter.read ? '↩ Não lido' : '✓ Lido'}
              </button>
              <button
                className="btn btn-sm btn-danger"
                onClick={() => handleDelete(chapter.filename)}
                disabled={deletingFile === chapter.filename}
                title="Excluir capítulo"
                aria-label={`Excluir ${chapter.title}`}
              >
                {deletingFile === chapter.filename ? '⏳' : '🗑'}
              </button>
            </div>
          </div>
        ))}

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
