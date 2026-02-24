import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function useUrls() {
  const [urls, setUrls] = useState({});
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl, setBaseUrl] = useState('');

  useEffect(() => {
    api.getUrls()
      .then(d => setUrls(typeof d === 'object' ? d : {}))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedManga && urls[selectedManga]) {
      setBaseUrl(urls[selectedManga]);
    }
  }, [selectedManga, urls]);

  const addUrl = async (nome, url) => {
    const data = await api.saveUrl(nome, url);
    if (data.success) {
      setUrls(prev => ({ ...prev, [nome]: url }));
    }
    return data;
  };

  const removeUrl = async (nome) => {
    const data = await api.removeUrl(nome);
    if (data.success) {
      setUrls(prev => {
        const n = { ...prev };
        delete n[nome];
        return n;
      });
      if (selectedManga === nome) {
        setSelectedManga('');
        setBaseUrl('');
      }
    }
    return data;
  };

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
