import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ChapterList() {
  const { mangaName } = useParams();
  const navigate = useNavigate();
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortOrder, setSortOrder] = useState('asc');

  useEffect(() => {
    const decodedName = decodeURIComponent(mangaName);
    fetch(`http://localhost:5000/api/library/${encodeURIComponent(decodedName)}?ordem=${sortOrder}`)
      .then(res => res.json())
      .then(data => {
        setChapters(data.chapters || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erro ao carregar capítulos:', err);
        setLoading(false);
      });
  }, [mangaName, sortOrder]);

  const handleDelete = (filename) => {
    if (!window.confirm(`Deletar capítulo "${filename}"?`)) return;

    const decodedName = decodeURIComponent(mangaName);
    fetch(`http://localhost:5000/excluir_capitulo/${encodeURIComponent(decodedName)}/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    })
      .then(res => res.json())
      .then(() => {
        setChapters(chapters.filter(ch => ch.filename !== filename));
      })
      .catch(err => console.error('Erro ao deletar:', err));
  };

  if (loading) {
    return (
      <div className="container">
        <button onClick={() => navigate('/library')} style={{ marginBottom: '20px' }}>
          ← Voltar
        </button>
        <p>Carregando capítulos...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <button onClick={() => navigate('/library')} style={{ marginBottom: '20px' }}>
        ← Voltar
      </button>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>{decodeURIComponent(mangaName)}</h2>
        <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}>
          Ordenar: {sortOrder === 'asc' ? 'Crescente' : 'Decrescente'}
        </button>
      </div>

      {chapters.length === 0 ? (
        <p>Nenhum capítulo disponível.</p>
      ) : (
        <div style={{ display: 'grid', gap: '10px' }}>
          {chapters.map(chapter => (
            <div
              key={chapter.filename}
              style={{
                display: 'flex',
                padding: '15px',
                backgroundColor: '#2a2a2a',
                borderRadius: '8px',
                alignItems: 'center',
                gap: '15px',
              }}
            >
              {chapter.thumbnail && (
                <img
                  src={chapter.thumbnail}
                  alt={chapter.title}
                  style={{
                    width: '60px',
                    height: '80px',
                    objectFit: 'cover',
                    borderRadius: '4px',
                  }}
                />
              )}
              <div style={{ flex: 1 }}>
                <a
                  href={chapter.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: '1.1em',
                    color: '#3498db',
                    textDecoration: 'none',
                  }}
                >
                  {chapter.title}
                </a>
                {chapter.read && <span style={{ marginLeft: '10px', color: '#2ecc71' }}>✓ Lido</span>}
              </div>
              <button
                onClick={() => handleDelete(chapter.filename)}
                style={{
                  backgroundColor: '#e74c3c',
                  color: 'white',
                  border: 'none',
                  padding: '8px 12px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Deletar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChapterList;
