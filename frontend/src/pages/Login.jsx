import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const API = "http://localhost:5001/api";

export default function Login() {
  const { login }  = useAuth();
  const navigate   = useNavigate();
  const [email, setEmail]           = useState("");
  const [password, setPassword]     = useState("");
  const [error, setError]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [users, setUsers]           = useState({});
  const [showPicker, setShowPicker] = useState(false);
  const [pickerRole, setPickerRole] = useState(null);

  useEffect(() => {
    fetch(`${API}/auth/users`)
      .then(r => r.json())
      .then(data => setUsers(data))
      .catch(() => {});
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Email ou mot de passe incorrect");
    } finally {
      setLoading(false);
    }
  }

  function selectUser(userEmail) {
    setEmail(userEmail);
    setPassword("ensa2025");
    setShowPicker(false);
    setPickerRole(null);
  }

  const ROLES = [
    { role: "Directeur",    label: "Directeur",    color: "#e74c3c" },
    { role: "Chef_Filiere", label: "Chef Filière",  color: "#9b59b6" },
    { role: "Professeur",   label: "Professeur",    color: "#3498db" },
    { role: "Etudiant",     label: "Étudiant",      color: "#2ecc71" },
  ];

  return (
    <div className="login-root">
      <div className="login-bg">
        <div className="geo geo-1" /><div className="geo geo-2" /><div className="geo geo-3" />
      </div>

      <div className="login-card">
        <div className="login-header">
          <div className="login-logo"><span className="logo-e">E</span><span className="logo-nsa">NSA</span></div>
          <p className="login-subtitle">École Nationale des Sciences Appliquées — Kénitra</p>
          <div className="login-divider" />
          <h2 className="login-title">Portail Analytique</h2>
          <p className="login-hint">Connectez-vous avec votre email académique</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="field-group">
            <label className="field-label">Adresse email</label>
            <div className="field-wrap">
              <span className="field-icon">✉</span>
              <input type="email" className="field-input" placeholder="prenom.nom@uit.ac.ma"
                value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
          </div>
          <div className="field-group">
            <label className="field-label">Mot de passe</label>
            <div className="field-wrap">
              <span className="field-icon">🔒</span>
              <input type="password" className="field-input" placeholder="••••••••"
                value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? <span className="spinner" /> : "Se connecter"}
          </button>
        </form>

        <div className="demo-section">
          <p className="demo-label">Connexion rapide — mot de passe : <strong>ensa2025</strong></p>
          <div className="demo-grid">
            {ROLES.map(d => (
              <button key={d.role} className="demo-chip" style={{ "--chip-color": d.color }}
                onClick={() => { setPickerRole(d.role); setShowPicker(true); }}>
                <span className="chip-dot" />
                {d.label}
                <span className="chip-count">{users[d.role]?.length || 0}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Picker utilisateurs */}
      {showPicker && pickerRole && (
        <div className="picker-overlay" onClick={() => setShowPicker(false)}>
          <div className="picker-card" onClick={e => e.stopPropagation()}>
            <div className="picker-header">
              <span>Choisir un compte — {ROLES.find(r => r.role === pickerRole)?.label}</span>
              <button className="picker-close" onClick={() => setShowPicker(false)}>✕</button>
            </div>
            <div className="picker-list">
              {(users[pickerRole] || []).map(u => (
                <button key={u.id} className="picker-item" onClick={() => selectUser(u.email)}>
                  <span className="picker-email">{u.email}</span>
                  {u.filiere && u.filiere !== "Aucune" && u.filiere !== "Toutes" && (
                    <span className="picker-filiere">{u.filiere}</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .login-root { min-height:100vh; display:flex; align-items:center; justify-content:center; background:#0a0f1e; font-family:'DM Sans',sans-serif; position:relative; overflow:hidden; }
        .login-bg { position:absolute; inset:0; pointer-events:none; }
        .geo { position:absolute; border:1px solid rgba(255,255,255,0.04); border-radius:50%; animation:pulse 8s ease-in-out infinite; }
        .geo-1 { width:600px; height:600px; top:-200px; right:-150px; }
        .geo-2 { width:400px; height:400px; bottom:-100px; left:-100px; animation-delay:2s; }
        .geo-3 { width:300px; height:300px; top:40%; left:40%; animation-delay:4s; }
        @keyframes pulse { 0%,100%{transform:scale(1);opacity:.4} 50%{transform:scale(1.05);opacity:.7} }
        .login-card { position:relative; width:440px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:24px; padding:48px 40px 36px; backdrop-filter:blur(20px); box-shadow:0 40px 80px rgba(0,0,0,0.5); animation:slideUp .6s cubic-bezier(.16,1,.3,1); }
        @keyframes slideUp { from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:translateY(0)} }
        .login-header { text-align:center; margin-bottom:36px; }
        .login-logo { font-family:'Playfair Display',serif; font-size:42px; line-height:1; margin-bottom:8px; }
        .logo-e { color:#e74c3c; } .logo-nsa { color:#fff; }
        .login-subtitle { font-size:11px; color:rgba(255,255,255,.35); letter-spacing:.5px; margin-bottom:20px; }
        .login-divider { width:40px; height:2px; background:linear-gradient(90deg,#e74c3c,#c0392b); margin:0 auto 20px; border-radius:2px; }
        .login-title { font-size:18px; font-weight:600; color:#fff; margin-bottom:6px; }
        .login-hint { font-size:13px; color:rgba(255,255,255,.4); }
        .login-form { display:flex; flex-direction:column; gap:16px; }
        .field-group { display:flex; flex-direction:column; gap:6px; }
        .field-label { font-size:12px; font-weight:500; color:rgba(255,255,255,.5); letter-spacing:.5px; text-transform:uppercase; }
        .field-wrap { position:relative; }
        .field-icon { position:absolute; left:14px; top:50%; transform:translateY(-50%); font-size:14px; opacity:.4; pointer-events:none; }
        .field-input { width:100%; padding:12px 14px 12px 40px; background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1); border-radius:10px; color:#fff; font-size:14px; font-family:'DM Sans',sans-serif; outline:none; transition:border-color .2s,background .2s; }
        .field-input::placeholder { color:rgba(255,255,255,.2); }
        .field-input:focus { border-color:rgba(231,76,60,.6); background:rgba(255,255,255,.07); }
        .login-error { background:rgba(231,76,60,.15); border:1px solid rgba(231,76,60,.3); border-radius:8px; padding:10px 14px; color:#e74c3c; font-size:13px; }
        .login-btn { margin-top:4px; padding:14px; background:linear-gradient(135deg,#e74c3c,#c0392b); border:none; border-radius:10px; color:#fff; font-size:15px; font-weight:600; font-family:'DM Sans',sans-serif; cursor:pointer; transition:opacity .2s,transform .15s; display:flex; align-items:center; justify-content:center; }
        .login-btn:hover:not(:disabled) { opacity:.9; transform:translateY(-1px); }
        .login-btn:disabled { opacity:.5; cursor:not-allowed; }
        .spinner { width:18px; height:18px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .7s linear infinite; }
        @keyframes spin { to{transform:rotate(360deg)} }
        .demo-section { margin-top:28px; }
        .demo-label { text-align:center; font-size:11px; color:rgba(255,255,255,.3); text-transform:uppercase; letter-spacing:1px; margin-bottom:12px; }
        .demo-label strong { color:rgba(255,255,255,.6); }
        .demo-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
        .demo-chip { display:flex; align-items:center; gap:8px; padding:10px 12px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.07); border-radius:8px; color:rgba(255,255,255,.6); font-size:13px; font-family:'DM Sans',sans-serif; cursor:pointer; transition:background .2s,color .2s; }
        .demo-chip:hover { background:rgba(255,255,255,.08); color:#fff; }
        .chip-dot { width:8px; height:8px; border-radius:50%; background:var(--chip-color); flex-shrink:0; }
        .chip-count { margin-left:auto; font-size:11px; background:rgba(255,255,255,.1); padding:2px 7px; border-radius:10px; color:rgba(255,255,255,.7); }
        .picker-overlay { position:fixed; inset:0; background:rgba(0,0,0,.7); display:flex; align-items:center; justify-content:center; z-index:100; animation:fadeIn .15s ease; }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }
        .picker-card { background:#0f1628; border:1px solid rgba(255,255,255,.1); border-radius:16px; width:400px; max-height:500px; display:flex; flex-direction:column; overflow:hidden; animation:slideUp .2s cubic-bezier(.16,1,.3,1); }
        .picker-header { display:flex; justify-content:space-between; align-items:center; padding:18px 20px; border-bottom:1px solid rgba(255,255,255,.07); font-size:14px; font-weight:600; color:#fff; }
        .picker-close { background:none; border:none; color:rgba(255,255,255,.4); font-size:16px; cursor:pointer; padding:4px 8px; border-radius:6px; transition:background .15s; }
        .picker-close:hover { background:rgba(255,255,255,.08); color:#fff; }
        .picker-list { overflow-y:auto; padding:8px; display:flex; flex-direction:column; gap:2px; }
        .picker-item { display:flex; flex-direction:column; align-items:flex-start; gap:3px; padding:10px 14px; border-radius:8px; background:none; border:none; cursor:pointer; text-align:left; transition:background .15s; }
        .picker-item:hover { background:rgba(255,255,255,.07); }
        .picker-email { font-size:13px; color:#fff; }
        .picker-filiere { font-size:11px; color:rgba(255,255,255,.35); }
      `}</style>
    </div>
  );
}
