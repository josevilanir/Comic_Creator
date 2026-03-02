import React from 'react';

/**
 * SkeletonCard — placeholder de carregamento para o grid da biblioteca.
 */
function SkeletonCard() {
  return (
    <div className="skeleton-card bento-layout-card">
      <div className="skeleton-thumb" />
      <div className="skeleton-body">
        <div className="skeleton-line" />
        <div className="skeleton-line short" />
      </div>
    </div>
  );
}

export default SkeletonCard;
