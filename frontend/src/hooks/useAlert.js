import { useState, useCallback } from 'react';

/**
 * useAlert — hook reutilizável para exibir mensagens de feedback.
 * @param {number} duration - tempo em ms até o alert sumir (padrão: 5000)
 * @returns {Object} { alert, showAlert, clearAlert }
 */
export function useAlert(duration = 5000) {
  const [alert, setAlert] = useState({ message: '', type: '' });

  const showAlert = useCallback((message, type = 'success') => {
    setAlert({ message, type });
    setTimeout(() => setAlert({ message: '', type: '' }), duration);
  }, [duration]);

  const clearAlert = useCallback(() => {
    setAlert({ message: '', type: '' });
  }, []);

  return { alert, showAlert, clearAlert };
}
