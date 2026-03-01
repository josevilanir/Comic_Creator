import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function AuthPage() {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(form.username, form.password);
      } else {
        await register(form.username, form.email, form.password);
      }
      navigate("/");
    } catch (err) {
      console.error("Auth error", err);
      // Ajustando para pegar a mensagem do JSend via axios
      const msg = err.response?.data?.data?.message || err.response?.data?.message || "Erro ao autenticar";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, var(--cream) 0%, var(--cream-dark) 100%)'
    }}>
      <div className="form-card" style={{ maxWidth: '400px', width: '100%' }}>
        <h1 style={{ textAlign: 'center', color: 'var(--coral)', marginBottom: '24px' }}>Comic Creator</h1>
        
        <div className="auth-tabs" style={{ display: 'flex', marginBottom: '20px', gap: '8px' }}>
          <button
            className={`btn ${mode === "login" ? "btn-coral" : "btn-outline"}`}
            style={{ flex: 1 }}
            onClick={() => setMode("login")}
          >
            Entrar
          </button>
          <button
            className={`btn ${mode === "register" ? "btn-coral" : "btn-outline"}`}
            style={{ flex: 1 }}
            onClick={() => setMode("register")}
          >
            Registrar
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="Digite seu username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          {mode === "register" && (
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-input"
                placeholder="seu@email.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Senha</label>
            <input
              type="password"
              className="form-input"
              placeholder="Sua senha"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          {error && (
              <div className="alert alert-error" style={{ marginBottom: '16px', padding: '10px' }}>
                  ⚠️ {error}
              </div>
          )}

          <button type="submit" className="btn btn-coral" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
            {loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}
          </button>
        </form>
      </div>
    </div>
  );
}
