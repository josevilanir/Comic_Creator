import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLibrary } from '../../hooks/useLibrary';
import MangaCard from '../../components/shared/MangaCard';
import Pagination from '../../components/shared/Pagination';
import Alert from '../../components/ui/Alert';

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-thumb" />
      <div className="skeleton-body">
        <div className="skeleton-line" />
        <div className="skeleton-line short" />
      </div>
    </div>
  );
}

// ─── Library ──────────────────────────────────────────────────────────────────
function Library() {
  const navigate = useNavigate();
  const {
    alert,
    loading,
    search,
    setSearch,
    filtered,
    paginated,
    currentPage,
    totalPages,
    handlePageChange,
    handleDelete,
    handleUploadCapa,
  } = useLibrary();

  // ── Loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <>
        <div className="page-header">
          <div className="page-header-inner">
            <h1>Minha <span>Biblioteca</span></h1>
            <p>Carregando sua coleção...</p>
          </div>
        </div>
        <div className="container">
          <div className="loading-grid">
            {Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        </div>
      </>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Header da página */}
      <div className="page-header">
        <div className="page-header-inner">
          <h1>Minha <span>Biblioteca</span></h1>
          <p>Gerencie sua coleção de mangás — clique para ver capítulos.</p>
        </div>
      </div>

      <div className="container">
        {/* Alerta global (useAlert) */}
        <Alert
          message={alert.message}
          type={alert.type}
        />

        {/* Busca */}
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Buscar mangá..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* Stats */}
        <div className="stats-bar">
          <span className="stats-count">
            <strong>{filtered.length}</strong> {filtered.length === 1 ? 'título' : 'títulos'}
            {totalPages > 1 && ` · Página ${currentPage} de ${totalPages}`}
          </span>
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div className="empty-state">
            <span className="empty-state-emoji">📭</span>
            {search ? (
              <>
                <h3>Nada encontrado</h3>
                <p>Nenhum mangá corresponde a "{search}".</p>
              </>
            ) : (
              <>
                <h3>Biblioteca vazia</h3>
                <p>Vá em <strong>Downloads</strong> para baixar seus primeiros mangás.</p>
              </>
            )}
          </div>
        )}

        {/* Grid */}
        {paginated.length > 0 && (
          <div className="manga-grid">
            {paginated.map(manga => (
              <MangaCard
                key={manga.nome}
                manga={manga}
                onClick={() => navigate(`/manga/${encodeURIComponent(manga.nome)}`)}
                onDelete={handleDelete}
                onUploadCapa={handleUploadCapa}
              />
            ))}
          </div>
        )}

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

export default Library;
