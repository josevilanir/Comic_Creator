import React from 'react';

/**
 * EmptyState — estado vazio da biblioteca, com variação de mensagem
 * dependendo se há ou não busca ativa.
 *
 * Props:
 *  - search  {string}  valor atual do campo de busca
 */
function EmptyState({ search }) {
  return (
    <div className="empty-state border-2 border-dashed border-black rounded-xl p-12 text-center my-8">
      <span className="empty-state-emoji text-6xl">📭</span>
      {search ? (
        <>
          <h3 className="font-black text-2xl uppercase mt-4">Nada encontrado</h3>
          <p className="text-gray-600">Nenhum mangá corresponde a &quot;{search}&quot;.</p>
        </>
      ) : (
        <>
          <h3 className="font-black text-2xl uppercase mt-4">Biblioteca vazia</h3>
          <p className="text-gray-600">Vá em <strong>Downloads</strong> para baixar seus primeiros mangás.</p>
        </>
      )}
    </div>
  );
}

export default EmptyState;
