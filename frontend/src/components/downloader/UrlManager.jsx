import React, { useState } from 'react';

/**
 * UrlManager — seção responsável por seleção/adição/remoção de URLs salvas.
 * Recebe o hook useUrls via props e um showAlert para mensagens.
 */
function UrlManager({
  urls,
  selectedManga,
  baseUrl,
  setSelectedManga,
  setBaseUrl,
  addUrl,
  removeUrl,
  showAlert,
}) {
  const [novoNome, setNovoNome] = useState('');
  const [novaUrl, setNovaUrl] = useState('');

  const urlKeys = Object.keys(urls);

  function handleAdd(e) {
    e.preventDefault();
    if (!novoNome || !novaUrl) {
      showAlert('Preencha o nome e a URL.', 'error');
      return;
    }

    addUrl(novoNome, novaUrl).then(data => {
      if (data.status === 'success') {
        showAlert(`URL de "${novoNome}" salva!`);
        setNovoNome('');
        setNovaUrl('');
      } else {
        showAlert(data.message || 'Erro ao salvar.', 'error');
      }
    }).catch(err => {
      showAlert(`Erro: ${err.message}`, 'error');
    });
  }

  function handleRemove(nome) {
    if (!window.confirm(`Remover a URL de "${nome}"?`)) return;
    removeUrl(nome).then(data => {
      if (data.status === 'success') {
        showAlert(`URL de "${nome}" removida.`);
      } else {
        showAlert(data.message || 'Erro ao remover.', 'error');
      }
    }).catch(err => {
      showAlert(`Erro: ${err.message}`, 'error');
    });
  }

  return (
    <>
      {/* Seletor de manga + URL base */}
      <div className="form-card" style={{ marginBottom: '24px' }}>
        <div className="form-card-title">
          <div className="form-icon">🎯</div>
          Manga de Destino
        </div>
        {urlKeys.length > 0 && (
          <div className="form-group">
            <label className="form-label">Selecionar Manga Salvo</label>
            <select
              className="form-input"
              value={selectedManga}
              onChange={e => setSelectedManga(e.target.value)}
            >
              <option value="">— Selecionar —</option>
              {urlKeys.map(nome => <option key={nome} value={nome}>{nome}</option>)}
            </select>
          </div>
        )}
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">URL Base</label>
          <input
            type="url"
            className="form-input"
            placeholder="https://site.com/manga/titulo/capitulo-"
            value={baseUrl}
            onChange={e => setBaseUrl(e.target.value)}
          />
        </div>
      </div>

      {/* área de salvar URL e lista */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="form-card">
          <div className="form-card-title">
            <div className="form-icon">🔗</div>
            Salvar URL
          </div>
          <form onSubmit={handleAdd}>
            <div className="form-group">
              <label className="form-label">Nome do Mangá</label>
              <input
                type="text"
                className="form-input"
                placeholder="Ex: Dandadan"
                value={novoNome}
                onChange={e => setNovoNome(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">URL Base</label>
              <input
                type="url"
                className="form-input"
                placeholder="https://..."
                value={novaUrl}
                onChange={e => setNovaUrl(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="btn btn-outline"
              style={{ width: '100%', justifyContent: 'center' }}
            >
              💾 Salvar URL
            </button>
          </form>
        </div>

        {urlKeys.length > 0 && (
          <div className="form-card">
            <div className="form-card-title">
              <div className="form-icon">📋</div>
              URLs Salvas
              <span
                style={{
                  marginLeft: 'auto',
                  background: 'var(--coral-light)',
                  color: 'var(--coral)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-full)',
                }}
              >
                {urlKeys.length}
              </span>
            </div>
            {urlKeys.map(nome => (
              <div key={nome} className="flex flex-col gap-3 bg-gray-50 rounded-2xl p-4 border border-gray-100 mb-2">
                <div className="min-w-0">
                  <p className="font-bold text-gray-800 text-sm">{nome}</p>
                  <p className="text-xs text-gray-400 truncate mt-1">{urls[nome]}</p>
                </div>
                <button
                  className="w-full py-3 rounded-full border border-red-300 text-red-500 text-sm font-bold hover:bg-red-50 transition-colors"
                  onClick={() => handleRemove(nome)}
                >
                  🗑 Remover
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

export default UrlManager;
