import React from 'react';
import { useUrls } from '../../hooks/useUrls';
import { useDownload } from '../../hooks/useDownload';
import { useAlert } from '../../hooks/useAlert';
import UrlManager from '../../components/downloader/UrlManager';
import SingleDownload from '../../components/downloader/SingleDownload';
import RangeDownload from '../../components/downloader/RangeDownload';
import Alert from '../../components/ui/Alert';

/**
 * Página de downloads que apenas compõe hooks e subcomponentes.
 */
function Downloader() {
  const { alert, showAlert } = useAlert(6000);

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
    <div className="bento-page-container">
      <div className="bento-page-header">
        <div className="bento-page-header-inner">
          <h1>⬇ <span>Downloads</span></h1>
          <p>Baixe capítulos individuais ou um range completo de uma vez.</p>
        </div>
      </div>

      <div className="bento-layout-card bg-white p-6 sm:p-8 flex flex-col gap-8 relative">
        <div className="absolute top-4 right-4 z-50">
           <Alert message={alert.message} type={alert.type} />
        </div>

        <div className="bento-layout-card bg-[var(--cream-dark)] p-6">
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
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bento-layout-card bg-gradient-to-br from-blue-50 to-indigo-50 p-6 flex flex-col h-full border-blue-900 border-opacity-20 border-2">
            <h2 className="font-black text-xl uppercase mb-6 flex items-center gap-2"><span className="text-2xl">⚡</span> Download Único</h2>
             <SingleDownload
               capitulo={capitulo}
               setCapitulo={setCapitulo}
               loadingSingle={loadingSingle}
               onDownload={() => handleDownloadSingle(baseUrl, capitulo, selectedManga)}
             />
          </div>

          <div className="bento-layout-card bg-gradient-to-br from-green-50 to-emerald-50 p-6 flex flex-col h-full border-green-900 border-opacity-20 border-2">
            <h2 className="font-black text-xl uppercase mb-6 flex items-center gap-2"><span className="text-2xl">📦</span> Download em Lote (Range)</h2>
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
    </div>
  );
}

export default Downloader;
