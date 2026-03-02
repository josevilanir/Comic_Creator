import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EmptyState from '../components/shared/EmptyState';

describe('EmptyState', () => {
  it('exibe mensagem de biblioteca vazia quando não há busca', () => {
    render(<EmptyState search="" />);
    expect(screen.getByText(/biblioteca vazia/i)).toBeInTheDocument();
    expect(screen.getByText(/downloads/i)).toBeInTheDocument();
  });

  it('exibe mensagem de "nada encontrado" quando há busca ativa', () => {
    render(<EmptyState search="Dandadan" />);
    expect(screen.getByText(/nada encontrado/i)).toBeInTheDocument();
    expect(screen.getByText(/dandadan/i)).toBeInTheDocument();
  });

  it('não exibe "nada encontrado" quando não há busca', () => {
    render(<EmptyState search="" />);
    expect(screen.queryByText(/nada encontrado/i)).not.toBeInTheDocument();
  });

  it('não exibe "biblioteca vazia" quando há busca ativa', () => {
    render(<EmptyState search="One Piece" />);
    expect(screen.queryByText(/biblioteca vazia/i)).not.toBeInTheDocument();
  });
});
