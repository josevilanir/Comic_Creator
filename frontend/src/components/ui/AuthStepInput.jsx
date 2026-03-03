import React, { useState } from 'react';
import { ArrowRight, Eye, EyeOff } from 'lucide-react';
import { cn } from '../../utils/cn';

export function AuthStepInput({
  icon,
  label,
  placeholder,
  type = 'text',
  value,
  onChange,
  isValid,
  onAdvance,
  showToggle = false,
  inputRef,
}) {
  const [revealed, setRevealed] = useState(false);
  const inputType = showToggle ? (revealed ? 'text' : 'password') : type;

  function handleKeyDown(e) {
    if (e.key === 'Enter' && isValid) {
      onAdvance?.();
    }
  }

  return (
    <div className="glass-input-wrap">
      {/* Floating label */}
      <span
        className={cn('glass-input__label', value.length > 0 && 'glass-input__label--visible')}
      >
        {label}
      </span>

      <div className="glass-input__row">
        {/* Leading icon */}
        {icon && <span className="glass-input__icon">{icon}</span>}

        <input
          ref={inputRef}
          type={inputType}
          className="glass-input"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          autoComplete={
            type === 'password' ? 'current-password' : type === 'email' ? 'email' : 'username'
          }
        />

        {/* Toggle visibility for password fields */}
        {showToggle && (
          <button
            type="button"
            className="glass-input__toggle"
            onClick={() => setRevealed((v) => !v)}
            tabIndex={-1}
            aria-label={revealed ? 'Ocultar senha' : 'Mostrar senha'}
          >
            {revealed ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}

        {/* Advance arrow */}
        {isValid && (
          <button
            type="button"
            className="glass-input__advance"
            onClick={onAdvance}
            aria-label="Avançar"
          >
            <ArrowRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
