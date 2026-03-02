import React from 'react';
import { useUrls } from '../../hooks/useUrls';
import { useDownload } from '../../hooks/useDownload';
import { useAlert } from '../../hooks/useAlert';
import Alert from '../../components/ui/Alert';

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

  const urlKeys = Object.keys(urls);

  return (
    <div className="w-full max-w-[1400px] mx-auto min-h-full flex flex-col p-4 md:p-8">
      
      {/* HEADER */}
      <div className="text-center mb-6">
        <h1 className="font-black text-3xl md:text-4xl tracking-tighter uppercase text-[var(--text-900)]">
          ↓ Downloads
        </h1>
      </div>

      {/* ALERT */}
      <div className="fixed top-4 right-4 z-50">
        <Alert message={alert.message} type={alert.type} />
      </div>

      {/* MAIN GRID */}
      <div className="flex flex-col lg:flex-row gap-4 h-full">
        
        {/* LEFT SIDEBAR (Config & URLs) */}
        <div className="bento-layout-card bg-[#D6CEB8] w-full lg:w-[320px] flex-shrink-0 flex flex-col p-5 gap-6 border-[2px] border-[#3D3220] rounded-2xl">
          
          {/* Configurações do Manga */}
          <div className="flex flex-col gap-3">
            <h3 className="font-bold text-[#3D3220] flex items-center gap-2">
              <span>⚙</span> Configurações do Manga
            </h3>
            
            <div className="flex flex-col gap-1">
              <label className="text-xs font-bold uppercase text-[#7A6E60]">Selecionar Manga Salvo</label>
              <select
                className="bg-[#F5F0E8] border border-[#3D3220] rounded-md px-3 py-2 text-sm text-[#3D3220] focus:outline-none"
                value={selectedManga}
                onChange={e => setSelectedManga(e.target.value)}
              >
                <option value="">- Selecionar Manga Salvo -</option>
                {urlKeys.map(nome => <option key={nome} value={nome}>{nome}</option>)}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-bold uppercase text-[#7A6E60]">URL Base</label>
              <input
                type="url"
                className="bg-[#F5F0E8] border border-[#3D3220] rounded-md px-3 py-2 text-sm text-[#3D3220] focus:outline-none"
                placeholder="https://tis.com/manga/itah/capitulo-"
                value={baseUrl}
                onChange={e => setBaseUrl(e.target.value)}
              />
            </div>
          </div>

          <hr className="border-[#A69B87] opacity-30" />

          {/* Gerenciar URLs */}
          <div className="flex flex-col gap-3 flex-1">
            <h3 className="font-bold text-[#3D3220] flex items-center gap-2">
              <span>🗂</span> Gerenciar URLs
            </h3>
            
            <h4 className="font-bold text-sm mt-2 text-[#3D3220]">URLs Salvas</h4>
            <div className="flex flex-col gap-3 overflow-y-auto pr-1" style={{ maxHeight: '400px' }}>
              {urlKeys.map(nome => (
                <div key={nome} className="bg-white rounded-xl border border-[#3D3220] p-3 flex items-center justify-between gap-2 shadow-sm">
                  <div className="min-w-0 flex-1">
                    <p className="font-bold text-sm text-[#3D3220] truncate">{nome}</p>
                    <p className="text-xs text-gray-400 truncate mt-0.5">{urls[nome]}</p>
                  </div>
                  <button
                    onClick={() => removeUrl(nome)}
                    className="flex flex-col items-center justify-center bg-[#E8412A] text-white rounded-lg px-2 py-1 text-[0.65rem] font-bold tracking-wider hover:bg-[#C9341F] transition-colors"
                  >
                    🗑
                    <span className="mt-0.5">remover</span>
                  </button>
                </div>
              ))}
              {urlKeys.length === 0 && (
                <p className="text-xs text-[#7A6E60] italic">Nenhuma URL salva ainda.</p>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT MAIN AREA */}
        <div className="flex-1 flex flex-col gap-4">
          
          {/* TOP SECTION: Cover Area & Forms */}
          <div className="flex flex-col xl:flex-row gap-4 flex-1">
            
            {/* Cover Display Area */}
            <div className="bento-layout-card flex-1 bg-gradient-to-br from-[#FFD6C1] to-[#FCA5A5] min-h-[300px] border-[2px] border-[#3D3220] rounded-2xl relative flex items-center justify-center p-8 overflow-hidden">
              {/* Spinning Text Badge (Reused logic) */}
              <div className="absolute top-1/2 left-1/4 -translate-y-1/2 -translate-x-1/2">
                 <div className="relative w-32 h-32 rounded-full border border-dashed border-[#3D3220] flex items-center justify-center">
                    <div className="w-16 h-16 bg-[#1A1208] text-white rounded-full flex items-center justify-center text-[0.6rem] font-bold text-center leading-tight shadow-xl cursor-pointer hover:bg-[#E8412A] transition-colors z-10">
                      START<br/>GENERATE
                    </div>
                    {/* Simulated rotating text via absolute positioning */}
                    <div className="absolute inset-0 rounded-full animate-[spin_15s_linear_infinite] pointer-events-none opacity-60 flex items-center justify-center text-xs">
                       ꩜   ꩜   ꩜   ꩜
                    </div>
                 </div>
              </div>

              {/* 3D Book Placeholder */}
              <div className="ml-24 relative z-0 mt-4 group cursor-pointer hover:scale-105 transition-transform duration-300">
                {/* Visual stack of books representation */}
                <div className="w-40 h-56 bg-emerald-500 rounded-md border-t border-l border-emerald-400 shadow-[12px_12px_0px_#A7F3D0,13px_13px_0_rgba(0,0,0,0.2)] transform -rotate-12 skew-y-12"></div>
                <div className="w-40 h-56 bg-purple-500 rounded-md border-t border-l border-purple-400 shadow-[12px_12px_0px_#DDD6FE,13px_13px_0_rgba(0,0,0,0.2)] absolute -bottom-4 left-2 transform -rotate-12 skew-y-12 -z-10"></div>
                <div className="w-40 h-56 bg-rose-400 rounded-md border-t border-l border-rose-300 shadow-[12px_12px_0px_#FECDD3,13px_13px_0_rgba(0,0,0,0.2)] absolute -bottom-8 left-4 transform -rotate-12 skew-y-12 -z-20"></div>
              </div>
            </div>

            {/* Download Forms Area */}
            <div className="w-full xl:w-[360px] flex flex-col gap-4">
              
              {/* Single Download Config */}
              <div className="bento-layout-card bg-white p-5 border-[2px] border-l-4 border-[#3D3220] border-l-[#FCA5A5] rounded-2xl flex flex-col gap-4 relative">
                <div className="absolute top-0 right-4 px-3 py-1 bg-[#F5F0E8] text-xs font-bold rounded-b-md border-x border-b border-[#3D3220]">
                  ⚡ Download Único
                </div>
                <h3 className="font-black text-xl flex items-center gap-2 mt-4 text-[#3D3220]">
                  ⚡ DOWNLOAD ÚNICO
                </h3>
                
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-bold text-[#7A6E60]">Número do Capítulo</label>
                  <input
                    type="number"
                    min="1"
                    className="bg-[#F5F0E8] border border-[#3D3220] rounded-md px-3 py-2 text-sm text-[#3D3220] focus:outline-none w-full shadow-inner"
                    placeholder="Ex: 40"
                    value={capitulo}
                    onChange={e => setCapitulo(e.target.value)}
                  />
                </div>

                <button 
                  onClick={() => handleDownloadSingle(baseUrl, capitulo, selectedManga)}
                  disabled={loadingSingle}
                  className="bg-[#E8412A] hover:bg-[#C9341F] text-white font-black py-3 rounded-full shadow-[0_4px_0_#991b1b] active:shadow-[0_0px_0_#991b1b] active:translate-y-1 transition-all mt-2"
                >
                  {loadingSingle ? '⏳ Baixando...' : '1 Baixar Capítulo'}
                </button>
              </div>

              {/* Batch Download Config */}
              <div className="bento-layout-card bg-[#8BA3B3]/20 p-5 border-[2px] border-l-4 border-[#3D3220] border-l-[#8BA3B3] rounded-2xl flex flex-col gap-4 relative">
                 <div className="absolute top-0 right-4 px-3 py-1 bg-[#F5F0E8] text-xs font-bold rounded-b-md border-x border-b border-[#3D3220]">
                  📦 Download em Lote
                </div>
                <h3 className="font-black text-xl flex items-center gap-2 mt-4 text-[#3D3220]">
                  ⚙ DOWNLOAD EM LOTE
                </h3>
                
                <div className="flex gap-2">
                  <div className="flex flex-col gap-1 w-1/2">
                     <label className="text-xs font-bold text-[#7A6E60]">Início</label>
                     <input
                         type="number" min="1"
                         className="bg-[#F5F0E8] border border-[#3D3220] rounded-md px-3 py-2 text-sm text-[#3D3220] focus:outline-none shadow-inner w-full"
                         placeholder="Ex: 1"
                         value={capInicio}
                         onChange={e => setCapInicio(e.target.value)}
                     />
                  </div>
                  <div className="flex flex-col gap-1 w-1/2">
                     <label className="text-xs font-bold text-[#7A6E60]">Fim</label>
                     <input
                         type="number" min="1"
                         className="bg-[#F5F0E8] border border-[#3D3220] rounded-md px-3 py-2 text-sm text-[#3D3220] focus:outline-none shadow-inner w-full"
                         placeholder="Ex: 50"
                         value={capFim}
                         onChange={e => setCapFim(e.target.value)}
                     />
                  </div>
                </div>

                {/* Range Slider decorativo (MVP visual) */}
                 <div className="relative w-full h-8 flex items-center my-2">
                    <div className="absolute w-full h-2 bg-[#F5F0E8] border border-[#3D3220] rounded-full"></div>
                    <div className="absolute w-[80%] h-2 bg-[#D1DF5C] border-y border-[#3D3220] left-0"></div>
                    <div className="absolute w-5 h-5 bg-[#D1DF5C] border-2 border-[#3D3220] rounded-full left-0 drop-shadow-md"></div>
                    <div className="absolute w-5 h-5 bg-[#D1DF5C] border-2 border-[#3D3220] rounded-full left-[80%] -translate-x-1/2 drop-shadow-md"></div>
                 </div>

                <button 
                  onClick={() => handleDownloadRange(baseUrl, capInicio, capFim, selectedManga)}
                  disabled={rangeAtivo}
                  className="bg-[#E8412A] hover:bg-[#C9341F] text-white font-black py-3 rounded-full shadow-[0_4px_0_#991b1b] active:shadow-[0_0px_0_#991b1b] active:translate-y-1 transition-all"
                >
                  {rangeAtivo ? '⏳ Baixando...' : 'Iniciar Download em Lote'}
                </button>
              </div>

            </div>
          </div>

          {/* BOTTOM SECTION: Gallery + Progress */}
          <div className="h-40 min-h-[160px] bg-[#C1D2DF]/40 border-[2px] border-[#3D3220] rounded-2xl relative flex flex-col justify-end overflow-hidden p-4">
             {/* Thumbnail Placeholders floating faintly in the bg */}
             <div className="absolute top-2 left-8 flex gap-4 opacity-50 pointer-events-none">
                <div className="w-16 h-24 bg-white border border-[#3D3220] rounded-sm transform -rotate-6"></div>
                <div className="w-16 h-24 bg-white border border-[#3D3220] rounded-sm transform rotate-3"></div>
                <div className="w-16 h-24 bg-white border border-[#3D3220] rounded-sm transform -rotate-12 translate-y-4"></div>
             </div>

             {/* Progress Bar Container */}
             <div className="w-full bg-[#f8f5ee] border-[2px] border-[#3D3220] rounded-xl h-20 flex items-center p-4 relative z-10 shadow-lg">
                
                {/* Character Icon Placeholder */}
                <div className="w-16 h-16 mr-4 bg-white border-2 border-[#3D3220] rounded-full flex items-center justify-center -ml-8 -mt-8 relative z-20 shadow-md transform -rotate-12 bg-[url('https://api.dicebear.com/7.x/bottts/svg?seed=mangas')] bg-cover"></div>
                
                {/* Progress bar logic hookup */}
                <div className="flex-1 bg-gray-200 h-4 rounded-full border border-[#3D3220] overflow-hidden relative">
                   <div 
                     className="absolute top-0 left-0 h-full bg-[#D1DF5C] transition-all duration-300"
                     style={{ width: jobStatus ? `${(jobStatus.concluido / jobStatus.total) * 100}%` : '0%' }}
                   ></div>
                </div>

                {jobStatus && (
                  <div className="ml-4 font-black text-sm text-[#3D3220]">
                    {jobStatus.concluido} / {jobStatus.total}
                  </div>
                )}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Downloader;
