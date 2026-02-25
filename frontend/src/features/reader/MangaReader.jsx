import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { BASE_URL } from '../../services/api';
import { useProgresso } from '../../hooks/useProgresso';

// ─── PDF.js lazy loader ────────────────────────────────────────────────────────
let _pdfjsLib = null;

async function getPdfJs() {
  if (_pdfjsLib) return _pdfjsLib;

  await new Promise((resolve, reject) => {
    if (window['pdfjs-dist/build/pdf']) { resolve(); return; }
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
    s.onload  = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });

  _pdfjsLib = window['pdfjs-dist/build/pdf'];
  _pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

  return _pdfjsLib;
}

/**
 * MangaReader — leitor de capítulo página a página.
 *
 * Estratégia CORS:
 *   O browser bloqueia pdfjs.getDocument({url}) cross-origin.
 *   Fazemos o fetch do PDF com React (credentials: 'include'),
 *   convertemos para ArrayBuffer e passamos para pdfjs.getDocument({data}).
 *   Assim o browser faz UMA requisição que pode ter CORS; o PDF.js
 *   recebe bytes puros e nunca tenta buscar cross-origin por conta própria.
 *
 * Rota: /manga/:mangaName/ler/:filename
 * state: { chapters: [...] }
 */
function MangaReader() {
  const { mangaName, filename } = useParams();
  const navigate  = useNavigate();
  const location  = useLocation();

  const decodedManga = decodeURIComponent(mangaName);
  const decodedFile  = decodeURIComponent(filename);
  const chapterTitle = decodedFile.replace('.pdf', '').replace(/_/g, ' ');

  const { loadProgresso, saveProgresso } = useProgresso(decodedManga, decodedFile);

  const allChapters = location.state?.chapters ?? [];
  const currentIdx  = allChapters.findIndex(c => c.filename === decodedFile);
  const prevChapter = currentIdx > 0                       ? allChapters[currentIdx - 1] : null;
  const nextChapter = currentIdx < allChapters.length - 1  ? allChapters[currentIdx + 1] : null;

  const pdfUrl = `${BASE_URL}/capitulo/visualizar/${encodeURIComponent(decodedManga)}/${encodeURIComponent(decodedFile)}`;

  // ── Estado ─────────────────────────────────────────────────────────────────
  const canvasRef  = useRef(null);
  const pdfRef     = useRef(null);
  const renderTask = useRef(null);

  const [page,      setPage]      = useState(1);
  const [total,     setTotal]     = useState(0);
  const [zoom,      setZoom]      = useState(1.4);
  const [status,    setStatus]    = useState('loading'); // 'loading' | 'ready' | 'error'
  const [rendering, setRendering] = useState(false);

  // ── Carrega PDF como ArrayBuffer → entrega ao PDF.js ──────────────────────
  useEffect(() => {
    let cancelled = false;

    async function load() {
      setStatus('loading');
      setPage(1);
      setTotal(0);
      pdfRef.current = null;

      try {
        // 1. Busca o PDF binário com fetch (CORS resolvido no backend por /capitulo/*)
        const token = localStorage.getItem("access_token");
        const res = await fetch(pdfUrl, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const buffer = await res.arrayBuffer();
        if (cancelled) return;

        // 2. Passa os bytes diretamente ao PDF.js — sem nova requisição cross-origin
        const pdfjs = await getPdfJs();
        const pdf   = await pdfjs.getDocument({ data: buffer }).promise;
        if (cancelled) return;

        pdfRef.current = pdf;
        setTotal(pdf.numPages);
        
        // Carrega a última página salva
        const savedPage = await loadProgresso();
        const startPage = Math.min(savedPage, pdf.numPages);
        setPage(startPage);
        
        setStatus('ready');
      } catch (err) {
        if (!cancelled) {
          console.error('Erro ao carregar PDF:', err);
          setStatus('error');
        }
      }
    }

    load();
    return () => { cancelled = true; };
  }, [pdfUrl]);

  // ── Renderiza página no canvas ─────────────────────────────────────────────
  const renderPage = useCallback(async (pageNum, scale) => {
    if (!pdfRef.current || !canvasRef.current) return;

    if (renderTask.current) {
      try { renderTask.current.cancel(); } catch (_) {}
      renderTask.current = null;
    }

    setRendering(true);
    try {
      const p        = await pdfRef.current.getPage(pageNum);
      const viewport = p.getViewport({ scale });
      const canvas   = canvasRef.current;
      const ctx      = canvas.getContext('2d');

      canvas.width  = viewport.width;
      canvas.height = viewport.height;

      const task = p.render({ canvasContext: ctx, viewport });
      renderTask.current = task;
      await task.promise;
    } catch (err) {
      if (err?.name !== 'RenderingCancelledException') {
        console.error('Erro ao renderizar:', err);
      }
    } finally {
      setRendering(false);
    }
  }, []);

  useEffect(() => {
    if (status === 'ready') renderPage(page, zoom);
  }, [status, page, zoom, renderPage]);

  // ── Navegação ──────────────────────────────────────────────────────────────
  function goNext() {
    if (page < total) {
      const nextP = page + 1;
      setPage(nextP);
      saveProgresso(nextP);
      return;
    }
    if (nextChapter)  goToChapter(nextChapter);
  }

  function goPrev() {
    if (page > 1) {
      const prevP = page - 1;
      setPage(prevP);
      saveProgresso(prevP);
      return;
    }
    if (prevChapter) goToChapter(prevChapter);
  }

  function goToChapter(ch) {
    navigate(
      `/manga/${encodeURIComponent(decodedManga)}/ler/${encodeURIComponent(ch.filename)}`,
      { state: { chapters: allChapters } }
    );
  }

  function goBack() {
    navigate(`/manga/${encodeURIComponent(decodedManga)}`);
  }

  // Clique nas metades esquerda/direita do canvas
  function handleViewportClick(e) {
    const half = e.currentTarget.getBoundingClientRect().width / 2;
    if (e.clientX - e.currentTarget.getBoundingClientRect().left < half) goPrev();
    else goNext();
  }

  // Atalhos de teclado
  useEffect(() => {
    function onKey(e) {
      const tag = document.activeElement?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') goNext();
      if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   goPrev();
      if (e.key === '+' || e.key === '=') setZoom(z => Math.min(+(z + 0.15).toFixed(2), 3.0));
      if (e.key === '-')                  setZoom(z => Math.max(+(z - 0.15).toFixed(2), 0.5));
      if (e.key === '0')                  setZoom(1.4);
      if (e.key === 'Escape')             goBack();
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [page, total, prevChapter, nextChapter]);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="reader-shell">

      {/* TOPBAR */}
      <div className="reader-topbar">
        {/* Esquerda: voltar + título */}
        <div className="reader-topbar-left">
          <button className="reader-btn" onClick={goBack}>
            ← Voltar à Biblioteca
          </button>
          <div className="reader-title-wrap">
            <span className="reader-manga-name">{decodedManga}</span>
            <span className="reader-chapter-name">{chapterTitle}</span>
          </div>
        </div>

        {/* Centro: zoom */}
        <div className="reader-controls-center">
          <button className="reader-ctrl-btn"
            onClick={() => setZoom(z => Math.max(+(z - 0.15).toFixed(2), 0.5))}
            title="Diminuir zoom (−)">−</button>
          <button className="reader-zoom-display"
            onClick={() => setZoom(1.4)}
            title="Resetar zoom (0)">
            {Math.round(zoom * 100)}%
          </button>
          <button className="reader-ctrl-btn"
            onClick={() => setZoom(z => Math.min(+(z + 0.15).toFixed(2), 3.0))}
            title="Aumentar zoom (+)">+</button>
        </div>

        {/* Direita: nav capítulos + contador páginas */}
        <div className="reader-topbar-right">
          {allChapters.length > 1 && (
            <div className="reader-chapter-nav">
              <button className="reader-nav-btn"
                onClick={() => prevChapter && goToChapter(prevChapter)}
                disabled={!prevChapter} title="Capítulo anterior">‹</button>
              <span className="reader-chapter-pos">
                Cap. {currentIdx + 1}/{allChapters.length}
              </span>
              <button className="reader-nav-btn"
                onClick={() => nextChapter && goToChapter(nextChapter)}
                disabled={!nextChapter} title="Próximo capítulo">›</button>
            </div>
          )}

          {total > 0 && (
            <div className="reader-page-counter">
              <button className="reader-nav-btn"
                onClick={goPrev}
                disabled={page === 1 && !prevChapter}
                title="Página anterior (←)">‹</button>
              <span className="reader-chapter-pos">{page} / {total}</span>
              <button className="reader-nav-btn"
                onClick={goNext}
                disabled={page === total && !nextChapter}
                title="Próxima página (→)">›</button>
            </div>
          )}
        </div>
      </div>

      {/* VIEWPORT */}
      <div className="reader-viewport" onClick={handleViewportClick}>

        {/* Loading */}
        {status === 'loading' && (
          <div className="reader-loading">
            <div className="reader-spinner" />
            <p>Carregando capítulo...</p>
          </div>
        )}

        {/* Erro */}
        {status === 'error' && (
          <div className="reader-loading">
            <span style={{ fontSize: '2rem' }}>⚠️</span>
            <p>Não foi possível carregar o capítulo.</p>
            <p style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: '4px' }}>
              Verifique se o servidor está rodando e tente novamente.
            </p>
            <button className="btn btn-coral" onClick={goBack}
              style={{ marginTop: '16px' }}>
              Voltar
            </button>
          </div>
        )}

        {/* Canvas */}
        {status === 'ready' && (
          <>
            {/* Zona clicável: anterior (esquerda) */}
            <div className="reader-click-zone reader-click-prev"
              onClick={e => { e.stopPropagation(); goPrev(); }}
              title="Página anterior">
              <span className="reader-click-arrow">‹</span>
            </div>

            {/* Canvas container */}
            <div className="reader-canvas-container"
              onClick={e => e.stopPropagation()}>
              {rendering && (
                <div className="reader-page-loading">
                  <div className="reader-spinner reader-spinner-sm" />
                </div>
              )}
              <canvas
                ref={canvasRef}
                className="reader-canvas"
                style={{ opacity: rendering ? 0.3 : 1, transition: 'opacity 0.15s' }}
              />
            </div>

            {/* Zona clicável: próxima (direita) */}
            <div className="reader-click-zone reader-click-next"
              onClick={e => { e.stopPropagation(); goNext(); }}
              title="Próxima página">
              <span className="reader-click-arrow">›</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default MangaReader;