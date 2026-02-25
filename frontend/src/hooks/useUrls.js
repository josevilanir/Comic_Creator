import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService as api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function useUrls() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const userId = user?.id;
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl, setBaseUrl] = useState('');

  // ── Fetch das URLs salvas ─────────────────────────────────────────────────
  const { data: urls = {} } = useQuery({
    queryKey: ['urls', userId],
    queryFn: () => api.getUrls().then(res => res.data ?? {}),
  });

  // Sincronizar baseUrl ao selecionar manga
  useEffect(() => {
    if (selectedManga && urls[selectedManga]) {
      setBaseUrl(urls[selectedManga]);
    }
  }, [selectedManga, urls]);

  // ── Mutation: adicionar URL ───────────────────────────────────────────────
  const addMutation = useMutation({
    mutationFn: ({ nome, url }) => api.saveUrl(nome, url),
    onSuccess: (res, { nome, url }) => {
      if (res.status === 'success') {
        queryClient.setQueryData(['urls', userId], (old = {}) => ({ ...old, [nome]: url }));
      }
    },
  });

  // ── Mutation: remover URL ─────────────────────────────────────────────────
  const removeMutation = useMutation({
    mutationFn: (nome) => api.removeUrl(nome),
    onSuccess: (res, nome) => {
      if (res.status === 'success') {
        queryClient.setQueryData(['urls', userId], (old = {}) => {
          const updated = { ...old };
          delete updated[nome];
          return updated;
        });
        if (selectedManga === nome) {
          setSelectedManga('');
          setBaseUrl('');
        }
      }
    },
  });

  const addUrl = (nome, url) => addMutation.mutateAsync({ nome, url });
  const removeUrl = (nome) => removeMutation.mutateAsync(nome);

  return {
    urls,
    selectedManga,
    setSelectedManga,
    baseUrl,
    setBaseUrl,
    addUrl,
    removeUrl,
  };
}
