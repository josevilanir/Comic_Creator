import React, { createContext, useContext, useState, useEffect } from "react";
import { apiService as api, api as axiosInstance } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Inicializa o usuário do localStorage
  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) {
        try {
            setUser(JSON.parse(stored));
        } catch (e) {
            localStorage.removeItem("user");
        }
    }
    setLoading(false);
  }, []);

  // Interceptor para detectar quando o token expira permanentemente
  useEffect(() => {
    const interceptor = axiosInstance.interceptors.response.use(
      (res) => res,
      (err) => {
        // Se a chamada de refresh falhou ou se recebemos 401 sem token no storage
        if (err.response?.status === 401 && !localStorage.getItem("access_token")) {
          setUser(null);
        }
        return Promise.reject(err);
      }
    );
    return () => axiosInstance.interceptors.response.eject(interceptor);
  }, []);

  const login = async (username, password) => {
    const data = await api.login(username, password);
    const { user, access_token, refresh_token } = data.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("user", JSON.stringify(user));
    setUser(user);
    return user;
  };

  const register = async (username, email, password) => {
    const data = await api.register(username, email, password);
    const { user, access_token, refresh_token } = data.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("user", JSON.stringify(user));
    setUser(user);
    return user;
  };

  const logout = async () => {
    const refresh_token = localStorage.getItem("refresh_token");
    try { 
        if (refresh_token) await api.logout(refresh_token); 
    } catch (e) {
        console.error("Logout error", e);
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
