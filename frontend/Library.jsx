import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Pagination from './Pagination';

const ITEMS_PER_PAGE = 18;
const API = 'http://localhost:5000';

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
 * UI pura: recebe dados e callbacks via props, sem conhecer regras de negócio.
 */
function MangaCard({ manga, onClick, onDelete, onUploadCapa }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [capaUrl, setCapaUrl] = useState(manga.capa_url);
  const fileInputRef = useRef(null);

  async function handleDelete(e) {
    e.stopPropagation();
    if (!window.confirm(`Excluir "${manga.nome}" e TODOS os seus capítulos?\n\nEsta ação não pode ser desfeita.`)) return;
    setIsDeleting(true);
    await onDelete(manga.nome);
    setIsDeleting(false);
  }

  function handleUploadClick(e) {
    // Para toda propagação — botão não deve navegar nem borbulhar
    e.preventDefault();
    e.stopPropagation();
    fileInputRef.current?.click();
  }

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    const novaUrl = await onUploadCapa(manga.nome, file);
    if (novaUrl) {
      setCapaUrl(`${novaUrl}?t=${Date.now()}`);
    }
    setIsUploading(false);
    e.target.value = '';
  }

  // Impede navegação quando o card está ocupado
  function handleCardClick(e) {
    if (isDeleting || isUploading) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    onClick();
  }

  const busy = isDeleting || isUploading;

  return (
    <>
      {/*
        Input fica FORA do card — renderizado como irmão no Fragment.
        Assim o clique no input nunca pode borbulhar até o div do card,
        eliminando a navegação acidental ao abrir o seletor de arquivo.
      */}
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
        {capaUrl ? (
          <img className="card-thumb" src={capaUrl} alt={manga.nome} loading="lazy" />
        ) : (
          <div className="card-no-thumb">
            <span className="card-no-thumb-icon">📖</span>
            <span className="card-no-thumb-text">Sem capa</span>
          </div>
        )}

        {/* Overlay hover */}
        <div className="card-overlay">
          <span className="card-overlay-label">Ver capítulos →</span>
        </div>

        {/* Botões de ação flutuantes — stopPropagation no wrapper garante isolamento */}
        <div className="card-actions-float" onClick={e => e.stopPropagation()}>
          <button
            className="card-action-btn card-action-upload"
            onClick={handleUploadClick}
            disabled={busy}
            title="Trocar capa"
            aria-label="Trocar capa"
          >
            {isUploading ? '⏳' : '🖼'}
          </button>

          <button
            className="card-action-btn card-action-delete"
            onClick={handleDelete}
            disabled={busy}
            title="Excluir mangá"
            aria-label="Excluir mangá"
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
              <span className="card-badge">NEW</span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

// ─── Library ──────────────────────────────────────────────────────────────────
/**
 * Library — página principal da biblioteca.
 * Gerencia estado e lógica de dados; delega UI ao MangaCard.
 */
function Library() {
  const [mangas, setMangas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [toast, setToast] = useState({ message: '', type: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API}/api/library`)
      .then(res => res.json())
      .then(data => {
        setMangas(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erro ao carregar biblioteca:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => { setCurrentPage(1); }, [search]);

  function showToast(message, type = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast({ message: '', type: '' }), 4000);
  }

  // ── Handlers ──────────────────────────────────────────────────────────────

  async function handleDelete(nomeManga) {
    try {
      const res = await fetch(
        `${API}/api/library/${encodeURIComponent(nomeManga)}`,
        { method: 'DELETE' }
      );
      const data = await res.json();
      if (data.success) {
        setMangas(prev => prev.filter(m => m.nome !== nomeManga));
        showToast(`"${nomeManga}" excluído com sucesso.`, 'success');
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
      const res = await fetch(
        `${API}/api/library/${encodeURIComponent(nomeManga)}/capa`,
        { method: 'POST', body: formData }
      );
      const data = await res.json();
      if (data.success) {
        showToast(`Capa de "${nomeManga}" atualizada!`, 'success');
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

  // ── Filtro e paginação ────────────────────────────────────────────────────

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

  // ── Render ────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="container">
        <div className="page-hero">
          <h1>BIBLIO<span>TECA</span></h1>
        </div>
        <div className="loading-grid">
          {Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-hero">
        <h1>BIBLIO<span>TECA</span></h1>
        <p>Todos os seus mangás organizados em um só lugar.</p>
      </div>

      {toast.message && (
        <div className={`alert alert-${toast.type}`}>
          <span>{toast.type === 'success' ? '✓' : '✕'}</span>
          {toast.message}
        </div>
      )}

      <div className="search-wrap">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          className="search-input"
          placeholder="Buscar mangá..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Buscar mangá"
        />
      </div>

      <div className="section-header">
        <h2 className="section-title">Coleção</h2>
        <span className="section-count">
          {filtered.length} {filtered.length === 1 ? 'título' : 'títulos'}
          {totalPages > 1 && ` · Pág. ${currentPage}/${totalPages}`}
        </span>
      </div>

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
              <p>Baixe seus primeiros mangás na aba <strong>Baixar</strong>.</p>
            </>
          )}
        </div>
      )}

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

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
}

export default Library;