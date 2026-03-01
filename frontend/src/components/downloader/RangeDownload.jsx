import React from 'react';
import ProgressBar from '../ui/ProgressBar';
import Button from '../ui/Button';
import ResultLog from './ResultLog';

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
          {/* Status header */}
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
              <Button className="btn-sm btn-danger" onClick={onCancel}>
                ⛔ Cancelar
              </Button>
            )}
          </div>

          <ProgressBar value={jobStatus.concluido} total={jobStatus.total} />

          {/* Resumo final */}
          {rangeFim && (
            <div
              style={{
                display: 'flex',
                gap: '12px',
                marginTop: '14px',
                flexWrap: 'wrap',
              }}
            >
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
                  {jobStatus.resultados.filter(r => r.sucesso).length}
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
                  {jobStatus.resultados.filter(r => !r.sucesso).length}
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
          )}

          {/* Log de resultados */}
          <ResultLog
            resultados={jobStatus.resultados}
            capAtual={rangeAtivo ? jobStatus.atual : null}
          />

          {/* Botão novo download */}
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
