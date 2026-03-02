import React from 'react';

/**
 * LibraryToolbar — barra de busca + contador de resultados da biblioteca.
 *
 * Props:
 *  - search         {string}  valor do campo de busca
 *  - setSearch      {fn}      setter do campo de busca
 *  - filteredCount  {number}  total de mangas filtrados
 *  - currentPage    {number}
 *  - totalPages     {number}
 */
function LibraryToolbar({ search, setSearch, filteredCount, currentPage, totalPages }) {
  return (
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
          <strong>{filteredCount}</strong> {filteredCount === 1 ? 'título' : 'títulos'}
          {totalPages > 1 && ` · Página ${currentPage} de ${totalPages}`}
        </span>
      </div>
    </div>
  );
}

export default LibraryToolbar;
