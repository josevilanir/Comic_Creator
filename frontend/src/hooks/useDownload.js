import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

export function useDownload(showAlert) {
  const [capitulo, setCapitulo] = useState('');
  const [loadingSingle, setLoadingSingle] = useState(false);

  const [capInicio, setCapInicio] = useState('');
  const [capFim, setCapFim] = useState('');
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const pollRef = useRef(null);

  const rangeAtivo = jobStatus && jobStatus.status === 'rodando';
  const rangeFim =
    jobStatus && (jobStatus.status === 'concluido' || jobStatus.status === 'cancelado');

  useEffect(() => {
    if (!jobId) return;

    pollRef.current = setInterval(async () => {
      try {
        const data = await api.getProgress(jobId);
        if (data.status !== 'success') return;

        setJobStatus(data.data);

        const status = data.data.status;
        if (status === 'concluido' || status === 'cancelado') {
          clearInterval(pollRef.current);
          const ok = data.data.resultados.filter(r => r.sucesso).length;
          const err = data.data.resultados.filter(r => !r.sucesso).length;
          const msg =
            status === 'cancelado'
              ? `Download cancelado. ${ok} capítulos baixados, ${err} falhou.`
              : `Download concluído! ✓ ${ok} baixados${err > 0 ? `, ✕ ${err} falharam` : ''}.`;
          showAlert && showAlert(msg, err > 0 ? 'error' : 'success');
        }
      } catch (_) {}
    }, 1500);

    return () => clearInterval(pollRef.current);
  }, [jobId, showAlert]);

  const handleDownloadSingle = async (baseUrl, cap, nome) => {
    if (!baseUrl || !cap) {
      showAlert && showAlert('Preencha a URL base e o número do capítulo.', 'error');
      return;
    }
    setLoadingSingle(true);
    try {
      const data = await api.downloadSingle({
        base_url: baseUrl,
        capitulo: parseInt(cap, 10),
        nome_manga: nome || 'Manga',
      });
      if (data.status === 'success') {
        showAlert && showAlert(data.data?.message || 'Capítulo baixado!');
        setCapitulo('');
      } else {
        showAlert && showAlert(data.message || 'Erro no download.', 'error');
      }
    } catch (err) {
      showAlert && showAlert(`Erro de conexão: ${err.message}`, 'error');
    } finally {
      setLoadingSingle(false);
    }
  };

  const handleDownloadRange = async (baseUrl, ini, fim, nome) => {
    if (!baseUrl) {
      showAlert && showAlert('Preencha a URL base.', 'error');
      return;
    }
    if (!ini || !fim) {
      showAlert && showAlert('Preencha o capítulo inicial e final.', 'error');
      return;
    }

    const i = parseInt(ini, 10);
    const f = parseInt(fim, 10);

    if (i < 1) {
      showAlert && showAlert('Capítulo inicial deve ser ≥ 1.', 'error');
      return;
    }
    if (f < i) {
      showAlert && showAlert('Capítulo final deve maior ou igual ao inicial.', 'error');
      return;
    }
    if (f - i + 1 > 200) {
      showAlert && showAlert('Máximo de 200 capítulos por download.', 'error');
      return;
    }

    try {
      const data = await api.downloadRange({
        base_url: baseUrl,
        cap_inicio: i,
        cap_fim: f,
        nome_manga: nome || 'Manga',
      });
      if (data.status === 'success') {
        setJobId(data.data.job_id);
        setJobStatus({ status: 'rodando', total: data.data.total, concluido: 0, atual: null, resultados: [] });
      } else {
        showAlert && showAlert(data.message || 'Erro ao iniciar download.', 'error');
      }
    } catch (err) {
      showAlert && showAlert(`Erro de conexão: ${err.message}`, 'error');
    }
  };

  const handleCancelar = async () => {
    if (!jobId) return;
    try {
      await api.cancelDownload(jobId);
      showAlert && showAlert('Cancelamento solicitado...', 'error');
    } catch (_) {}
  };

  const handleNovoRange = () => {
    setJobId(null);
    setJobStatus(null);
    setCapInicio('');
    setCapFim('');
  };

  return {
    capitulo,
    setCapitulo,
    loadingSingle,
    capInicio,
    setCapInicio,
    capFim,
    setCapFim,
    jobStatus,
    rangeAtivo,
    rangeFim,
    handleDownloadSingle,
    handleDownloadRange,
    handleCancelar,
    handleNovoRange,
  };
}
