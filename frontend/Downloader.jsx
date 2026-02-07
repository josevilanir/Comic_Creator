import React, { useState, useEffect } from 'react';

function Downloader() {
  const [urls, setUrls] = useState({});
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [capitulo, setCapitulo] = useState('1');
  const [novoMangaNome, setNovoMangaNome] = useState('');
  const [novaUrl, setNovaUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  // Carregar URLs salvas ao montar
  useEffect(() => {
    fetch('http://localhost:5000/api/urls')
      .then(res => res.json())
      .then(data => {
        setUrls(data || {});
        if (Object.keys(data).length > 0) {
          const firstKey = Object.keys(data)[0];
          setSelectedManga(firstKey);
          setBaseUrl(data[firstKey]);
        }
      })
      .catch(err => console.error('Erro ao carregar URLs:', err));
  }, []);

  // Atualizar base URL quando manga selecionado muda
  useEffect(() => {
    if (selectedManga && urls[selectedManga]) {
      setBaseUrl(urls[selectedManga]);
    }
  }, [selectedManga, urls]);

  const handleDownload = async (e) => {
    e.preventDefault();
    if (!baseUrl || !capitulo) {
      setMessage('Por favor preencha a URL e o número do capítulo.');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:5000/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_url: baseUrl,
          capitulo: capitulo,
          nome_manga: selectedManga || novoMangaNome,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setMessage(data.message);
        setMessageType('success');
        setCapitulo('1');
      } else {
        setMessage(data.message || 'Erro ao baixar.');
        setMessageType('error');
      }
    } catch (err) {
      setMessage(`Erro: ${err.message}`);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUrl = async (e) => {
    e.preventDefault();
    if (!novoMangaNome || !novaUrl) {
      setMessage('Nome e URL são obrigatórios.');
      setMessageType('error');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: novoMangaNome,
          url: novaUrl,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setUrls({ ...urls, [novoMangaNome]: novaUrl });
        setSelectedManga(novoMangaNome);
        setBaseUrl(novaUrl);
        setNovoMangaNome('');
        setNovaUrl('');
        setMessage('URL salva com sucesso!');
        setMessageType('success');
      }
    } catch (err) {
      setMessage(`Erro: ${err.message}`);
      setMessageType('error');
    }
  };

  const handleRemoveUrl = async (nome) => {
    if (!window.confirm(`Remover URL de "${nome}"?`)) return;

    try {
      const response = await fetch('http://localhost:5000/api/urls', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });

      const data = await response.json();
      if (data.success) {
        const newUrls = { ...urls };
        delete newUrls[nome];
        setUrls(newUrls);
        if (selectedManga === nome) {
          const firstKey = Object.keys(newUrls)[0] || '';
          setSelectedManga(firstKey);
          setBaseUrl(newUrls[firstKey] || '');
        }
        setMessage('URL removida com sucesso!');
        setMessageType('success');
      }
    } catch (err) {
      setMessage(`Erro: ${err.message}`);
      setMessageType('error');
    }
  };

  return (
    <div className="container">
      <h2>Início - Baixar Mangas</h2>

      {message && (
        <div
          style={{
            padding: '10px 15px',
            marginBottom: '20px',
            borderRadius: '4px',
            backgroundColor: messageType === 'success' ? '#27ae60' : '#c0392b',
            color: 'white',
          }}
        >
          {message}
        </div>
      )}

      <form onSubmit={handleDownload} style={{ marginBottom: '40px' }}>
        <h3>Baixar Capítulo</h3>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Selecione o Mangá:
            <select
              value={selectedManga}
              onChange={e => setSelectedManga(e.target.value)}
              style={{
                display: 'block',
                width: '100%',
                padding: '8px',
                marginTop: '5px',
                backgroundColor: '#333',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
              }}
            >
              <option value="">-- Selecione ou use URL manual --</option>
              {Object.keys(urls).map(nome => (
                <option key={nome} value={nome}>
                  {nome}
                </option>
              ))}
            </select>
          </label>
        </div>

        {selectedManga && (
          <div style={{ marginBottom: '15px' }}>
            <label>
              URL Base:
              <input
                type="text"
                value={baseUrl}
                onChange={e => setBaseUrl(e.target.value)}
                placeholder="https://..."
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '8px',
                  marginTop: '5px',
                  backgroundColor: '#333',
                  color: '#fff',
                  border: '1px solid #555',
                  borderRadius: '4px',
                  boxSizing: 'border-box',
                }}
              />
            </label>
          </div>
        )}

        <div style={{ marginBottom: '15px' }}>
          <label>
            Número do Capítulo:
            <input
              type="number"
              value={capitulo}
              onChange={e => setCapitulo(e.target.value)}
              min="1"
              style={{
                display: 'block',
                width: '100%',
                padding: '8px',
                marginTop: '5px',
                backgroundColor: '#333',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
                boxSizing: 'border-box',
              }}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? 'Baixando...' : 'Baixar Capítulo'}
        </button>
      </form>

      <form onSubmit={handleAddUrl} style={{ marginBottom: '40px', paddingTop: '20px', borderTop: '1px solid #333' }}>
        <h3>Adicionar URL</h3>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Nome do Mangá:
            <input
              type="text"
              value={novoMangaNome}
              onChange={e => setNovoMangaNome(e.target.value)}
              placeholder="Ex: Dandadan"
              style={{
                display: 'block',
                width: '100%',
                padding: '8px',
                marginTop: '5px',
                backgroundColor: '#333',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
                boxSizing: 'border-box',
              }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            URL Base:
            <input
              type="text"
              value={novaUrl}
              onChange={e => setNovaUrl(e.target.value)}
              placeholder="https://..."
              style={{
                display: 'block',
                width: '100%',
                padding: '8px',
                marginTop: '5px',
                backgroundColor: '#333',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
                boxSizing: 'border-box',
              }}
            />
          </label>
        </div>

        <button
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#2ecc71',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Adicionar
        </button>
      </form>

      {Object.keys(urls).length > 0 && (
        <div style={{ paddingTop: '20px', borderTop: '1px solid #333' }}>
          <h3>URLs Salvas</h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            {Object.entries(urls).map(([nome, url]) => (
              <div
                key={nome}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 15px',
                  backgroundColor: '#2a2a2a',
                  borderRadius: '4px',
                }}
              >
                <div>
                  <strong>{nome}</strong>
                  <div style={{ fontSize: '0.9em', color: '#999', marginTop: '5px', wordBreak: 'break-all' }}>
                    {url}
                  </div>
                </div>
                <button
                  onClick={() => handleRemoveUrl(nome)}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                  }}
                >
                  Remover
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Downloader;
