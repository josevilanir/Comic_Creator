import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Library() {
  const [mangas, setMangas] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/api/library')
      .then(res => res.json())
      .then(data => {
        setMangas(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erro ao carregar biblioteca:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="container"><p>Carregando biblioteca...</p></div>;
  }

  if (mangas.length === 0) {
    return (
      <div className="container">
        <p style={{ fontSize: '1.2em', color: '#999' }}>
          Biblioteca vazia. Baixe alguns mangás usando a seção <strong>Início (Baixar)</strong>.
        </p>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>Biblioteca</h2>
      <div className="grid">
        {mangas.map(manga => (
          <div
            key={manga.nome}
            className="card"
            onClick={() => navigate(`/manga/${encodeURIComponent(manga.nome)}`)}
            style={{ cursor: 'pointer' }}
          >
            {manga.tem_capa && manga.capa_url ? (
              <img src={manga.capa_url} alt={manga.nome} />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '280px',
                  backgroundColor: '#444',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#999',
                }}
              >
                Sem Capa
              </div>
            )}
            <div style={{ padding: '10px' }}>
              <h3 style={{ margin: '0 0 5px 0', fontSize: '1em' }}>{manga.nome}</h3>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Library;
