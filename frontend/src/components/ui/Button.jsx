import React from 'react';

/**
 * Botão base reutilizável, aceita classes adicionais.
 */
function Button({ children, className = '', ...props }) {
  return (
    <button className={`btn ${className}`} {...props}>
      {children}
    </button>
  );
}

export default Button;
