import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLibrary } from '../../hooks/useLibrary';
import MangaCard from '../../components/shared/MangaCard';
import SkeletonCard from '../../components/shared/SkeletonCard';
import EmptyState from '../../components/shared/EmptyState';
import Pagination from '../../components/shared/Pagination';
import Alert from '../../components/ui/Alert';
import LibraryToolbar from '../../components/library/LibraryToolbar';

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
      <div className="bento-page-header">
        <div className="bento-page-header-inner">
          <h1>Minha <span>Biblioteca</span></h1>
          <p>Gerencie sua coleção de mangás — clique para ver capítulos.</p>
        </div>
      </div>

      <div className="bento-layout-card bg-white p-6 sm:p-8 flex flex-col gap-6 relative">
        {/* Alerta global */}
        <div className="absolute top-4 right-4 z-50">
          <Alert message={alert.message} type={alert.type} />
        </div>

        <LibraryToolbar
          search={search}
          setSearch={setSearch}
          filteredCount={filtered.length}
          currentPage={currentPage}
          totalPages={totalPages}
        />

        {/* Empty state */}
        {filtered.length === 0 && <EmptyState search={search} />}

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
