import React from 'react';

/**
 * Barra de progresso reutilizável exibindo valor/totais e %.
 */
function ProgressBar({ value, total }) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div style={{ marginTop: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.78rem',
            fontWeight: 700,
            color: 'var(--text-500)',
          }}
        >
          Progresso
        </span>
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.78rem',
            fontWeight: 800,
            color: 'var(--coral)',
          }}
        >
          {value} / {total} capítulos
        </span>
      </div>
      <div
        style={{
          height: '8px',
          borderRadius: '99px',
          background: 'var(--cream-dark)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            borderRadius: '99px',
            background: 'linear-gradient(90deg, var(--coral-dark), var(--coral))',
            width: `${pct}%`,
            transition: 'width 0.4s ease',
            boxShadow: pct > 0 ? '0 0 8px rgba(232,65,42,0.4)' : 'none',
          }}
        />
      </div>
      <div
        style={{
          textAlign: 'right',
          marginTop: '4px',
          fontFamily: 'var(--font-display)',
          fontSize: '0.7rem',
          fontWeight: 700,
          color: 'var(--text-300)',
        }}
      >
        {pct}%
      </div>
    </div>
  );
}

export default ProgressBar;
