import React from 'react';

/**
 * ReaderViewport — área principal de leitura do capítulo.
 *
 * Props:
 *  - status     {'loading'|'ready'|'error'}  estado de carregamento do PDF
 *  - rendering  {boolean}                    true enquanto renderiza página
 *  - canvasRef  {React.Ref}                  ref do <canvas> controlado pelo pai
 *  - onPrev     {fn}                         ir para página/capítulo anterior
 *  - onNext     {fn}                         ir para página/capítulo seguinte
 *  - onBack     {fn}                         voltar à biblioteca (tela de erro)
 */
function ReaderViewport({ status, rendering, canvasRef, onPrev, onNext, onBack }) {
  function handleViewportClick(e) {
    const half = e.currentTarget.getBoundingClientRect().width / 2;
    if (e.clientX - e.currentTarget.getBoundingClientRect().left < half) onPrev();
    else onNext();
  }

  return (
    <div className="reader-viewport" onClick={handleViewportClick}>

      {/* Loading */}
      {status === 'loading' && (
        <div className="reader-loading">
          <div className="reader-spinner" />
          <p>Carregando capítulo...</p>
        </div>
      )}

      {/* Erro */}
      {status === 'error' && (
        <div className="reader-loading">
          <span style={{ fontSize: '2rem' }}>⚠️</span>
          <p>Não foi possível carregar o capítulo.</p>
          <p style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: '4px' }}>
            Verifique se o servidor está rodando e tente novamente.
          </p>
          <button
            className="btn btn-coral"
            onClick={onBack}
            style={{ marginTop: '16px' }}
          >
            Voltar
          </button>
        </div>
      )}

      {/* Canvas + zonas de clique */}
      {status === 'ready' && (
        <>
          {/* Zona clicável: anterior (esquerda) */}
          <div
            className="reader-click-zone reader-click-prev"
            onClick={e => { e.stopPropagation(); onPrev(); }}
            title="Página anterior"
          >
            <span className="reader-click-arrow">‹</span>
          </div>

          {/* Canvas container */}
          <div
            className="reader-canvas-container"
            onClick={e => e.stopPropagation()}
          >
            {rendering && (
              <div className="reader-page-loading">
                <div className="reader-spinner reader-spinner-sm" />
              </div>
            )}
            <canvas
              ref={canvasRef}
              className="reader-canvas"
              style={{ opacity: rendering ? 0.3 : 1, transition: 'opacity 0.15s' }}
            />
          </div>

          {/* Zona clicável: próxima (direita) */}
          <div
            className="reader-click-zone reader-click-next"
            onClick={e => { e.stopPropagation(); onNext(); }}
            title="Próxima página"
          >
            <span className="reader-click-arrow">›</span>
          </div>
        </>
      )}
    </div>
  );
}

export default ReaderViewport;
