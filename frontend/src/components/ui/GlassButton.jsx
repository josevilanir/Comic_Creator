import React from 'react';
import { cn } from '../../utils/cn';

const sizeWrapClasses = {
  default: 'glass-button-wrap',
  sm:      'glass-button-wrap glass-button-wrap--sm',
  lg:      'glass-button-wrap glass-button-wrap--lg',
  icon:    'glass-button-wrap glass-button-wrap--icon',
};

const sizeInnerClasses = {
  default: 'glass-button__content px-6 py-3 text-base font-medium',
  sm:      'glass-button__content px-4 py-2 text-sm font-medium',
  lg:      'glass-button__content px-8 py-4 text-lg font-medium',
  icon:    'glass-button__content flex h-10 w-10 items-center justify-center',
};

export function GlassButton({
  size = 'default',
  onClick,
  type = 'button',
  children,
  className,
  contentClassName,
  disabled,
}) {
  return (
    <div className={cn(sizeWrapClasses[size] ?? sizeWrapClasses.default, className)}>
      <button
        type={type}
        onClick={onClick}
        disabled={disabled}
        className={cn('glass-button', sizeInnerClasses[size] ?? sizeInnerClasses.default, contentClassName)}
      >
        {children}
      </button>
    </div>
  );
}
