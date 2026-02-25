import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAlert } from './useAlert';
import { api } from '../services/api';

const ITEMS_PER_PAGE = 20;

export function useChapters(mangaName) {
  const { alert, showAlert } = useAlert(4000);
  const queryClient = useQueryClient();

  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingFile, setDeletingFile] = useState(null);

  // ── Fetch dos capítulos ───────────────────────────────────────────────────
  const { data: chapters = [], isLoading: loading } = useQuery({
    queryKey: ['chapters', mangaName, sortOrder],
    queryFn: () =>
      api.getChapters(mangaName, sortOrder).then(res => {
        const lista = res.data?.chapters ?? res.data?.capitulos ?? [];
        return Array.isArray(lista) ? lista : [];
      }),
    enabled: !!mangaName,
  });

  // ── Ordenação e paginação ────────────────────────────────────────────────
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

  // ── Mutation: excluir capítulo ────────────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: (filename) => api.deleteChapter(mangaName, filename),
    onMutate: (filename) => setDeletingFile(filename),
    onSuccess: (res, filename) => {
      if (res.status === 'success') {
        queryClient.setQueryData(['chapters', mangaName, sortOrder], (old = []) =>
          old.filter(c => c.filename !== filename)
        );
        showAlert(res.data?.message || 'Capítulo excluído!');
      } else {
        showAlert(res.message || 'Erro ao excluir capítulo.', 'error');
      }
    },
    onError: (err) => showAlert(`Erro de conexão: ${err.message}`, 'error'),
    onSettled: () => setDeletingFile(null),
  });

  // ── Mutation: toggle lido ─────────────────────────────────────────────────
  const toggleLidoMutation = useMutation({
    mutationFn: (filename) => api.toggleLido(mangaName, filename),
    onSuccess: (res, filename) => {
      // toggleLido ainda não usa JSend 100% no backend (retorna success: true)
      // Mas nosso wrapper no api.js ou o backend pode ter mudado.
      // Se seguir o padrão JSend:
      if (res.status === 'success' || res.success) {
        queryClient.setQueryData(['chapters', mangaName, sortOrder], (old = []) =>
          old.map(c =>
            c.filename === filename ? { ...c, read: res.data?.lido ?? res.lido } : c
          )
        );
        showAlert(res.message || 'Status atualizado', 'success');
      } else {
        showAlert(res.message || 'Erro ao atualizar.', 'error');
      }
    },
    onError: (err) => showAlert(`Erro de conexão: ${err.message}`, 'error'),
  });

  async function handleDelete(filename) {
    if (!window.confirm(`Excluir o capítulo "${filename.replace('.pdf', '')}"?\n\nEsta ação não pode ser desfeita.`))
      return;
    deleteMutation.mutate(filename);
  }

  async function handleToggleLido(filename) {
    toggleLidoMutation.mutate(filename);
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
    handleToggleLido,
  };
}
