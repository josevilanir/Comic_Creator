import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import ReaderTopbar from '../components/reader/ReaderTopbar';

const defaultProps = {
  decodedManga: 'Dandadan',
  chapterTitle: 'Capítulo 42',
  zoom: 1.4,
  onZoomIn: vi.fn(),
  onZoomOut: vi.fn(),
  onZoomReset: vi.fn(),
  page: 3,
  total: 10,
  onPrevPage: vi.fn(),
  onNextPage: vi.fn(),
  allChapters: [{ filename: 'cap1.pdf' }, { filename: 'cap2.pdf' }],
  currentIdx: 1,
  prevChapter: { filename: 'cap1.pdf' },
  nextChapter: null,
  onPrevChapter: vi.fn(),
  onNextChapter: vi.fn(),
  onBack: vi.fn(),
};

describe('ReaderTopbar', () => {
  it('exibe o nome do mangá e o título do capítulo', () => {
    render(<ReaderTopbar {...defaultProps} />);
    expect(screen.getByText('Dandadan')).toBeInTheDocument();
    expect(screen.getByText('Capítulo 42')).toBeInTheDocument();
  });

  it('exibe o zoom atual em %', () => {
    render(<ReaderTopbar {...defaultProps} zoom={1.4} />);
    expect(screen.getByText('140%')).toBeInTheDocument();
  });

  it('chama onBack ao clicar em Voltar', async () => {
    const onBack = vi.fn();
    render(<ReaderTopbar {...defaultProps} onBack={onBack} />);
    await userEvent.click(screen.getByText(/voltar/i));
    expect(onBack).toHaveBeenCalledOnce();
  });

  it('chama onZoomIn ao clicar em +', async () => {
    const onZoomIn = vi.fn();
    render(<ReaderTopbar {...defaultProps} onZoomIn={onZoomIn} />);
    await userEvent.click(screen.getByTitle(/aumentar zoom/i));
    expect(onZoomIn).toHaveBeenCalledOnce();
  });

  it('chama onZoomOut ao clicar em −', async () => {
    const onZoomOut = vi.fn();
    render(<ReaderTopbar {...defaultProps} onZoomOut={onZoomOut} />);
    await userEvent.click(screen.getByTitle(/diminuir zoom/i));
    expect(onZoomOut).toHaveBeenCalledOnce();
  });

  it('exibe nav de capítulos quando há mais de 1 capítulo', () => {
    render(<ReaderTopbar {...defaultProps} />);
    expect(screen.getByText(/cap\. 2\/2/i)).toBeInTheDocument();
  });

  it('não exibe nav de capítulos quando há apenas 1', () => {
    render(<ReaderTopbar {...defaultProps} allChapters={[{ filename: 'cap1.pdf' }]} />);
    expect(screen.queryByText(/cap\./i)).not.toBeInTheDocument();
  });

  it('exibe o contador de páginas quando total > 0', () => {
    render(<ReaderTopbar {...defaultProps} />);
    expect(screen.getByText('3 / 10')).toBeInTheDocument();
  });

  it('botão de capítulo anterior fica desabilitado quando não há prevChapter', () => {
    render(<ReaderTopbar {...defaultProps} prevChapter={null} />);
    const prevBtn = screen.getByTitle(/capítulo anterior/i);
    expect(prevBtn).toBeDisabled();
  });

  it('botão de próximo capítulo fica desabilitado quando não há nextChapter', () => {
    render(<ReaderTopbar {...defaultProps} nextChapter={null} />);
    const nextBtn = screen.getByTitle(/próximo capítulo/i);
    expect(nextBtn).toBeDisabled();
  });
});
