import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import LibraryToolbar from '../components/library/LibraryToolbar';

describe('LibraryToolbar', () => {
  const defaultProps = {
    search: '',
    setSearch: vi.fn(),
    filteredCount: 12,
    currentPage: 1,
    totalPages: 1,
  };

  it('renderiza o campo de busca', () => {
    render(<LibraryToolbar {...defaultProps} />);
    expect(screen.getByPlaceholderText(/buscar mangá/i)).toBeInTheDocument();
  });

  it('exibe a contagem de títulos corretamente', () => {
    render(<LibraryToolbar {...defaultProps} />);
    expect(screen.getByText(/12/)).toBeInTheDocument();
    expect(screen.getByText(/títulos/i)).toBeInTheDocument();
  });

  it('usa singular "título" quando há 1 resultado', () => {
    render(<LibraryToolbar {...defaultProps} filteredCount={1} />);
    expect(screen.getByText(/1/)).toBeInTheDocument();
    expect(screen.getByText(/título/i)).toBeInTheDocument();
  });

  it('exibe info de paginação quando totalPages > 1', () => {
    render(<LibraryToolbar {...defaultProps} totalPages={3} currentPage={2} />);
    expect(screen.getByText(/página 2 de 3/i)).toBeInTheDocument();
  });

  it('não exibe info de paginação quando totalPages === 1', () => {
    render(<LibraryToolbar {...defaultProps} totalPages={1} />);
    expect(screen.queryByText(/página/i)).not.toBeInTheDocument();
  });

  it('chama setSearch ao digitar', async () => {
    const setSearch = vi.fn();
    render(<LibraryToolbar {...defaultProps} setSearch={setSearch} />);
    await userEvent.type(screen.getByPlaceholderText(/buscar mangá/i), 'X');
    expect(setSearch).toHaveBeenCalled();
  });
});
