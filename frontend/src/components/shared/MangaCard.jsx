import React, { useState, useRef } from 'react';
import { authImgUrl } from '../../services/api';
import { useLongPress } from '../../hooks/useLongPress';
import { useIsTouchDevice } from '../../hooks/useIsTouchDevice';

// ── Ícones SVG minimalistas ────────────────────────────────────────────────────
const IconEdit = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
);

const IconDelete = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
    <path d="M10 11v6M14 11v6"/>
    <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
  </svg>
);

/**
 * MangaCard
 *
 * Mobile (touch):
 *   - Toque simples → navega para capítulos
 *   - Toque longo   → exibe overlay com ícones no canto inferior direito
 *
 * Desktop (mouse):
 *   - Hover         → exibe overlay com nº de capítulos centralizado
 *                     + ícones no canto inferior direito
 *   - Clique        → navega para capítulos
 */
function MangaCard({ manga, onClick, onDelete, onUploadCapa }) {
  const [isDeleting,  setIsDeleting]  = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [capaUrl,     setCapaUrl]     = useState(authImgUrl(manga.capa_url));
  const [menuOpen,    setMenuOpen]    = useState(false);
  const [hovered,     setHovered]     = useState(false);

  const fileInputRef = useRef(null);
  const didLongPress = useRef(false);   // swallow synthetic click pós-long-press
  const isTouch      = useIsTouchDevice();

  const showOverlay = isTouch ? menuOpen : hovered;

  // ── Ações ─────────────────────────────────────────────────────────────────
  async function doDelete() {
    if (!window.confirm(
      `Excluir "${manga.nome}" e TODOS os seus capítulos?\n\nEsta ação não pode ser desfeita.`
    )) return;
    setIsDeleting(true);
    await onDelete(manga.nome);
    setIsDeleting(false);
  }

  function handleUploadClick(e) {
    e.stopPropagation();
    setMenuOpen(false);
    fileInputRef.current?.click();
  }

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    const novaUrl = await onUploadCapa(manga.nome, file);
    if (novaUrl) setCapaUrl(authImgUrl(`${novaUrl}?t=${Date.now()}`));
    setIsUploading(false);
    e.target.value = '';
  }

  // ── Long press (mobile) ───────────────────────────────────────────────────
  const longPressProps = useLongPress(() => {
    didLongPress.current = true;
    setMenuOpen(true);
  }, 500);

  // ── Clique ────────────────────────────────────────────────────────────────
  function handleCardClick() {
    if (didLongPress.current) { didLongPress.current = false; return; }
    if (menuOpen) { setMenuOpen(false); return; }
    if (isDeleting || isUploading) return;
    onClick();
  }

  const busy = isDeleting || isUploading;

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <div
        className="flex flex-col gap-2 animate-in select-none"
        onClick={handleCardClick}
        style={{ cursor: busy ? 'default' : 'pointer' }}
      >
        {/* ── Capa ── */}
        <div
          className="relative aspect-[2/3] rounded-xl overflow-hidden bg-[var(--cream-dark)]"
          {...(isTouch ? longPressProps : {})}
          onMouseEnter={() => !isTouch && setHovered(true)}
          onMouseLeave={() => !isTouch && setHovered(false)}
        >
          {capaUrl ? (
            <img
              className={`w-full h-full object-cover transition-transform duration-300 ${hovered ? 'scale-105' : ''}`}
              src={capaUrl}
              alt={manga.nome}
              loading="lazy"
              draggable={false}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2">
              <span className="text-4xl opacity-40">📖</span>
              <span className="text-xs text-gray-400 font-bold uppercase tracking-wider">Sem capa</span>
            </div>
          )}

          {/* Overlay — desktop hover ou mobile long press */}
          {showOverlay && (
            <div
              className="absolute inset-0 bg-black/40"
              onClick={e => e.stopPropagation()}
            >
              {/* Nº de capítulos — só no desktop, centralizado */}
              {!isTouch && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-white text-sm font-medium bg-black/30 px-3 py-1 rounded-full">
                    {manga.total_capitulos != null
                      ? `${manga.total_capitulos} capítulos`
                      : 'Sem capítulos'}
                  </span>
                </div>
              )}

              {/* Botões — canto inferior direito */}
              <div className="absolute bottom-2 right-2 flex gap-2">
                <button
                  className="bg-white/90 text-gray-700 rounded-full p-2 shadow-md
                             hover:bg-white transition-colors disabled:opacity-50"
                  onClick={handleUploadClick}
                  disabled={busy}
                  title="Trocar capa"
                >
                  {isUploading ? '…' : <IconEdit />}
                </button>
                <button
                  className="bg-red-500/90 text-white rounded-full p-2 shadow-md
                             hover:bg-red-500 transition-colors disabled:opacity-50"
                  onClick={(e) => { e.stopPropagation(); doDelete(); setMenuOpen(false); }}
                  disabled={busy}
                  title="Excluir mangá"
                >
                  {isDeleting ? '…' : <IconDelete />}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── Info ── */}
        <div>
          <p className="text-sm font-bold text-gray-900 truncate leading-tight">{manga.nome}</p>
          <div className="flex items-center justify-between mt-1">
            {/* Capítulos abaixo da capa — visível só no mobile */}
            <span className="text-xs text-gray-400 md:hidden">
              {manga.total_capitulos != null ? `${manga.total_capitulos} cap.` : '—'}
            </span>
            {manga.total_capitulos > 0 && (
              <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-bold ml-auto">
                PDF
              </span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default MangaCard;
