import React from 'react';

/**
 * Componente de alerta base usado em várias telas.
 * Exibe ícone e mensagem dependendo do tipo (success/error).
 */
function Alert({ type = 'success', message = '' }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${type}`}> 
      <span>{type === 'success' ? '✓' : '✕'}</span> {message}
    </div>
  );
}

export default Alert;
