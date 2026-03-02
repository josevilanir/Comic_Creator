import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import SkeletonCard from '../components/shared/SkeletonCard';

describe('SkeletonCard', () => {
  it('renderiza sem erros', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.firstChild).not.toBeNull();
  });

  it('contém os elementos skeleton (thumb e lines)', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('.skeleton-thumb')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-line')).toBeInTheDocument();
  });
});
