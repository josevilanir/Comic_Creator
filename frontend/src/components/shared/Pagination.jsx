import React from 'react';

/**
 * Pagination - Componente de paginação reutilizável
 * 
 * Props:
 *   currentPage: número da página atual (1-indexed)
 *   totalPages: total de páginas
 *   onPageChange: callback (page: number) => void
 */
function Pagination({ currentPage, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  // Gera os números de página a exibir com elipses
  function getPageNumbers() {
    const delta = 1;
    const pages = [];
    const left = Math.max(2, currentPage - delta);
    const right = Math.min(totalPages - 1, currentPage + delta);

    pages.push(1);

    if (left > 2) pages.push('...');

    for (let i = left; i <= right; i++) {
      pages.push(i);
    }

    if (right < totalPages - 1) pages.push('...');

    if (totalPages > 1) pages.push(totalPages);

    return pages;
  }

  const pages = getPageNumbers();

  return (
    <nav className="pagination" aria-label="Paginação">
      {/* Botão anterior */}
      <button
        className="page-btn-arrow"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Página anterior"
      >
        ←
      </button>

      {/* Páginas */}
      {pages.map((page, idx) =>
        page === '...' ? (
          <span key={`ellipsis-${idx}`} className="page-ellipsis">…</span>
        ) : (
          <button
            key={page}
            className={`page-btn ${page === currentPage ? 'active' : ''}`}
            onClick={() => onPageChange(page)}
            aria-label={`Página ${page}`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        )
      )}

      {/* Botão próximo */}
      <button
        className="page-btn-arrow"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Próxima página"
      >
        →
      </button>
    </nav>
  );
}

export default Pagination;