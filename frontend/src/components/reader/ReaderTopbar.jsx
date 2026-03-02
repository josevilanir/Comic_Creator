import React from 'react';

/**
 * ReaderTopbar — barra superior do leitor de capítulos.
 *
 * Props:
 *  - decodedManga   {string}   nome do mangá
 *  - chapterTitle   {string}   título do capítulo (sem extensão)
 *  - zoom           {number}   escala atual (ex: 1.4)
 *  - onZoomIn       {fn}
 *  - onZoomOut      {fn}
 *  - onZoomReset    {fn}
 *  - page           {number}   página atual
 *  - total          {number}   total de páginas
 *  - onPrevPage     {fn}
 *  - onNextPage     {fn}
 *  - allChapters    {Array}    lista de capítulos do mangá
 *  - currentIdx     {number}   índice do capítulo atual
 *  - prevChapter    {object|null}
 *  - nextChapter    {object|null}
 *  - onPrevChapter  {fn}
 *  - onNextChapter  {fn}
 *  - onBack         {fn}       volta para a página do mangá
 */
function ReaderTopbar({
  decodedManga,
  chapterTitle,
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomReset,
  page,
  total,
  onPrevPage,
  onNextPage,
  allChapters,
  currentIdx,
  prevChapter,
  nextChapter,
  onPrevChapter,
  onNextChapter,
  onBack,
}) {
  return (
    <div className="reader-topbar">
      {/* Esquerda: voltar + título */}
      <div className="reader-topbar-left">
        <button className="reader-btn" onClick={onBack}>
          ← Voltar à Biblioteca
        </button>
        <div className="reader-title-wrap">
          <span className="reader-manga-name">{decodedManga}</span>
          <span className="reader-chapter-name">{chapterTitle}</span>
        </div>
      </div>

      {/* Centro: zoom */}
      <div className="reader-controls-center">
        <button
          className="reader-ctrl-btn"
          onClick={onZoomOut}
          title="Diminuir zoom (−)"
        >
          −
        </button>
        <button
          className="reader-zoom-display"
          onClick={onZoomReset}
          title="Resetar zoom (0)"
        >
          {Math.round(zoom * 100)}%
        </button>
        <button
          className="reader-ctrl-btn"
          onClick={onZoomIn}
          title="Aumentar zoom (+)"
        >
          +
        </button>
      </div>

      {/* Direita: nav capítulos + contador de páginas */}
      <div className="reader-topbar-right">
        {allChapters.length > 1 && (
          <div className="reader-chapter-nav">
            <button
              className="reader-nav-btn"
              onClick={onPrevChapter}
              disabled={!prevChapter}
              title="Capítulo anterior"
            >
              ‹
            </button>
            <span className="reader-chapter-pos">
              Cap. {currentIdx + 1}/{allChapters.length}
            </span>
            <button
              className="reader-nav-btn"
              onClick={onNextChapter}
              disabled={!nextChapter}
              title="Próximo capítulo"
            >
              ›
            </button>
          </div>
        )}

        {total > 0 && (
          <div className="reader-page-counter">
            <button
              className="reader-nav-btn"
              onClick={onPrevPage}
              disabled={page === 1 && !prevChapter}
              title="Página anterior (←)"
            >
              ‹
            </button>
            <span className="reader-chapter-pos">
              {page} / {total}
            </span>
            <button
              className="reader-nav-btn"
              onClick={onNextPage}
              disabled={page === total && !nextChapter}
              title="Próxima página (→)"
            >
              ›
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReaderTopbar;
