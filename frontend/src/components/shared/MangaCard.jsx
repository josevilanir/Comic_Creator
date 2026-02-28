import React, { useState, useRef } from 'react';
import { authImgUrl } from '../../services/api';
import { useLongPress } from '../../hooks/useLongPress';

/**
 * MangaCard — exibe capa e info do mangá.
 *
 * Interação:
 *   - Toque simples / clique  → navega para capítulos
 *   - Toque longo (500ms)     → abre menu de ações no canto inferior da capa
 *   - Hover desktop           → mesmo menu aparece via CSS (group-hover)
 */
function MangaCard({ manga, onClick, onDelete, onUploadCapa }) {
  const [isDeleting,  setIsDeleting]  = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [capaUrl,     setCapaUrl]     = useState(authImgUrl(manga.capa_url));
  const [menuOpen,    setMenuOpen]    = useState(false);

  const fileInputRef = useRef(null);
  // Evita que o synthetic click pós-long-press dispare navegação
  const didLongPress = useRef(false);

  // ── Ações ─────────────────────────────────────────────────────────────────
  async function doDelete() {
    if (!window.confirm(`Excluir "${manga.nome}" e TODOS os seus capítulos?\n\nEsta ação não pode ser desfeita.`)) return;
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

  // ── Long press ────────────────────────────────────────────────────────────
  const longPressProps = useLongPress(() => {
    didLongPress.current = true;
    setMenuOpen(true);
  }, 500);

  // ── Clique no card ────────────────────────────────────────────────────────
  function handleCardClick() {
    // Swallow the synthetic click that fires right after a touch long-press
    if (didLongPress.current) {
      didLongPress.current = false;
      return;
    }
    if (menuOpen) {
      setMenuOpen(false);
      return;
    }
    if (isDeleting || isUploading) return;
    onClick();
  }

  const busy = isDeleting || isUploading;

  return (
    <>
      {/* Input de arquivo fora do card — evita propagação de clique */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <div
        className="group flex flex-col gap-2 animate-in select-none"
        onClick={handleCardClick}
        style={{ cursor: busy ? 'default' : 'pointer' }}
      >
        {/* ── Capa ── */}
        <div
          className="relative aspect-[2/3] rounded-xl overflow-hidden bg-[var(--cream-dark)]"
          {...longPressProps}
        >
          {capaUrl ? (
            <img
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
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

          {/* Overlay — oculto por padrão; aparece no hover (desktop) ou long press */}
          <div
            className={`absolute inset-0 bg-black/40 flex flex-col justify-end pb-2 transition-opacity
              ${menuOpen ? 'opacity-100' : 'opacity-0 md:group-hover:opacity-100'}`}
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-center gap-3">
              <button
                className="bg-white/90 backdrop-blur-sm rounded-full p-2.5 shadow-lg text-sm
                           disabled:opacity-50 hover:scale-110 transition-transform"
                onClick={handleUploadClick}
                disabled={busy}
                title="Trocar capa"
              >
                {isUploading ? '⏳' : '🖼️'}
              </button>
              <button
                className="bg-red-500/90 backdrop-blur-sm text-white rounded-full p-2.5 shadow-lg text-sm
                           disabled:opacity-50 hover:scale-110 transition-transform"
                onClick={(e) => { e.stopPropagation(); doDelete(); setMenuOpen(false); }}
                disabled={busy}
                title="Excluir mangá"
              >
                {isDeleting ? '⏳' : '🗑️'}
              </button>
            </div>
          </div>
        </div>

        {/* ── Info ── */}
        <div>
          <p className="text-sm font-bold text-gray-900 truncate leading-tight">{manga.nome}</p>
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-gray-400">
              {manga.total_capitulos != null ? `${manga.total_capitulos} cap.` : '—'}
            </span>
            {manga.total_capitulos > 0 && (
              <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-bold">PDF</span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default MangaCard;
