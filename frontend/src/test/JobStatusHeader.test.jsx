import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import JobStatusHeader from '../components/downloader/JobStatusHeader';

describe('JobStatusHeader', () => {
  const baseJob = { atual: 5, status: 'rodando' };

  it('exibe o capítulo atual enquanto range está ativo', () => {
    render(
      <JobStatusHeader rangeAtivo rangeFim={false} jobStatus={baseJob} onCancel={vi.fn()} />
    );
    expect(screen.getByText(/baixando capítulo 5/i)).toBeInTheDocument();
  });

  it('exibe botão de cancelar enquanto range está ativo', () => {
    render(
      <JobStatusHeader rangeAtivo rangeFim={false} jobStatus={baseJob} onCancel={vi.fn()} />
    );
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
  });

  it('chama onCancel ao clicar em Cancelar', async () => {
    const onCancel = vi.fn();
    render(
      <JobStatusHeader rangeAtivo rangeFim={false} jobStatus={baseJob} onCancel={onCancel} />
    );
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it('exibe "concluído" quando rangeFim e status concluido', () => {
    render(
      <JobStatusHeader
        rangeAtivo={false} rangeFim
        jobStatus={{ ...baseJob, status: 'concluido' }}
        onCancel={vi.fn()}
      />
    );
    expect(screen.getByText(/download concluído/i)).toBeInTheDocument();
  });

  it('exibe "cancelado" quando rangeFim e status cancelado', () => {
    render(
      <JobStatusHeader
        rangeAtivo={false} rangeFim
        jobStatus={{ ...baseJob, status: 'cancelado' }}
        onCancel={vi.fn()}
      />
    );
    expect(screen.getByText(/download cancelado/i)).toBeInTheDocument();
  });

  it('não exibe botão de cancelar quando rangeFim', () => {
    render(
      <JobStatusHeader
        rangeAtivo={false} rangeFim
        jobStatus={{ ...baseJob, status: 'concluido' }}
        onCancel={vi.fn()}
      />
    );
    expect(screen.queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
  });
});
