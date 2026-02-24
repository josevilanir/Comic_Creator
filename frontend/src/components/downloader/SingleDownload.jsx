import React from 'react';
import Button from '../ui/Button';

/**
 * Formulário para baixar um capítulo único.
 */
function SingleDownload({
  capitulo,
  setCapitulo,
  loadingSingle,
  onDownload,
}) {
  return (
    <div className="form-card">
      <div className="form-card-title">
        <div className="form-icon">📥</div>
        Capítulo Único
      </div>
      <form
        onSubmit={e => {
          e.preventDefault();
          onDownload();
        }}
      >
        <div className="form-group">
          <label className="form-label">Número do Capítulo</label>
          <input
            type="number"
            className="form-input"
            placeholder="Ex: 42"
            value={capitulo}
            onChange={e => setCapitulo(e.target.value)}
            min="1"
          />
        </div>
        <Button
          type="submit"
          className="btn-coral"
          disabled={loadingSingle}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {loadingSingle ? '⏳ Baixando...' : '⬇ Baixar Capítulo'}
        </Button>
      </form>
    </div>
  );
}

export default SingleDownload;
