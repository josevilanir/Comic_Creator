import React, { useState, useEffect } from 'react';

/**
 * URLItem - item de URL salva (componente base reutilizável)
 */
function URLItem({ name, url, onRemove }) {
  return (
    <div className="url-item">
      <div style={{ minWidth: 0 }}>
        <div className="url-item-name">{name}</div>
        <div className="url-item-url">{url}</div>
      </div>
      <button className="btn btn-danger" onClick={() => onRemove(name)}>
        Remover
      </button>
    </div>
  );
}

/**
 * Downloader - página de download de capítulos
 * Separação clara: UI → lógica local → chamadas de API
 */
function Downloader() {
  const [urls, setUrls] = useState({});
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [chapter, setChapter] = useState('1');
  const [newMangaName, setNewMangaName] = useState('');
  const [newMangaUrl, setNewMangaUrl] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);
  const [alert, setAlert] = useState({ message: '', type: '' });

  // Carrega URLs salvas
  useEffect(() => {
    fetch('http://localhost:5000/api/urls')
      .then(res => res.json())
      .then(data => {
        const parsed = data || {};
        setUrls(parsed);
        const first = Object.keys(parsed)[0];
        if (first) {
          setSelectedManga(first);
          setBaseUrl(parsed[first]);
        }
      })
      .catch(err => console.error('Erro ao carregar URLs:', err));
  }, []);

  // Atualiza URL base ao trocar manga selecionado
  useEffect(() => {
    if (selectedManga && urls[selectedManga]) {
      setBaseUrl(urls[selectedManga]);
    }
  }, [selectedManga, urls]);

  function showAlert(message, type) {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 4000);
  }

  async function handleDownload(e) {
    e.preventDefault();
    if (!baseUrl || !chapter) {
      showAlert('Preencha a URL base e o número do capítulo.', 'error');
      return;
    }
    setIsDownloading(true);
    try {
      const res = await fetch('http://localhost:5000/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_url: baseUrl,
          capitulo: chapter,
          nome_manga: selectedManga || newMangaName,
        }),
      });
      const data = await res.json();
      if (data.success) {
        showAlert(data.message, 'success');
        setChapter('1');
      } else {
        showAlert(data.message || 'Erro ao baixar.', 'error');
      }
    } catch (err) {
      showAlert(`Erro: ${err.message}`, 'error');
    } finally {
      setIsDownloading(false);
    }
  }

  async function handleSaveUrl(e) {
    e.preventDefault();
    if (!newMangaName || !newMangaUrl) {
      showAlert('Nome e URL são obrigatórios.', 'error');
      return;
    }
    try {
      const res = await fetch('http://localhost:5000/api/urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: newMangaName, url: newMangaUrl }),
      });
      const data = await res.json();
      if (data.success) {
        setUrls(prev => ({ ...prev, [newMangaName]: newMangaUrl }));
        setSelectedManga(newMangaName);
        setBaseUrl(newMangaUrl);
        setNewMangaName('');
        setNewMangaUrl('');
        showAlert('URL salva com sucesso!', 'success');
      }
    } catch (err) {
      showAlert(`Erro: ${err.message}`, 'error');
    }
  }

  async function handleRemoveUrl(name) {
    if (!window.confirm(`Remover URL de "${name}"?`)) return;
    try {
      const res = await fetch('http://localhost:5000/api/urls', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: name }),
      });
      const data = await res.json();
      if (data.success) {
        const updated = { ...urls };
        delete updated[name];
        setUrls(updated);
        const first = Object.keys(updated)[0] || '';
        setSelectedManga(first);
        setBaseUrl(updated[first] || '');
        showAlert('URL removida.', 'success');
      }
    } catch (err) {
      showAlert(`Erro: ${err.message}`, 'error');
    }
  }

  // ---- RENDER ----

  return (
    <div className="container">
      {/* Hero */}
      <div className="page-hero">
        <h1>BAIXAR <span>CAPÍTULOS</span></h1>
        <p>Selecione um mangá salvo ou insira uma URL manualmente para baixar capítulos.</p>
      </div>

      {/* Alert */}
      {alert.message && (
        <div className={`alert alert-${alert.type}`}>
          <span>{alert.type === 'success' ? '✓' : '✕'}</span>
          {alert.message}
        </div>
      )}

      {/* Form de download */}
      <div className="form-card">
        <h2>Baixar Capítulo</h2>
        <form onSubmit={handleDownload}>
          {/* Selecionar manga */}
          {Object.keys(urls).length > 0 && (
            <div className="form-group">
              <label className="form-label">Selecione o Mangá</label>
              <select
                className="form-input"
                value={selectedManga}
                onChange={e => setSelectedManga(e.target.value)}
              >
                <option value="">— URL manual —</option>
                {Object.keys(urls).map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>
          )}

          {/* URL base */}
          <div className="form-group">
            <label className="form-label">URL Base</label>
            <input
              type="text"
              className="form-input"
              value={baseUrl}
              onChange={e => setBaseUrl(e.target.value)}
              placeholder="https://..."
            />
          </div>

          {/* Número do capítulo */}
          <div className="form-group">
            <label className="form-label">Número do Capítulo</label>
            <input
              type="number"
              className="form-input"
              value={chapter}
              onChange={e => setChapter(e.target.value)}
              min="1"
              style={{ maxWidth: '180px' }}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isDownloading}
            style={{ opacity: isDownloading ? 0.6 : 1 }}
          >
            {isDownloading ? '⏳ Baixando...' : '⬇ Baixar Capítulo'}
          </button>
        </form>
      </div>

      {/* Form de salvar URL */}
      <div className="form-card">
        <h2>Salvar URL de Mangá</h2>
        <form onSubmit={handleSaveUrl}>
          <div className="form-group">
            <label className="form-label">Nome do Mangá</label>
            <input
              type="text"
              className="form-input"
              value={newMangaName}
              onChange={e => setNewMangaName(e.target.value)}
              placeholder="Ex: Dandadan"
            />
          </div>
          <div className="form-group">
            <label className="form-label">URL Base</label>
            <input
              type="text"
              className="form-input"
              value={newMangaUrl}
              onChange={e => setNewMangaUrl(e.target.value)}
              placeholder="https://..."
            />
          </div>
          <button type="submit" className="btn btn-ghost">
            + Salvar URL
          </button>
        </form>
      </div>

      {/* URLs salvas */}
      {Object.keys(urls).length > 0 && (
        <div className="form-card">
          <h2>URLs Salvas</h2>
          {Object.entries(urls).map(([name, url]) => (
            <URLItem key={name} name={name} url={url} onRemove={handleRemoveUrl} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Downloader;