/**
 * useProgresso — gerencia salvamento e carregamento do progresso de leitura.
 * Salva a cada virada de página com debounce de 800ms para não spammar a API.
 */
import { useCallback, useRef } from 'react';
import { api } from '../services/api';

export function useProgresso(mangaName, filename) {
  const debounceRef = useRef(null);

  /**
   * Carrega a última página salva para o capítulo.
   * Retorna 1 se não houver progresso salvo.
   */
  const loadProgresso = useCallback(async () => {
    try {
      const res = await api.getProgresso(mangaName, filename);
      if (res.status === 'success') {
        return res.data.pagina ?? 1;
      }
    } catch (err) {
      console.warn('Erro ao carregar progresso:', err);
    }
    return 1;
  }, [mangaName, filename]);

  /**
   * Salva a página atual com debounce de 800ms.
   * Evita chamadas desnecessárias ao virar páginas rápido.
   */
  const saveProgresso = useCallback((pagina) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        await api.saveProgresso(mangaName, filename, pagina);
      } catch (err) {
        console.warn('Erro ao salvar progresso:', err);
      }
    }, 800);
  }, [mangaName, filename]);

  return { loadProgresso, saveProgresso };
}
