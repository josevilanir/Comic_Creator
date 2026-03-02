import React from 'react';
import Button from '../ui/Button';

/**
 * JobStatusHeader — cabeçalho de status de um job de download em range.
 *
 * Props:
 *  - rangeAtivo  {boolean}       true enquanto o job está rodando
 *  - rangeFim    {boolean}       true quando o job terminou (sucesso ou cancelado)
 *  - jobStatus   {object}        objeto retornado pela API com { atual, status }
 *  - onCancel    {fn}            callback para cancelar o job
 */
function JobStatusHeader({ rangeAtivo, rangeFim, jobStatus, onCancel }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '4px',
      }}
    >
      <span
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.82rem',
          fontWeight: 800,
          color: 'var(--text-900)',
        }}
      >
        {rangeAtivo && `⏳ Baixando capítulo ${jobStatus.atual ?? '...'}...`}
        {rangeFim && jobStatus.status === 'concluido' && '✅ Download concluído!'}
        {rangeFim && jobStatus.status === 'cancelado' && '⛔ Download cancelado'}
      </span>

      {rangeAtivo && (
        <Button className="btn-sm btn-danger" onClick={onCancel} style={{ flexShrink: 0 }}>
          ⛔ Cancelar
        </Button>
      )}
    </div>
  );
}

export default JobStatusHeader;
