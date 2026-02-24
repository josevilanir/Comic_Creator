export const BASE_URL = 'http://localhost:5000';

export const api = {
  getUrls: () => fetch(`${BASE_URL}/api/urls`).then(r => r.json()),
  saveUrl: (nome, url) => fetch(`${BASE_URL}/api/urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, url }),
  }).then(r => r.json()),
  removeUrl: (nome) => fetch(`${BASE_URL}/api/urls/${encodeURIComponent(nome)}`, {
    method: 'DELETE',
  }).then(r => r.json()),
  downloadSingle: (payload) => fetch(`${BASE_URL}/api/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(r => r.json()),
  downloadRange: (payload) => fetch(`${BASE_URL}/api/download/range`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(r => r.json()),
  cancelDownload: (jobId) => fetch(`${BASE_URL}/api/download/cancelar/${jobId}`, {
    method: 'POST',
  }).then(r => r.json()),
  getProgress: (jobId) => fetch(`${BASE_URL}/api/download/progresso/${jobId}`).then(r => r.json()),
  getChapters: (mangaName, ordem) =>
    fetch(`${BASE_URL}/api/library/${encodeURIComponent(mangaName)}?ordem=${ordem}`).then(r => r.json()),
  deleteChapter: (mangaName, filename) =>
    fetch(
      `${BASE_URL}/api/library/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`,
      { method: 'DELETE' }
    ).then(r => r.json()),
  getLibrary: () => fetch(`${BASE_URL}/api/library`).then(r => r.json()),
  deleteManga: (nome) =>
    fetch(`${BASE_URL}/api/library/${encodeURIComponent(nome)}`, { method: 'DELETE' }).then(r => r.json()),
  uploadCover: (nome, formData) =>
    fetch(`${BASE_URL}/api/library/${encodeURIComponent(nome)}/capa`, { method: 'POST', body: formData }).then(r => r.json()),
};
