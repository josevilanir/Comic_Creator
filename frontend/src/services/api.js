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
  if (token) config.headers.Authorization = `Bearer ${token}`;
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
  (res) => res.data, // Já retorna o data (JSend: {status, data})
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            return api(original);
          })
          .catch((err) => Promise.reject(err));
      }
      original._retry = true;
      isRefreshing = true;
      const refresh_token = localStorage.getItem("refresh_token");
      if (!refresh_token) {
        // Se não tem refresh token, limpa e vai pro login
        localStorage.clear();
        if (window.location.pathname !== '/login') {
            window.location.href = "/login";
        }
        return Promise.reject(error);
      }
      try {
        // Chamada direta ao axios para não usar o interceptor de erro recursivamente
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
        localStorage.clear();
        if (window.location.pathname !== '/login') {
            window.location.href = "/login";
        }
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

// Adaptando as funções do objeto api para usar axios
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
      // toggleLido ainda está fora do api_bp no backend (/capitulo/lido/...)
      // Mas vamos tentar manter a consistência se possível. 
      // O backend define capitulo_bp sem prefixo /api/v1 no app.py
      return axios.post(`${BASE_URL}/capitulo/lido/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`);
  },
  getProgresso: (mangaName, filename) => api.get(`/progresso/${encodeURIComponent(mangaName)}/${encodeURIComponent(filename)}`),
  saveProgresso: (manga, filename, pagina) => api.post(`/progresso`, { manga, filename, pagina }),
  
  // Novos métodos de Auth
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  logout: (refresh_token) => api.post('/auth/logout', { refresh_token }),
};
