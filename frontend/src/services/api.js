import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';
const API_V1 = `${BASE_URL}/api/v1`;

export { BASE_URL };

export const api = axios.create({
  baseURL: API_V1,
});

// Request: injetar access token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response: refresh automático se 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (res) => res.data, // JSend: {status, data}
  async (error) => {
    const original = error.config;

    // Se não for 401 ou se for uma tentativa de login/refresh que falhou, não tenta refresh
    if (error.response?.status !== 401 || original._retry || original.url?.includes('/auth/login') || original.url?.includes('/auth/refresh')) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      try {
        const token = await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        });
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      } catch (err) {
        return Promise.reject(err);
      }
    }

    original._retry = true;
    isRefreshing = true;

    const refresh_token = localStorage.getItem("refresh_token");
    
    if (!refresh_token) {
      localStorage.clear();
      return Promise.reject(error);
    }

    try {
      // Chamada direta ao axios (global) para evitar interceptor de erro
      const { data } = await axios.post(`${API_V1}/auth/refresh`, { refresh_token });
      
      if (data.status === 'success') {
        const { access_token, refresh_token: new_refresh } = data.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", new_refresh);
        
        api.defaults.headers.common.Authorization = `Bearer ${access_token}`;
        processQueue(null, access_token);
        
        original.headers.Authorization = `Bearer ${access_token}`;
        return api(original);
      } else {
        throw new Error("Refresh failed");
      }
    } catch (err) {
      processQueue(err, null);
      // Apenas limpa se o erro for realmente de autenticação (401 ou 403)
      if (err.response?.status === 401 || err.response?.status === 403) {
          localStorage.clear();
      }
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

export const apiService = {
  getUrls: () => api.get('/urls'),
  saveUrl: (nome, url) => api.post('/urls', { nome, url }),
  removeUrl: (nome) => api.delete(`/urls/${encodeURIComponent(nome)}`),
  downloadSingle: (payload) => api.post('/download', payload),
  downloadRange: (payload) => api.post('/download/range', payload),
  cancelDownload: (jobId) => api.post(`/download/cancelar/${jobId}`),
  getProgress: (jobId) => api.get(`/download/progresso/${jobId}`),
  getChapters: (mangaName, ordem) => api.get(`/library/${encodeURIComponent(mangaName)}?ordem=${ordem}`),
  deleteChapter: (mangaName, filename) => api.delete(`/library/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`),
  getLibrary: () => api.get('/library'),
  deleteManga: (nome) => api.delete(`/library/${encodeURIComponent(nome)}`),
  uploadCover: (nome, formData) => api.post(`/library/${encodeURIComponent(nome)}/capa`, formData),
  toggleLido: (mangaName, filename) => {
      return api.post(`../../capitulo/lido/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`);
  },
  getProgresso: (mangaName, filename) => api.get(`/progresso/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`),
  saveProgresso: (manga, filename, pagina) => api.post(`/progresso`, { manga, filename, pagina }),
  
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  logout: (refresh_token) => api.post('/auth/logout', { refresh_token }),
};
