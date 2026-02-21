import React, { useState, useEffect } from 'react';

const API = 'http://localhost:5000';

// ─── URLItem ──────────────────────────────────────────────────────────────────
function URLItem({ nome, url, onRemove }) {
  return (
    <div className="url-item">
      <div style={{ minWidth: 0 }}>
        <div className="url-item-name">{nome}</div>
        <div className="url-item-url">{url}</div>
      </div>
      <button
        className="btn btn-sm btn-danger"
        onClick={() => onRemove(nome)}
        style={{ flexShrink: 0 }}
      >
        🗑 Remover
      </button>
    </div>
  );
}

// ─── Downloader ───────────────────────────────────────────────────────────────
function Downloader() {
  const [urls,          setUrls]          = useState({});
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl,       setBaseUrl]       = useState('');
  const [capitulo,      setCapitulo]      = useState('');
  const [loading,       setLoading]       = useState(false);
  const [novoNome,      setNovoNome]      = useState('');
  const [novaUrl,       setNovaUrl]       = useState('');
  const [alert,         setAlert]         = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 5000);
  }

  useEffect(() => {
    fetch(`${API}/api/urls`)
      .then(res => res.json())
      .then(data => setUrls(typeof data === 'object' ? data : {}))
      .catch(err => console.error('Erro ao carregar URLs:', err));
  }, []);

  useEffect(() => {
    if (selectedManga && urls[selectedManga]) setBaseUrl(urls[selectedManga]);
  }, [selectedManga, urls]);

  async function handleDownload(e) {
    e.preventDefault();
    if (!baseUrl || !capitulo) { showAlert('Preencha a URL base e o número do capítulo.', 'error'); return; }
    setLoading(true);
    try {
      const res  = await fetch(`${API}/api/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: baseUrl, capitulo: parseInt(capitulo), nome_manga: selectedManga || 'Manga' }),
      });
      const data = await res.json();
      if (data.success) { showAlert(data.message || 'Capítulo baixado!'); setCapitulo(''); }
      else showAlert(data.message || 'Erro no download.', 'error');
    } catch (err) { showAlert(`Erro de conexão: ${err.message}`, 'error'); }
    finally { setLoading(false); }
  }

  async function handleAddUrl(e) {
    e.preventDefault();
    if (!novoNome || !novaUrl) { showAlert('Preencha o nome e a URL.', 'error'); return; }
    try {
      const res  = await fetch(`${API}/api/urls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: novoNome, url: novaUrl }),
      });
      const data = await res.json();
      if (data.success) { setUrls(prev => ({ ...prev, [novoNome]: novaUrl })); setNovoNome(''); setNovaUrl(''); showAlert(`URL de "${novoNome}" salva!`); }
      else showAlert(data.message || 'Erro ao salvar.', 'error');
    } catch (err) { showAlert(`Erro: ${err.message}`, 'error'); }
  }

  async function handleRemoveUrl(nome) {
    if (!window.confirm(`Remover a URL de "${nome}"?`)) return;
    try {
      const res  = await fetch(`${API}/api/urls`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });
      const data = await res.json();
      if (data.success) {
        setUrls(prev => { const n = { ...prev }; delete n[nome]; return n; });
        if (selectedManga === nome) { setSelectedManga(''); setBaseUrl(''); }
        showAlert(`URL de "${nome}" removida.`);
      } else showAlert(data.message || 'Erro ao remover.', 'error');
    } catch (err) { showAlert(`Erro: ${err.message}`, 'error'); }
  }

  const urlKeys = Object.keys(urls);

  return (
    <>
      <div className="page-header">
        <div className="page-header-inner">
          <h1>⬇ <span>Downloads</span></h1>
          <p>Baixe capítulos de mangás e salve URLs para uso rápido.</p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '32px', paddingBottom: '64px' }}>
        {alert.message && (
          <div className={`alert alert-${alert.type}`}>
            <span>{alert.type === 'success' ? '✓' : '✕'}</span>
            {alert.message}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>

          {/* Baixar Capítulo */}
          <div className="form-card">
            <div className="form-card-title">
              <div className="form-icon">📥</div>
              Baixar Capítulo
            </div>
            <form onSubmit={handleDownload}>
              {urlKeys.length > 0 && (
                <div className="form-group">
                  <label className="form-label">Manga Salvo</label>
                  <select className="form-input" value={selectedManga} onChange={e => setSelectedManga(e.target.value)}>
                    <option value="">— Selecionar —</option>
                    {urlKeys.map(nome => <option key={nome} value={nome}>{nome}</option>)}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label className="form-label">URL Base</label>
                <input type="url" className="form-input" placeholder="https://site.com/manga/titulo/capitulo-" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Número do Capítulo</label>
                <input type="number" className="form-input" placeholder="Ex: 42" value={capitulo} onChange={e => setCapitulo(e.target.value)} min="1" />
              </div>
              <button type="submit" className="btn btn-coral" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
                {loading ? '⏳ Baixando...' : '⬇ Baixar Capítulo'}
              </button>
            </form>
          </div>

          {/* Salvar URL */}
          <div className="form-card">
            <div className="form-card-title">
              <div className="form-icon">🔗</div>
              Salvar URL
            </div>
            <form onSubmit={handleAddUrl}>
              <div className="form-group">
                <label className="form-label">Nome do Mangá</label>
                <input type="text" className="form-input" placeholder="Ex: Dandadan" value={novoNome} onChange={e => setNovoNome(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">URL Base</label>
                <input type="url" className="form-input" placeholder="https://..." value={novaUrl} onChange={e => setNovaUrl(e.target.value)} />
              </div>
              <button type="submit" className="btn btn-outline" style={{ width: '100%', justifyContent: 'center' }}>
                💾 Salvar URL
              </button>
            </form>
          </div>
        </div>

        {/* URLs Salvas */}
        {urlKeys.length > 0 && (
          <div className="form-card" style={{ marginTop: '24px' }}>
            <div className="form-card-title">
              <div className="form-icon">📋</div>
              URLs Salvas
              <span style={{ marginLeft: 'auto', background: 'var(--coral-light)', color: 'var(--coral)', fontFamily: 'var(--font-display)', fontSize: '0.75rem', fontWeight: 800, padding: '3px 10px', borderRadius: 'var(--radius-full)' }}>
                {urlKeys.length}
              </span>
            </div>
            {urlKeys.map(nome => (
              <URLItem key={nome} nome={nome} url={urls[nome]} onRemove={handleRemoveUrl} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}

export default Downloader;