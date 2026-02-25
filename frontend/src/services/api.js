const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';
const API_V1 = `${BASE_URL}/api/v1`;

export { BASE_URL };

export const api = {
  getUrls: () => fetch(`${API_V1}/urls`).then(r => r.json()),
  saveUrl: (nome, url) => fetch(`${API_V1}/urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, url }),
  }).then(r => r.json()),
  removeUrl: (nome) => fetch(`${API_V1}/urls/${encodeURIComponent(nome)}`, {
    method: 'DELETE',
  }).then(r => r.json()),
  downloadSingle: (payload) => fetch(`${API_V1}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(r => r.json()),
  downloadRange: (payload) => fetch(`${API_V1}/download/range`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(r => r.json()),
  cancelDownload: (jobId) => fetch(`${API_V1}/download/cancelar/${jobId}`, {
    method: 'POST',
  }).then(r => r.json()),
  getProgress: (jobId) => fetch(`${API_V1}/download/progresso/${jobId}`).then(r => r.json()),
  getChapters: (mangaName, ordem) =>
    fetch(`${API_V1}/library/${encodeURIComponent(mangaName)}?ordem=${ordem}`).then(r => r.json()),
  deleteChapter: (mangaName, filename) =>
    fetch(
      `${API_V1}/library/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`,
      { method: 'DELETE' }
    ).then(r => r.json()),
  getLibrary: () => fetch(`${API_V1}/library`).then(r => r.json()),
  deleteManga: (nome) =>
    fetch(`${API_V1}/library/${encodeURIComponent(nome)}`, { method: 'DELETE' }).then(r => r.json()),
  uploadCover: (nome, formData) =>
    fetch(`${API_V1}/library/${encodeURIComponent(nome)}/capa`, { method: 'POST', body: formData }).then(r => r.json()),
  toggleLido: (mangaName, filename) =>
    fetch(
      `${BASE_URL}/capitulo/lido/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`,
      { method: 'POST' }
    ).then(r => r.json()),
};
