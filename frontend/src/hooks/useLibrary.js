import { useState, useEffect, useMemo } from 'react';
import { useAlert } from './useAlert';
import { api } from '../services/api';

const ITEMS_PER_PAGE = 18;

export function useLibrary() {
  const { alert, showAlert } = useAlert(4000);
  const [mangas, setMangas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    api.getLibrary()
      .then(data => setMangas(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { setCurrentPage(1); }, [search]);

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

  async function handleDelete(nomeManga) {
    try {
      const data = await api.deleteManga(nomeManga);
      if (data.success) {
        setMangas(prev => prev.filter(m => m.nome !== nomeManga));
        showAlert(`"${nomeManga}" excluído com sucesso.`);
      } else {
        showAlert(data.message || 'Erro ao excluir.', 'error');
      }
    } catch (err) {
      showAlert(`Erro de conexão: ${err.message}`, 'error');
    }
  }

  async function handleUploadCapa(nomeManga, file) {
    const formData = new FormData();
    formData.append('capa', file);
    try {
      const data = await api.uploadCover(nomeManga, formData);
      if (data.success) {
        showAlert(`Capa de "${nomeManga}" atualizada!`);
        return data.capa_url;
      } else {
        showAlert(data.message || 'Erro ao enviar capa.', 'error');
        return null;
      }
    } catch (err) {
      showAlert(`Erro de conexão: ${err.message}`, 'error');
      return null;
    }
  }

  return {
    alert,
    loading,
    search,
    setSearch,
    filtered,
    paginated,
    currentPage,
    totalPages,
    handlePageChange,
    handleDelete,
    handleUploadCapa,
  };
}
