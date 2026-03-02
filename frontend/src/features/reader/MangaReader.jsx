import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { BASE_URL } from '../../services/api';
import { useProgresso } from '../../hooks/useProgresso';
import ReaderTopbar from '../../components/reader/ReaderTopbar';
import ReaderViewport from '../../components/reader/ReaderViewport';

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
  const [zoom,      setZoom]      = useState(() => window.innerWidth < 640 ? 0.7 : 1.4);
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
        const token = localStorage.getItem("access_token");
        const res = await fetch(pdfUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const buffer = await res.arrayBuffer();
        if (cancelled) return;

        const pdfjs = await getPdfJs();
        const pdf   = await pdfjs.getDocument({ data: buffer }).promise;
        if (cancelled) return;

        pdfRef.current = pdf;
        setTotal(pdf.numPages);

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
    if (nextChapter) goToChapter(nextChapter);
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

  // ── Atalhos de teclado ─────────────────────────────────────────────────────
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
      <ReaderTopbar
        decodedManga={decodedManga}
        chapterTitle={chapterTitle}
        zoom={zoom}
        onZoomIn={() => setZoom(z => Math.min(+(z + 0.15).toFixed(2), 3.0))}
        onZoomOut={() => setZoom(z => Math.max(+(z - 0.15).toFixed(2), 0.5))}
        onZoomReset={() => setZoom(1.4)}
        page={page}
        total={total}
        onPrevPage={goPrev}
        onNextPage={goNext}
        allChapters={allChapters}
        currentIdx={currentIdx}
        prevChapter={prevChapter}
        nextChapter={nextChapter}
        onPrevChapter={() => prevChapter && goToChapter(prevChapter)}
        onNextChapter={() => nextChapter && goToChapter(nextChapter)}
        onBack={goBack}
      />
      <ReaderViewport
        status={status}
        rendering={rendering}
        canvasRef={canvasRef}
        onPrev={goPrev}
        onNext={goNext}
        onBack={goBack}
      />
    </div>
  );
}

export default MangaReader;