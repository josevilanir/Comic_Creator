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
        className="manga-card animate-in"
        onClick={handleCardClick}
        style={{ cursor: busy ? 'default' : 'pointer' }}
      >
        {/* Capa */}
        <div className="card-thumb-wrap">
          {capaUrl ? (
            <img className="card-thumb" src={capaUrl} alt={manga.nome} loading="lazy" />
          ) : (
            <div className="card-no-thumb">
              <span className="card-no-thumb-icon">📖</span>
              <span className="card-no-thumb-text">Sem capa</span>
            </div>
          )}
        </div>

        {/* Overlay hover */}
        <div className="card-overlay">
          <span className="card-overlay-label">Ver capítulos →</span>
        </div>

        {/* Ações flutuantes */}
        <div className="card-actions-float" onClick={e => e.stopPropagation()}>
          <button
            className="card-action-btn card-action-upload"
            onClick={handleUploadClick}
            disabled={busy}
            title="Trocar capa"
          >
            {isUploading ? '⏳' : '🖼'}
          </button>
          <button
            className="card-action-btn card-action-delete"
            onClick={handleDelete}
            disabled={busy}
            title="Excluir mangá"
          >
            {isDeleting ? '⏳' : '🗑'}
          </button>
        </div>

        {/* Info */}
        <div className="card-body">
          <h3 className="card-title">{manga.nome}</h3>
          <div className="card-meta">
            <span className="card-chapters">
              {manga.total_capitulos != null ? `${manga.total_capitulos} cap.` : '—'}
            </span>
            {manga.total_capitulos > 0 && (
              <span className="card-badge">PDF</span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default MangaCard;
