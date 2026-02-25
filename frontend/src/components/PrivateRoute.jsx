import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
      return (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
              <div className="spinner"></div>
              <p>Carregando...</p>
          </div>
      );
  }
  
  return user ? children : <Navigate to="/login" replace />;
}
