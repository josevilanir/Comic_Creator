import React from 'react';
import { useUrls } from '../../hooks/useUrls';
import { useDownload } from '../../hooks/useDownload';
import { useAlert } from '../../hooks/useAlert';
import Alert from '../../components/ui/Alert';
import ProgressBar from '../../components/ui/ProgressBar';
import UrlManager from '../../components/downloader/UrlManager';
import SingleDownload from '../../components/downloader/SingleDownload';
import RangeDownload from '../../components/downloader/RangeDownload';

function Downloader() {
  const { alert, showAlert } = useAlert(6000);

  const {
    urls,
    selectedManga,
    baseUrl,
    setSelectedManga,
    setBaseUrl,
    addUrl,
    removeUrl,
  } = useUrls();

  const {
    capitulo,
    setCapitulo,
    loadingSingle,
    capInicio,
    setCapInicio,
    capFim,
    setCapFim,
    jobStatus,
    rangeAtivo,
    rangeFim,
    handleDownloadSingle,
    handleDownloadRange,
    handleCancelar,
    handleNovoRange,
  } = useDownload(showAlert);

  return (
    <div className="download-page-wrapper">

      {/* Título centralizado */}
      <h1 className="download-page-title">⬇ DOWNLOADS</h1>

      {/* Alert */}
      <Alert message={alert.message} type={alert.type} />

      {/* Grid 3 colunas */}
      <div className="download-page-layout">

        {/* Coluna 1 — Sidebar */}
        <aside className="download-sidebar">
          <UrlManager
            urls={urls}
            selectedManga={selectedManga}
            baseUrl={baseUrl}
            setSelectedManga={setSelectedManga}
            setBaseUrl={setBaseUrl}
            addUrl={addUrl}
            removeUrl={removeUrl}
            showAlert={showAlert}
          />
        </aside>

        {/* Coluna 2 — Hero */}
        <div className="download-hero-area">
          {/* Decoração de fundo pontilhado */}
          <div
            className="download-hero-bg-pattern"
            aria-hidden="true"
          />

          <div className="download-hero-circle">
            <svg
              viewBox="0 0 200 200"
              width="160"
              height="160"
              className="download-hero-circle-svg"
              aria-hidden="true"
            >
              <defs>
                <path
                  id="heroCircleTextPath"
                  d="M 100, 100 m -72, 0 a 72,72 0 1,1 144,0 a 72,72 0 1,1 -144,0"
                />
              </defs>
              <text
                style={{
                  fill: 'rgba(26,18,8,0.45)',
                  fontSize: '11px',
                  fontFamily: 'var(--font-display)',
                  fontWeight: 800,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                }}
              >
                <textPath href="#heroCircleTextPath" startOffset="0%">
                  &nbsp;COMIC CREATOR OFFICIAL&nbsp;
                </textPath>
              </text>
            </svg>

            <div className="download-hero-circle-inner">
              <span>START</span>
              <span>GENERATE</span>
            </div>
          </div>

          {/* Stack de livros decorativo */}
          <div className="download-hero-books" aria-hidden="true">
            <div className="download-hero-book download-hero-book--top" />
            <div className="download-hero-book download-hero-book--mid" />
            <div className="download-hero-book download-hero-book--bot" />
          </div>
        </div>

        {/* Coluna 3 — Painéis de Download */}
        <div className="download-panels">

          {/* Painel: Download Único */}
          <div className="download-panel-card">
            <div className="download-panel-label">
              <span>⚡ Download Único</span>
              <span className="download-panel-tab-btn">Capítulo Único</span>
            </div>
            <SingleDownload
              capitulo={capitulo}
              setCapitulo={setCapitulo}
              loadingSingle={loadingSingle}
              onDownload={() => handleDownloadSingle(baseUrl, capitulo, selectedManga)}
            />
          </div>

          {/* Painel: Download em Lote */}
          <div className="download-panel-card">
            <div className="download-panel-label">
              <span>📦 Download em Lote</span>
              <span className="download-panel-tab-btn">Range</span>
            </div>
            <RangeDownload
              capInicio={capInicio}
              setCapInicio={setCapInicio}
              capFim={capFim}
              setCapFim={setCapFim}
              jobStatus={jobStatus}
              rangeAtivo={rangeAtivo}
              rangeFim={rangeFim}
              onStartRange={() => handleDownloadRange(baseUrl, capInicio, capFim, selectedManga)}
              onCancel={handleCancelar}
              onNewRange={handleNovoRange}
            />
          </div>

        </div>
      </div>

      {/* Faixa de progresso — fora do grid, abaixo */}
      {jobStatus && (
        <div className="download-progress-bar-area">
          <ProgressBar value={jobStatus.concluido} total={jobStatus.total} />
        </div>
      )}

    </div>
  );
}

export default Downloader;
