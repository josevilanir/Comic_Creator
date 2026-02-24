import React, { useState, useEffect, useRef } from 'react';

const API = 'http://localhost:5000';
const POLL_INTERVAL = 1500; // ms entre cada consulta de progresso

// ─── URLItem ──────────────────────────────────────────────────────────────────
function URLItem({ nome, url, onRemove }) {
  return (
    <div className="url-item">
      <div style={{ minWidth: 0 }}>
        <div className="url-item-name">{nome}</div>
        <div className="url-item-url">{url}</div>
      </div>
      <button className="btn btn-sm btn-danger" onClick={() => onRemove(nome)} style={{ flexShrink: 0 }}>
        🗑 Remover
      </button>
    </div>
  );
}

// ─── ProgressBar ──────────────────────────────────────────────────────────────
function ProgressBar({ value, total }) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div style={{ marginTop: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-500)' }}>
          Progresso
        </span>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.78rem', fontWeight: 800, color: 'var(--coral)' }}>
          {value} / {total} capítulos
        </span>
      </div>
      <div style={{
        height: '8px', borderRadius: '99px',
        background: 'var(--cream-dark)', overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', borderRadius: '99px',
          background: 'linear-gradient(90deg, var(--coral-dark), var(--coral))',
          width: `${pct}%`,
          transition: 'width 0.4s ease',
          boxShadow: pct > 0 ? '0 0 8px rgba(232,65,42,0.4)' : 'none',
        }} />
      </div>
      <div style={{ textAlign: 'right', marginTop: '4px', fontFamily: 'var(--font-display)', fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-300)' }}>
        {pct}%
      </div>
    </div>
  );
}

// ─── ResultLog ────────────────────────────────────────────────────────────────
/**
 * Lista de resultados de cada capítulo do range, exibida durante e após o download.
 */
function ResultLog({ resultados, capAtual }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [resultados.length]);

  if (resultados.length === 0 && !capAtual) return null;

  return (
    <div style={{
      marginTop: '16px',
      background: 'var(--bg)',
      border: '1.5px solid var(--card-border)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '10px 14px',
        borderBottom: '1px solid var(--card-border)',
        fontFamily: 'var(--font-display)',
        fontSize: '0.75rem', fontWeight: 800,
        color: 'var(--text-500)',
        letterSpacing: '0.07em', textTransform: 'uppercase',
      }}>
        Log de Download
      </div>
      <div style={{ maxHeight: '200px', overflowY: 'auto', padding: '8px 0' }}>
        {/* Capítulo sendo baixado agora */}
        {capAtual && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '6px 14px' }}>
            <span style={{ fontSize: '0.8rem', animation: 'spin 1s linear infinite', display: 'inline-block' }}>⏳</span>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-500)' }}>
              Baixando capítulo {capAtual}...
            </span>
          </div>
        )}
        {/* Resultados anteriores (mais recente no topo) */}
        {[...resultados].reverse().map((r, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: '10px',
            padding: '6px 14px',
            borderTop: i > 0 ? '1px solid var(--card-border)' : 'none',
          }}>
            <span style={{ fontSize: '0.85rem', flexShrink: 0, marginTop: '1px' }}>
              {r.sucesso ? '✅' : '❌'}
            </span>
            <div>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.82rem', fontWeight: 800, color: r.sucesso ? 'var(--text-900)' : 'var(--coral)' }}>
                Capítulo {r.cap}
              </span>
              <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', color: 'var(--text-300)', marginLeft: '8px' }}>
                {r.mensagem}
              </span>
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}

