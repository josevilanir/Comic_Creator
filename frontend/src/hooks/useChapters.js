import { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';

const ITEMS_PER_PAGE = 20;

export function useChapters(mangaName) {
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingFile, setDeletingFile] = useState(null);
  const [alert, setAlert] = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 4000);
  }

  useEffect(() => {
    setLoading(true);
    api.getChapters(mangaName, sortOrder)
      .then(data => {
        const lista = data.chapters ?? data.capitulos ?? [];
        setChapters(Array.isArray(lista) ? lista : []);
      })
      .catch(err => {
        console.error('Erro ao carregar capítulos:', err);
      })
      .finally(() => setLoading(false));
  }, [mangaName, sortOrder]);

  const sorted = useMemo(() => {
    return [...chapters].sort((a, b) => {
      const numA = parseInt(a.title?.match(/\d+/)?.[0] ?? 0, 10);
      const numB = parseInt(b.title?.match(/\d+/)?.[0] ?? 0, 10);
      return sortOrder === 'asc' ? numA - numB : numB - numA;
    });
  }, [chapters, sortOrder]);

  const totalPages = Math.ceil(sorted.length / ITEMS_PER_PAGE);

  const paginated = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return sorted.slice(start, start + ITEMS_PER_PAGE);
  }, [sorted, currentPage]);

  function toggleSort() {
    setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  }

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function handleDelete(filename) {
    if (!window.confirm(`Excluir o capítulo "${filename.replace('.pdf', '')}"?\n\nEsta ação não pode ser desfeita.`))
      return;

    setDeletingFile(filename);
    try {
      const data = await api.deleteChapter(mangaName, filename);
      if (data.success) {
        setChapters(prev => prev.filter(c => c.filename !== filename));
        showAlert(data.message || 'Capítulo excluído!');
      } else {
        showAlert(data.message || 'Erro ao excluir capítulo.', 'error');
      }
    } catch (err) {
      showAlert(`Erro de conexão: ${err.message}`, 'error');
    } finally {
      setDeletingFile(null);
    }
  }

  return {
    loading,
    alert,
    sorted,
    paginated,
    sortOrder,
    currentPage,
    totalPages,
    deletingFile,
    toggleSort,
    handlePageChange,
    handleDelete,
  };
}
