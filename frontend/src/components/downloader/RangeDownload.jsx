import React from 'react';
import Button from '../ui/Button';
import ResultLog from './ResultLog';
import JobStatusHeader from './JobStatusHeader';
import DownloadSummary from './DownloadSummary';

/**
 * Formulário + andamento para downloads em range.
 */
function RangeDownload({
  capInicio,
  setCapInicio,
  capFim,
  setCapFim,
  jobStatus,
  rangeAtivo,
  rangeFim,
  onStartRange,
  onCancel,
  onNewRange,
}) {
  return (
    <div className="form-card">
      <div className="form-card-title">
        <div className="form-icon">📦</div>
        Range de Capítulos
        <span
          style={{
            marginLeft: 'auto',
            background: 'var(--coral-light)',
            color: 'var(--coral)',
            fontFamily: 'var(--font-display)',
            fontSize: '0.68rem',
            fontWeight: 800,
            padding: '2px 8px',
            borderRadius: 'var(--radius-full)',
          }}
        >
          Até 200 caps
        </span>
      </div>

      {/* Formulário — escondido enquanto job está rodando/concluído */}
      {!jobStatus && (
        <form
          onSubmit={e => {
            e.preventDefault();
            onStartRange();
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(min(200px, 100%), 1fr))',
              gap: '12px',
            }}
          >
            <div className="form-group">
              <label className="form-label">Do capítulo</label>
              <input
                type="number"
                className="form-input"
                placeholder="Ex: 1"
                value={capInicio}
                onChange={e => setCapInicio(e.target.value)}
                min="1"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Até o capítulo</label>
              <input
                type="number"
                className="form-input"
                placeholder="Ex: 50"
                value={capFim}
                onChange={e => setCapFim(e.target.value)}
                min="1"
              />
            </div>
          </div>

          {capInicio && capFim && parseInt(capFim, 10) >= parseInt(capInicio, 10) && (
            <div
              style={{
                marginBottom: '14px',
                padding: '8px 12px',
                background: 'var(--coral-light)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-display)',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: 'var(--coral)',
              }}
            >
              📋 {parseInt(capFim, 10) - parseInt(capInicio, 10) + 1} capítulos serão baixados
            </div>
          )}

          <Button
            type="submit"
            className="btn-coral"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            📦 Iniciar Download em Range
          </Button>
        </form>
      )}

      {/* Progresso em tempo real */}
      {jobStatus && (
        <div>
          <JobStatusHeader
            rangeAtivo={rangeAtivo}
            rangeFim={rangeFim}
            jobStatus={jobStatus}
            onCancel={onCancel}
          />

          {rangeFim && <DownloadSummary resultados={jobStatus.resultados} />}

          <ResultLog
            resultados={jobStatus.resultados}
            capAtual={rangeAtivo ? jobStatus.atual : null}
          />

          {rangeFim && (
            <Button
              className="btn-outline"
              onClick={onNewRange}
              style={{ width: '100%', justifyContent: 'center', marginTop: '14px' }}
            >
              ↩ Novo Download
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

export default RangeDownload;
