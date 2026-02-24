import React, { useEffect, useRef } from 'react';

/**
 * Lista de resultados de cada capítulo do range, exibida durante e após o download.
 */
function ResultLog({ resultados, capAtual }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [resultados.length]);

  if (resultados.length === 0 && !capAtual) return null;

  return (
    <div
      style={{
        marginTop: '16px',
        background: 'var(--bg)',
        border: '1.5px solid var(--card-border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: '10px 14px',
          borderBottom: '1px solid var(--card-border)',
          fontFamily: 'var(--font-display)',
          fontSize: '0.75rem',
          fontWeight: 800,
          color: 'var(--text-500)',
          letterSpacing: '0.07em',
          textTransform: 'uppercase',
        }}
      >
        Log de Download
      </div>
      <div style={{ maxHeight: '200px', overflowY: 'auto', padding: '8px 0' }}>
        {/* Capítulo sendo baixado agora */}
        {capAtual && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '6px 14px',
            }}
          >
            <span
              style={{ fontSize: '0.8rem', animation: 'spin 1s linear infinite', display: 'inline-block' }}
            >
              ⏳
            </span>
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.82rem',
                fontWeight: 700,
                color: 'var(--text-500)',
              }}
            >
              Baixando capítulo {capAtual}...
            </span>
          </div>
        )}
        {/* Resultados anteriores (mais recente no topo) */}
        {[...resultados].reverse().map((r, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              padding: '6px 14px',
              borderTop: i > 0 ? '1px solid var(--card-border)' : 'none',
            }}
          >
            <span
              style={{ fontSize: '0.85rem', flexShrink: 0, marginTop: '1px' }}
            >
              {r.sucesso ? '✅' : '❌'}
            </span>
            <div>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.82rem',
                  fontWeight: 800,
                  color: r.sucesso ? 'var(--text-900)' : 'var(--coral)',
                }}
              >
                Capítulo {r.cap}
              </span>
              <span
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.78rem',
                  color: 'var(--text-300)',
                  marginLeft: '8px',
                }}
              >
                {r.mensagem}
              </span>
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}

export default ResultLog;
