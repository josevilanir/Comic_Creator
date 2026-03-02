import React from 'react';

/**
 * DownloadSummary — cards de resumo ao fim de um download em range.
 *
 * Props:
 *  - resultados  {Array}  lista de { cap, sucesso, mensagem }
 */
function DownloadSummary({ resultados }) {
  const sucessos = resultados.filter(r => r.sucesso).length;
  const falhas   = resultados.filter(r => !r.sucesso).length;

  return (
    <div
      style={{
        display: 'flex',
        gap: '12px',
        marginTop: '14px',
        flexWrap: 'wrap',
      }}
    >
      {/* Baixados */}
      <div
        style={{
          flex: 1,
          padding: '10px 14px',
          background: '#EDFAF4',
          borderRadius: 'var(--radius-sm)',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.3rem',
            fontWeight: 900,
            color: '#22A05B',
          }}
        >
          {sucessos}
        </div>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.7rem',
            fontWeight: 700,
            color: '#22A05B',
          }}
        >
          Baixados
        </div>
      </div>

      {/* Falhas */}
      <div
        style={{
          flex: 1,
          padding: '10px 14px',
          background: 'var(--coral-light)',
          borderRadius: 'var(--radius-sm)',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.3rem',
            fontWeight: 900,
            color: 'var(--coral)',
          }}
        >
          {falhas}
        </div>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.7rem',
            fontWeight: 700,
            color: 'var(--coral)',
          }}
        >
          Falhas
        </div>
      </div>
    </div>
  );
}

export default DownloadSummary;