// ─── Downloader ───────────────────────────────────────────────────────────────
function Downloader() {
  // ── URLs salvas ────────────────────────────────────────────────────────────
  const [urls,          setUrls]          = useState({});
  const [selectedManga, setSelectedManga] = useState('');
  const [baseUrl,       setBaseUrl]       = useState('');
  const [novoNome,      setNovoNome]      = useState('');
  const [novaUrl,       setNovaUrl]       = useState('');

  // ── Capítulo único ─────────────────────────────────────────────────────────
  const [capitulo,      setCapitulo]      = useState('');
  const [loadingSingle, setLoadingSingle] = useState(false);

  // ── Range download ─────────────────────────────────────────────────────────
  const [capInicio,     setCapInicio]     = useState('');
  const [capFim,        setCapFim]        = useState('');
  const [jobId,         setJobId]         = useState(null);
  const [jobStatus,     setJobStatus]     = useState(null); // objeto com status do job
  const pollRef = useRef(null);

  // ── Alert global ──────────────────────────────────────────────────────────
  const [alert, setAlert] = useState({ message: '', type: '' });

  function showAlert(message, type = 'success') {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), 6000);
  }

  // ── Carrega URLs ───────────────────────────────────────────────────────────
  useEffect(() => {
    fetch(`${API}/api/urls`)
      .then(r => r.json())
      .then(d => setUrls(typeof d === 'object' ? d : {}))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedManga && urls[selectedManga]) setBaseUrl(urls[selectedManga]);
  }, [selectedManga, urls]);

  // ── Polling de progresso ───────────────────────────────────────────────────
  useEffect(() => {
    if (!jobId) return;

    pollRef.current = setInterval(async () => {
      try {
        const res  = await fetch(`${API}/api/download/progresso/${jobId}`);
        const data = await res.json();
        if (!data.success) return;

        setJobStatus(data);

        // Para o polling quando termina
        if (data.status === 'concluido' || data.status === 'cancelado') {
          clearInterval(pollRef.current);
          const ok  = data.resultados.filter(r => r.sucesso).length;
          const err = data.resultados.filter(r => !r.sucesso).length;
          const msg = data.status === 'cancelado'
            ? `Download cancelado. ${ok} capítulos baixados, ${err} falhou.`
            : `Download concluído! ✓ ${ok} baixados${err > 0 ? `, ✕ ${err} falharam` : ''}.`;
          showAlert(msg, err > 0 ? 'error' : 'success');
        }
      } catch (_) {}
    }, POLL_INTERVAL);

    return () => clearInterval(pollRef.current);
  }, [jobId]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  async function handleDownloadSingle(e) {
    e.preventDefault();
    if (!baseUrl || !capitulo) { showAlert('Preencha a URL base e o número do capítulo.', 'error'); return; }
    setLoadingSingle(true);
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
    finally { setLoadingSingle(false); }
  }

  async function handleDownloadRange(e) {
    e.preventDefault();
    if (!baseUrl)     { showAlert('Preencha a URL base.', 'error'); return; }
    if (!capInicio || !capFim) { showAlert('Preencha o capítulo inicial e final.', 'error'); return; }

    const ini = parseInt(capInicio);
    const fim = parseInt(capFim);

    if (ini < 1)   { showAlert('Capítulo inicial deve ser ≥ 1.', 'error'); return; }
    if (fim < ini) { showAlert('Capítulo final deve ser maior ou igual ao inicial.', 'error'); return; }
    if (fim - ini + 1 > 200) { showAlert('Máximo de 200 capítulos por download.', 'error'); return; }

    try {
      const res  = await fetch(`${API}/api/download/range`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_url:   baseUrl,
          cap_inicio: ini,
          cap_fim:    fim,
          nome_manga: selectedManga || 'Manga',
        }),
      });
      const data = await res.json();
      if (data.success) {
        setJobId(data.job_id);
        setJobStatus({ status: 'rodando', total: data.total, concluido: 0, atual: null, resultados: [] });
      } else {
        showAlert(data.message || 'Erro ao iniciar download.', 'error');
      }
    } catch (err) { showAlert(`Erro de conexão: ${err.message}`, 'error'); }
  }

  async function handleCancelar() {
    if (!jobId) return;
    try {
      await fetch(`${API}/api/download/cancelar/${jobId}`, { method: 'POST' });
      showAlert('Cancelamento solicitado...', 'error');
    } catch (_) {}
  }

  function handleNovoRange() {
    setJobId(null);
    setJobStatus(null);
    setCapInicio('');
    setCapFim('');
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
        method: 'DELETE', headers: { 'Content-Type': 'application/json' },
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

  // ── Derived state ────────────────────────────────────────────────────────
  const urlKeys     = Object.keys(urls);
  const rangeAtivo  = jobStatus && (jobStatus.status === 'rodando');
  const rangeFim    = jobStatus && (jobStatus.status === 'concluido' || jobStatus.status === 'cancelado');

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <>
      <div className="page-header">
        <div className="page-header-inner">
          <h1>⬇ <span>Downloads</span></h1>
          <p>Baixe capítulos individuais ou um range completo de uma vez.</p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '32px', paddingBottom: '64px' }}>
        {/* Alert global */}
        {alert.message && (
          <div className={`alert alert-${alert.type}`}>
            <span>{alert.type === 'success' ? '✓' : '✕'}</span>
            {alert.message}
          </div>
        )}

        {/* Seletor de manga + URL base — compartilhado */}
        <div className="form-card" style={{ marginBottom: '24px' }}>
          <div className="form-card-title">
            <div className="form-icon">🎯</div>
            Manga de Destino
          </div>
          {urlKeys.length > 0 && (
            <div className="form-group">
              <label className="form-label">Selecionar Manga Salvo</label>
              <select className="form-input" value={selectedManga} onChange={e => setSelectedManga(e.target.value)}>
                <option value="">— Selecionar —</option>
                {urlKeys.map(nome => <option key={nome} value={nome}>{nome}</option>)}
              </select>
            </div>
          )}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">URL Base</label>
            <input
              type="url" className="form-input"
              placeholder="https://site.com/manga/titulo/capitulo-"
              value={baseUrl} onChange={e => setBaseUrl(e.target.value)}
            />
          </div>
        </div>

        {/* Grid: capítulo único + range */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '24px' }}>

          {/* ── Capítulo único ── */}
          <div className="form-card">
            <div className="form-card-title">
              <div className="form-icon">📥</div>
              Capítulo Único
            </div>
            <form onSubmit={handleDownloadSingle}>
              <div className="form-group">
                <label className="form-label">Número do Capítulo</label>
                <input
                  type="number" className="form-input"
                  placeholder="Ex: 42"
                  value={capitulo} onChange={e => setCapitulo(e.target.value)}
                  min="1"
                />
              </div>
              <button type="submit" className="btn btn-coral" disabled={loadingSingle} style={{ width: '100%', justifyContent: 'center' }}>
                {loadingSingle ? '⏳ Baixando...' : '⬇ Baixar Capítulo'}
              </button>
            </form>
          </div>

          {/* ── Range de capítulos ── */}
          <div className="form-card">
            <div className="form-card-title">
              <div className="form-icon">📦</div>
              Range de Capítulos
              <span style={{
                marginLeft: 'auto', background: 'var(--coral-light)', color: 'var(--coral)',
                fontFamily: 'var(--font-display)', fontSize: '0.68rem', fontWeight: 800,
                padding: '2px 8px', borderRadius: 'var(--radius-full)',
              }}>
                Até 200 caps
              </span>
            </div>

            {/* Formulário — escondido enquanto job está rodando/concluído */}
            {!jobStatus && (
              <form onSubmit={handleDownloadRange}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Do capítulo</label>
                    <input
                      type="number" className="form-input"
                      placeholder="Ex: 1"
                      value={capInicio} onChange={e => setCapInicio(e.target.value)}
                      min="1"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Até o capítulo</label>
                    <input
                      type="number" className="form-input"
                      placeholder="Ex: 50"
                      value={capFim} onChange={e => setCapFim(e.target.value)}
                      min="1"
                    />
                  </div>
                </div>
                {capInicio && capFim && parseInt(capFim) >= parseInt(capInicio) && (
                  <div style={{
                    marginBottom: '14px', padding: '8px 12px',
                    background: 'var(--coral-light)', borderRadius: 'var(--radius-sm)',
                    fontFamily: 'var(--font-display)', fontSize: '0.78rem', fontWeight: 700, color: 'var(--coral)',
                  }}>
                    📋 {parseInt(capFim) - parseInt(capInicio) + 1} capítulos serão baixados
                  </div>
                )}
                <button type="submit" className="btn btn-coral" style={{ width: '100%', justifyContent: 'center' }}>
                  📦 Iniciar Download em Range
                </button>
              </form>
            )}

            {/* Progresso em tempo real */}
            {jobStatus && (
              <div>
                {/* Status header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.82rem', fontWeight: 800, color: 'var(--text-900)' }}>
                    {rangeAtivo  && `⏳ Baixando capítulo ${jobStatus.atual ?? '...'}...`}
                    {rangeFim && jobStatus.status === 'concluido'  && '✅ Download concluído!'}
                    {rangeFim && jobStatus.status === 'cancelado'  && '⛔ Download cancelado'}
                  </span>
                  {rangeAtivo && (
                    <button className="btn btn-sm btn-danger" onClick={handleCancelar}>
                      ⛔ Cancelar
                    </button>
                  )}
                </div>

                <ProgressBar value={jobStatus.concluido} total={jobStatus.total} />

                {/* Resumo final */}
                {rangeFim && (
                  <div style={{ display: 'flex', gap: '12px', marginTop: '14px', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, padding: '10px 14px', background: '#EDFAF4', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 900, color: '#22A05B' }}>
                        {jobStatus.resultados.filter(r => r.sucesso).length}
                      </div>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.7rem', fontWeight: 700, color: '#22A05B' }}>Baixados</div>
                    </div>
                    <div style={{ flex: 1, padding: '10px 14px', background: 'var(--coral-light)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 900, color: 'var(--coral)' }}>
                        {jobStatus.resultados.filter(r => !r.sucesso).length}
                      </div>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.7rem', fontWeight: 700, color: 'var(--coral)' }}>Falhas</div>
                    </div>
                  </div>
                )}

                {/* Log de resultados */}
                <ResultLog
                  resultados={jobStatus.resultados}
                  capAtual={rangeAtivo ? jobStatus.atual : null}
                />

                {/* Botão novo download */}
                {rangeFim && (
                  <button className="btn btn-outline" onClick={handleNovoRange} style={{ width: '100%', justifyContent: 'center', marginTop: '14px' }}>
                    ↩ Novo Download
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Salvar URL + URLs salvas ── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
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

          {urlKeys.length > 0 && (
            <div className="form-card">
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
      </div>
    </>
  );
}

export default Downloader;