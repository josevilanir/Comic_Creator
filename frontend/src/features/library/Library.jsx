import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLibrary } from '../../hooks/useLibrary';
import MangaCard from '../../components/shared/MangaCard';
import Pagination from '../../components/shared/Pagination';
import Alert from '../../components/ui/Alert';

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="skeleton-card bento-layout-card">
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
      <div className="bento-page-container">
        <div className="bento-page-header">
          <div className="bento-page-header-inner">
            <h1>Minha <span>Biblioteca</span></h1>
            <p>Carregando sua coleção...</p>
          </div>
        </div>
        <div className="bento-layout-card bg-white p-6 sm:p-8">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        </div>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="bento-page-container">
      {/* Header da página */}
      <div className="bento-page-header">
        <div className="bento-page-header-inner">
          <h1>Minha <span>Biblioteca</span></h1>
          <p>Gerencie sua coleção de mangás — clique para ver capítulos.</p>
        </div>
      </div>

      <div className="bento-layout-card bg-white p-6 sm:p-8 flex flex-col gap-6 relative">
        {/* Alerta global (useAlert) */}
        <div className="absolute top-4 right-4 z-50">
           <Alert message={alert.message} type={alert.type} />
        </div>

        <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
          {/* Busca */}
          <div className="search-wrap w-full md:w-auto m-0 flex-1">
            <span className="search-icon text-black font-bold">🔍</span>
            <input
              type="text"
              className="search-input border-2 border-black rounded-full w-full max-w-lg bg-[var(--cream-dark)] text-black focus:bg-white"
              placeholder="Buscar mangá..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          {/* Stats */}
          <div className="stats-bar m-0">
            <span className="stats-count bg-[var(--coral-light)] text-[var(--coral)] border border-black rounded-full px-4 py-2 font-black uppercase text-xs">
              <strong>{filtered.length}</strong> {filtered.length === 1 ? 'título' : 'títulos'}
              {totalPages > 1 && ` · Página ${currentPage} de ${totalPages}`}
            </span>
          </div>
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div className="empty-state border-2 border-dashed border-black rounded-xl p-12 text-center my-8">
            <span className="empty-state-emoji text-6xl">📭</span>
            {search ? (
              <>
                <h3 className="font-black text-2xl uppercase mt-4">Nada encontrado</h3>
                <p className="text-gray-600">Nenhum mangá corresponde a "{search}".</p>
              </>
            ) : (
              <>
                <h3 className="font-black text-2xl uppercase mt-4">Biblioteca vazia</h3>
                <p className="text-gray-600">Vá em <strong>Downloads</strong> para baixar seus primeiros mangás.</p>
              </>
            )}
          </div>
        )}

        {/* Grid */}
        {paginated.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 mt-4">
            {paginated.map(manga => (
              <div key={manga.nome} className="bento-layout-card">
                 <MangaCard
                   key={manga.nome}
                   manga={manga}
                   onClick={() => navigate(`/manga/${encodeURIComponent(manga.nome)}`)}
                   onDelete={handleDelete}
                   onUploadCapa={handleUploadCapa}
                 />
              </div>
            ))}
          </div>
        )}

        {/* Paginação */}
        <div className="mt-8 border-t-2 border-dashed border-gray-200 pt-8">
           <Pagination
             currentPage={currentPage}
             totalPages={totalPages}
             onPageChange={handlePageChange}
           />
        </div>
      </div>
    </div>
  );
}

export default Library;
