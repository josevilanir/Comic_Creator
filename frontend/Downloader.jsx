import React, { useState } from 'react';
import { useUrls } from './src/hooks/useUrls';
import { useDownload } from './src/hooks/useDownload';
import UrlManager from './src/components/downloader/UrlManager';
import SingleDownload from './src/components/downloader/SingleDownload';
import RangeDownload from './src/components/downloader/RangeDownload';
import Alert from './src/components/ui/Alert';

/**
 * Página de downloads que apenas compõe hooks e subcomponentes.
 */
function Downloader() {
  // alerta global da página
  const [alert, setAlert] = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 6000);
  }

  // hooks de domínio
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

  const urlKeys = Object.keys(urls);

  return (
    <>
      <div className="page-header">
        <div className="page-header-inner">
          <h1>⬇ <span>Downloads</span></h1>
          <p>Baixe capítulos individuais ou um range completo de uma vez.</p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '32px', paddingBottom: '64px' }}>
        <Alert message={alert.message} type={alert.type} />

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

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
            marginBottom: '24px',
          }}
        >
          <SingleDownload
            capitulo={capitulo}
            setCapitulo={setCapitulo}
            loadingSingle={loadingSingle}
            onDownload={() => handleDownloadSingle(baseUrl, capitulo, selectedManga)}
          />

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
    </>
  );
}

export default Downloader;
