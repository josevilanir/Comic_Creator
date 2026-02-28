import React, { useState, useRef } from 'react';
import { authImgUrl } from '../../services/api';

/**
 * MangaCard — componente base reutilizável para exibição de um mangá.
 * UI com estado local de loading de ações (delete/upload).
 * Recebe dados e callbacks via props.
 */
function MangaCard({ manga, onClick, onDelete, onUploadCapa }) {
  const [isDeleting,  setIsDeleting]  = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [capaUrl,     setCapaUrl]     = useState(authImgUrl(manga.capa_url));
  const fileInputRef = useRef(null);

  async function handleDelete(e) {
    e.stopPropagation();
    if (!window.confirm(`Excluir "${manga.nome}" e TODOS os seus capítulos?

Esta ação não pode ser desfeita.`)) return;
    setIsDeleting(true);
    await onDelete(manga.nome);
    setIsDeleting(false);
  }

  function handleUploadClick(e) {
    e.preventDefault();
    e.stopPropagation();
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

  function handleCardClick() {
    if (isDeleting || isUploading) return;
    onClick();
  }

  const busy = isDeleting || isUploading;

  return (
    <>
      {/* Input fora do card — evita propagação de clique */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <div
        className="group flex flex-col gap-2 animate-in"
        onClick={handleCardClick}
        style={{ cursor: busy ? 'default' : 'pointer' }}
      >
        {/* Capa */}
        <div className="relative aspect-[2/3] rounded-xl overflow-hidden bg-[var(--cream-dark)]">
          {capaUrl ? (
            <img
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              src={capaUrl}
              alt={manga.nome}
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2">
              <span className="text-4xl opacity-40">📖</span>
              <span className="text-xs text-gray-400 font-bold uppercase tracking-wider">Sem capa</span>
            </div>
          )}

          {/* Overlay com botões — sempre visível em mobile, hover em desktop */}
          <div
            className="absolute inset-0 bg-black/40 flex items-center justify-center gap-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
            onClick={e => e.stopPropagation()}
          >
            <button
              className="bg-white rounded-full p-2 text-sm shadow disabled:opacity-50 hover:scale-110 transition-transform"
              onClick={handleUploadClick}
              disabled={busy}
              title="Trocar capa"
            >
              {isUploading ? '⏳' : '🖼'}
            </button>
            <button
              className="bg-red-500 text-white rounded-full p-2 text-sm shadow disabled:opacity-50 hover:scale-110 transition-transform"
              onClick={handleDelete}
              disabled={busy}
              title="Excluir mangá"
            >
              {isDeleting ? '⏳' : '🗑'}
            </button>
          </div>
        </div>

        {/* Info */}
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
