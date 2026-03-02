import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import ReaderViewport from '../components/reader/ReaderViewport';

describe('ReaderViewport', () => {
  it('exibe spinner de carregamento quando status="loading"', () => {
    const { container } = render(
      <ReaderViewport status="loading" rendering={false} canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={vi.fn()} onBack={vi.fn()} />
    );
    expect(screen.getByText(/carregando capítulo/i)).toBeInTheDocument();
    expect(container.querySelector('.reader-spinner')).toBeInTheDocument();
  });

  it('exibe mensagem de erro quando status="error"', () => {
    render(
      <ReaderViewport status="error" rendering={false} canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={vi.fn()} onBack={vi.fn()} />
    );
    expect(screen.getByText(/não foi possível carregar/i)).toBeInTheDocument();
  });

  it('chama onBack ao clicar em Voltar na tela de erro', async () => {
    const onBack = vi.fn();
    render(
      <ReaderViewport status="error" rendering={false} canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={vi.fn()} onBack={onBack} />
    );
    await userEvent.click(screen.getByRole('button', { name: /voltar/i }));
    expect(onBack).toHaveBeenCalledOnce();
  });

  it('exibe canvas e zonas de clique quando status="ready"', () => {
    const { container } = render(
      <ReaderViewport status="ready" rendering={false} canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={vi.fn()} onBack={vi.fn()} />
    );
    expect(container.querySelector('canvas')).toBeInTheDocument();
    expect(container.querySelector('.reader-click-prev')).toBeInTheDocument();
    expect(container.querySelector('.reader-click-next')).toBeInTheDocument();
  });

  it('chama onPrev ao clicar na zona esquerda', async () => {
    const onPrev = vi.fn();
    const { container } = render(
      <ReaderViewport status="ready" rendering={false} canvasRef={{ current: null }}
        onPrev={onPrev} onNext={vi.fn()} onBack={vi.fn()} />
    );
    await userEvent.click(container.querySelector('.reader-click-prev'));
    expect(onPrev).toHaveBeenCalledOnce();
  });

  it('chama onNext ao clicar na zona direita', async () => {
    const onNext = vi.fn();
    const { container } = render(
      <ReaderViewport status="ready" rendering={false} canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={onNext} onBack={vi.fn()} />
    );
    await userEvent.click(container.querySelector('.reader-click-next'));
    expect(onNext).toHaveBeenCalledOnce();
  });

  it('aplica opacidade reduzida no canvas durante rendering', () => {
    const { container } = render(
      <ReaderViewport status="ready" rendering canvasRef={{ current: null }}
        onPrev={vi.fn()} onNext={vi.fn()} onBack={vi.fn()} />
    );
    const canvas = container.querySelector('canvas');
    expect(canvas.style.opacity).toBe('0.3');
  });
});
