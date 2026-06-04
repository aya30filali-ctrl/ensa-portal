import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);
const API = "http://localhost:5001/api";

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(() => localStorage.getItem("ensa_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetch(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(data => setUser(data))
        .catch(() => { setToken(null); localStorage.removeItem("ensa_token"); })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  async function login(email, password) {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur de connexion");
    localStorage.setItem("ensa_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem("ensa_token");
    setToken(null);
    setUser(null);
  }

  async function apiFetch(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers || {}),
      },
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, apiFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
