import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Pagination from '../../components/shared/Pagination';
import { api } from '../../services/api';

const ITEMS_PER_PAGE = 18;

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-thumb" />
      <div className="skeleton-body">
        <div className="skeleton-line" />
        <div className="skeleton-line short" />
      </div>
    </div>
  );
}

// ─── MangaCard ────────────────────────────────────────────────────────────────
/**
 * MangaCard — componente base reutilizável.
 * UI pura: recebe dados e callbacks via props.
 */
function MangaCard({ manga, onClick, onDelete, onUploadCapa }) {
  const [isDeleting,  setIsDeleting]  = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [capaUrl,     setCapaUrl]     = useState(manga.capa_url);
  const fileInputRef = useRef(null);

  async function handleDelete(e) {
    e.stopPropagation();
    if (!window.confirm(`Excluir "${manga.nome}" e TODOS os seus capítulos?\n\nEsta ação não pode ser desfeita.`)) return;
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
    if (novaUrl) setCapaUrl(`${novaUrl}?t=${Date.now()}`);
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

// ─── Library ──────────────────────────────────────────────────────────────────
function Library() {
  const [mangas,      setMangas]      = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [search,      setSearch]      = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [toast,       setToast]       = useState({ message: '', type: '' });
  const navigate = useNavigate();

  useEffect(() => {
    api.getLibrary()
      .then(data => { setMangas(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { setCurrentPage(1); }, [search]);

  function showToast(message, type = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast({ message: '', type: '' }), 4000);
  }

  async function handleDelete(nomeManga) {
    try {
      const data = await api.deleteManga(nomeManga);
      if (data.success) {
        setMangas(prev => prev.filter(m => m.nome !== nomeManga));
        showToast(`"${nomeManga}" excluído com sucesso.`);
      } else {
        showToast(data.message || 'Erro ao excluir.', 'error');
      }
    } catch (err) {
      showToast(`Erro de conexão: ${err.message}`, 'error');
    }
  }

  async function handleUploadCapa(nomeManga, file) {
    const formData = new FormData();
    formData.append('capa', file);
    try {
      const data = await api.uploadCover(nomeManga, formData);
      if (data.success) {
        showToast(`Capa de "${nomeManga}" atualizada!`);
        return data.capa_url;
      } else {
        showToast(data.message || 'Erro ao enviar capa.', 'error');
        return null;
      }
    } catch (err) {
      showToast(`Erro de conexão: ${err.message}`, 'error');
      return null;
    }
  }

  const filtered = useMemo(() => {
    if (!search.trim()) return mangas;
    const q = search.toLowerCase();
    return mangas.filter(m => m.nome.toLowerCase().includes(q));
  }, [mangas, search]);

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);

  const paginated = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filtered.slice(start, start + ITEMS_PER_PAGE);
  }, [filtered, currentPage]);

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ── Loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <>
        <div className="page-header">
          <div className="page-header-inner">
            <h1>Minha <span>Biblioteca</span></h1>
            <p>Carregando sua coleção...</p>
          </div>
        </div>
        <div className="container">
          <div className="loading-grid">
            {Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        </div>
      </>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Header da página */}
      <div className="page-header">
        <div className="page-header-inner">
          <h1>Minha <span>Biblioteca</span></h1>
          <p>Gerencie sua coleção de mangás — clique para ver capítulos.</p>
        </div>
      </div>

      <div className="container">
        {/* Toast */}
        {toast.message && (
          <div className={`alert alert-${toast.type}`}>
            <span>{toast.type === 'success' ? '✓' : '✕'}</span>
            {toast.message}
          </div>
        )}

        {/* Busca */}
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Buscar mangá..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* Stats */}
        <div className="stats-bar">
          <span className="stats-count">
            <strong>{filtered.length}</strong> {filtered.length === 1 ? 'título' : 'títulos'}
            {totalPages > 1 && ` · Página ${currentPage} de ${totalPages}`}
          </span>
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div className="empty-state">
            <span className="empty-state-emoji">📭</span>
            {search ? (
              <>
                <h3>Nada encontrado</h3>
                <p>Nenhum mangá corresponde a "{search}".</p>
              </>
            ) : (
              <>
                <h3>Biblioteca vazia</h3>
                <p>Vá em <strong>Downloads</strong> para baixar seus primeiros mangás.</p>
              </>
            )}
          </div>
        )}

        {/* Grid */}
        {paginated.length > 0 && (
          <div className="manga-grid">
            {paginated.map(manga => (
              <MangaCard
                key={manga.nome}
                manga={manga}
                onClick={() => navigate(`/manga/${encodeURIComponent(manga.nome)}`)}
                onDelete={handleDelete}
                onUploadCapa={handleUploadCapa}
              />
            ))}
          </div>
        )}

        {/* Paginação */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </div>
    </>
  );
}

export default Library;