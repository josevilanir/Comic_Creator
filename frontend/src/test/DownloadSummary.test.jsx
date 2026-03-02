import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import DownloadSummary from '../components/downloader/DownloadSummary';

describe('DownloadSummary', () => {
  const makeResultados = (s, f) => [
    ...Array(s).fill({ cap: 1, sucesso: true,  mensagem: 'ok' }),
    ...Array(f).fill({ cap: 2, sucesso: false, mensagem: 'erro' }),
  ];

  it('exibe a contagem correta de sucessos', () => {
    render(<DownloadSummary resultados={makeResultados(7, 3)} />);
    expect(screen.getByText('7')).toBeInTheDocument();
    expect(screen.getByText(/baixados/i)).toBeInTheDocument();
  });

  it('exibe a contagem correta de falhas', () => {
    render(<DownloadSummary resultados={makeResultados(7, 3)} />);
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText(/falhas/i)).toBeInTheDocument();
  });

  it('exibe 0 falhas quando todos foram sucesso', () => {
    render(<DownloadSummary resultados={makeResultados(5, 0)} />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('exibe 0 sucessos quando todos falharam', () => {
    render(<DownloadSummary resultados={makeResultados(0, 4)} />);
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });
});
