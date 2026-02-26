import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAlert } from './useAlert';
import { apiService as api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ITEMS_PER_PAGE = 18;

export function useLibrary() {
  const { alert, showAlert } = useAlert(4000);
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const userId = user?.id;

  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // ── Fetch da biblioteca ───────────────────────────────────────────────────
  const { data: libraryData = { mangas: [], pagination: {} }, isLoading: loading } = useQuery({
    queryKey: ['library', userId],
    queryFn: () => api.getLibrary().then(res => res.data ?? { mangas: [], pagination: {} }),
  });

  const mangas = libraryData.mangas || [];

  // Resetar página ao mudar busca
  const handleSearchChange = (value) => {
    setSearch(value);
    setCurrentPage(1);
  };

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

  // ── Mutation: excluir mangá ───────────────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: (nomeManga) => api.deleteManga(nomeManga),
    onSuccess: (res, nomeManga) => {
      if (res.status === 'success') {
        // Atualiza cache sem refetch
        queryClient.setQueryData(['library', userId], (old) => {
          if (!old) return old;
          return {
            ...old,
            mangas: old.mangas.filter(m => m.nome !== nomeManga)
          };
        });
        showAlert(`"${nomeManga}" excluído com sucesso.`);
      } else {
        showAlert(res.data?.message || 'Erro ao excluir.', 'error');
      }
    },
    onError: (err) => showAlert(`Erro de conexão: ${err.message}`, 'error'),
  });

  // ── Mutation: upload de capa ──────────────────────────────────────────────
  const uploadCapaMutation = useMutation({
    mutationFn: ({ nomeManga, formData }) => api.uploadCover(nomeManga, formData),
    onSuccess: (res, { nomeManga }) => {
      if (res.status === 'success') {
        // Atualiza a capa no cache sem refetch
        queryClient.setQueryData(['library', userId], (old) => {
          if (!old) return old;
          return {
            ...old,
            mangas: old.mangas.map(m =>
              m.nome === nomeManga
                ? { ...m, tem_capa: true, capa_url: res.data?.capa_url ?? m.capa_url }
                : m
            )
          };
        });
        showAlert(`Capa de "${nomeManga}" atualizada!`);
        return res.data?.capa_url;
      } else {
        showAlert(res.data?.message || 'Erro ao enviar capa.', 'error');
      }
    },
    onError: (err) => showAlert(`Erro de conexão: ${err.message}`, 'error'),
  });

  async function handleDelete(nomeManga) {
    deleteMutation.mutate(nomeManga);
  }

  async function handleUploadCapa(nomeManga, file) {
    const formData = new FormData();
    formData.append('capa', file);
    uploadCapaMutation.mutate({ nomeManga, formData });
  }

  return {
    alert,
    loading,
    search,
    setSearch: handleSearchChange,
    filtered,
    paginated,
    currentPage,
    totalPages,
    handlePageChange,
    handleDelete,
    handleUploadCapa,
  };
}
