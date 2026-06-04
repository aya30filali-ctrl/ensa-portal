import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

// ── Couleurs et icônes par rôle ─────────────────────────────
const ROLE_CONFIG = {
  Directeur:    { label: "Directeur",        color: "#e74c3c", icon: "🏛",  bg: "#1a0a0a" },
  Chef_Filiere: { label: "Chef de Filière",  color: "#9b59b6", icon: "📊",  bg: "#120a1a" },
  Professeur:   { label: "Professeur",        color: "#3498db", icon: "📚",  bg: "#0a1220" },
  Etudiant:     { label: "Étudiant",          color: "#2ecc71", icon: "🎓",  bg: "#0a1a10" },
};

// ── URLs Power BI par rôle ──────────────────────────────────
const POWERBI_URLS = {
  Directeur:    "https://app.powerbi.com/groups/me/reports/eba5e869-ab33-42d9-934e-17c2cd0cead2/37b5ee6fa2eeb042c306?experience=power-bi",
  Chef_Filiere: "https://app.powerbi.com/groups/me/reports/eba5e869-ab33-42d9-934e-17c2cd0cead2/595ee354bac309201e24?experience=power-bi",
  Professeur:   "https://app.powerbi.com/groups/me/reports/eba5e869-ab33-42d9-934e-17c2cd0cead2/8fc1e2301aee65163a4a?experience=power-bi",
  Etudiant:     "https://app.powerbi.com/groups/me/reports/eba5e869-ab33-42d9-934e-17c2cd0cead2/9ce3f9eeb8b1600a7480?experience=power-bi",
};

// ── Composant KPI Card ───────────────────────────────────────
function KpiCard({ label, value, unit = "", color, icon }) {
  return (
    <div className="kpi-card" style={{ "--kpi-color": color }}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-value">
        {value ?? "—"}
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}

// ── Composant barre de progression ──────────────────────────
function ProgressBar({ label, value, max = 100, color }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="prog-row">
      <div className="prog-meta">
        <span className="prog-label">{label}</span>
        <span className="prog-val">{value}%</span>
      </div>
      <div className="prog-track">
        <div className="prog-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

// ── Dashboard principal ──────────────────────────────────────
export default function Dashboard() {
  const { user, apiFetch, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats]     = useState(null);
  const [embed, setEmbed]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab]         = useState("stats"); // "stats" | "powerbi"

  const cfg = ROLE_CONFIG[user?.role] || ROLE_CONFIG.Etudiant;

  useEffect(() => {
    Promise.all([
      apiFetch("/stats/summary"),
      apiFetch("/dashboard/embed"),
    ])
      .then(([s, e]) => { setStats(s); setEmbed(e); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  function handleLogout() { logout(); navigate("/"); }

  if (loading) return (
    <div className="dash-loading" style={{ background: cfg.bg }}>
      <div className="loading-ring" style={{ "--c": cfg.color }} />
      <p>Chargement de votre tableau de bord…</p>
    </div>
  );

  return (
    <div className="dash-root" style={{ "--accent": cfg.color, "--bg": cfg.bg }}>
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span style={{ color: "#e74c3c" }}>E</span>NSA
        </div>
        <div className="sidebar-role">
          <span className="role-badge" style={{ background: cfg.color + "22", color: cfg.color }}>
            {cfg.icon} {cfg.label}
          </span>
          <p className="sidebar-email">{user?.email}</p>
          {user?.filiere && user.filiere !== "Aucune" && user.filiere !== "Toutes" && (
            <p className="sidebar-filiere">{user.filiere}</p>
          )}
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${tab === "stats" ? "active" : ""}`}
            onClick={() => setTab("stats")}
          >
            <span>📈</span> Statistiques
          </button>
          <button
            className={`nav-item ${tab === "powerbi" ? "active" : ""}`}
            onClick={() => setTab("powerbi")}
          >
            <span>⚡</span> Power BI
          </button>
        </nav>

        <button className="logout-btn" onClick={handleLogout}>
          ← Déconnexion
        </button>
      </aside>

      {/* ── Contenu principal ── */}
      <main className="dash-main">
        <header className="dash-header">
          <div>
            <h1 className="dash-title">
              {tab === "stats" ? "Vue d'ensemble" : "Tableau de bord Power BI"}
            </h1>
            <p className="dash-subtitle">
              {new Date().toLocaleDateString("fr-MA", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
            </p>
          </div>
          <div className="header-accent" style={{ background: cfg.color }} />
        </header>

        {tab === "stats" && stats && (
          <div className="stats-content">
            {/* KPIs selon le rôle */}
            <div className="kpi-grid">
              {renderKpis(stats, cfg.color)}
            </div>

            {/* Contenu détaillé selon le rôle */}
            <div className="detail-grid">
              {renderDetail(stats, cfg.color)}
            </div>
          </div>
        )}

        {tab === "powerbi" && (
          <div className="powerbi-section">
            <div className="pbi-info-card">
              <h3>Tableau de bord Power BI</h3>
              <p>Votre rapport Power BI personnalisé selon votre profil — filtré automatiquement par RLS.</p>
              <div className="pbi-config">
                <div className="pbi-row">
                  <span className="pbi-key">Rôle</span>
                  <span className="pbi-val" style={{ color: cfg.color }}>{cfg.label}</span>
                </div>
                <div className="pbi-row">
                  <span className="pbi-key">Email</span>
                  <span className="pbi-val">{user?.email}</span>
                </div>
                <div className="pbi-row">
                  <span className="pbi-key">Page assignée</span>
                  <span className="pbi-val" style={{ color: cfg.color }}>Dashboard {cfg.label}</span>
                </div>
              </div>
              <div className="pbi-open-section">
                <p className="pbi-open-hint">
                  Cliquez sur le bouton ci-dessous pour ouvrir votre tableau de bord Power BI.<br/>
                  Connectez-vous avec votre email académique pour que le RLS s'applique automatiquement.
                </p>
                <a
                  href={POWERBI_URLS[user?.role]}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="pbi-open-btn"
                  style={{ background: `linear-gradient(135deg, ${cfg.color}, ${cfg.color}99)` }}
                >
                  <span style={{ fontSize: 22 }}>⚡</span>
                  Ouvrir mon Dashboard Power BI
                </a>
              </div>
            </div>
          </div>
        )}
      </main>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }

        .dash-root {
          display: flex;
          min-height: 100vh;
          background: var(--bg);
          font-family: 'DM Sans', sans-serif;
          color: #fff;
        }

        /* ── Sidebar ── */
        .sidebar {
          width: 240px; flex-shrink: 0;
          background: rgba(255,255,255,0.03);
          border-right: 1px solid rgba(255,255,255,0.06);
          display: flex; flex-direction: column;
          padding: 32px 20px;
          position: sticky; top: 0; height: 100vh;
        }
        .sidebar-logo {
          font-family: 'Syne', sans-serif;
          font-size: 28px; font-weight: 800;
          color: #fff; margin-bottom: 32px;
        }
        .sidebar-role { margin-bottom: 32px; }
        .role-badge {
          display: inline-block;
          padding: 6px 12px; border-radius: 20px;
          font-size: 12px; font-weight: 600;
          margin-bottom: 8px;
        }
        .sidebar-email { font-size: 11px; color: rgba(255,255,255,0.35); word-break: break-all; }
        .sidebar-filiere { font-size: 11px; color: rgba(255,255,255,0.25); margin-top: 4px; }

        .sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 4px; }
        .nav-item {
          display: flex; align-items: center; gap: 10px;
          padding: 10px 14px; border-radius: 10px;
          background: none; border: none;
          color: rgba(255,255,255,0.45);
          font-size: 14px; font-family: 'DM Sans', sans-serif;
          cursor: pointer; text-align: left;
          transition: background 0.15s, color 0.15s;
        }
        .nav-item:hover { background: rgba(255,255,255,0.06); color: #fff; }
        .nav-item.active { background: rgba(255,255,255,0.08); color: #fff; font-weight: 500; }

        .logout-btn {
          margin-top: auto;
          padding: 10px 14px; border-radius: 10px;
          background: none; border: 1px solid rgba(255,255,255,0.08);
          color: rgba(255,255,255,0.35); font-size: 13px;
          font-family: 'DM Sans', sans-serif;
          cursor: pointer; transition: all 0.15s;
        }
        .logout-btn:hover { border-color: #e74c3c; color: #e74c3c; }

        /* ── Main ── */
        .dash-main { flex: 1; padding: 40px 48px; overflow-y: auto; }
        .dash-header {
          display: flex; justify-content: space-between; align-items: flex-start;
          margin-bottom: 40px;
        }
        .dash-title {
          font-family: 'Syne', sans-serif;
          font-size: 30px; font-weight: 700; color: #fff;
        }
        .dash-subtitle { font-size: 13px; color: rgba(255,255,255,0.3); margin-top: 4px; }
        .header-accent { width: 4px; height: 40px; border-radius: 2px; align-self: center; }

        /* ── KPI Grid ── */
        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 16px; margin-bottom: 32px;
        }
        .kpi-card {
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 16px; padding: 24px 20px;
          position: relative; overflow: hidden;
          transition: transform 0.2s;
        }
        .kpi-card:hover { transform: translateY(-2px); }
        .kpi-card::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0; height: 3px;
          background: var(--kpi-color);
        }
        .kpi-icon { font-size: 22px; margin-bottom: 12px; }
        .kpi-value {
          font-family: 'Syne', sans-serif;
          font-size: 28px; font-weight: 700;
          color: var(--kpi-color); line-height: 1;
          margin-bottom: 6px;
        }
        .kpi-unit { font-size: 14px; margin-left: 2px; opacity: 0.7; }
        .kpi-label { font-size: 12px; color: rgba(255,255,255,0.4); }

        /* ── Detail Grid ── */
        .detail-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 20px;
        }
        .detail-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 16px; padding: 24px;
        }
        .detail-card h3 {
          font-size: 13px; font-weight: 600;
          text-transform: uppercase; letter-spacing: 1px;
          color: rgba(255,255,255,0.4); margin-bottom: 16px;
        }

        /* Progress bars */
        .prog-row { margin-bottom: 14px; }
        .prog-meta { display: flex; justify-content: space-between; margin-bottom: 6px; }
        .prog-label { font-size: 13px; color: rgba(255,255,255,0.7); }
        .prog-val { font-size: 13px; font-weight: 600; color: #fff; }
        .prog-track { height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
        .prog-fill { height: 100%; border-radius: 3px; transition: width 1s cubic-bezier(0.16,1,0.3,1); }

        /* Table */
        .data-table { width: 100%; border-collapse: collapse; }
        .data-table th {
          font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
          color: rgba(255,255,255,0.3); padding: 8px 0; text-align: left;
          border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .data-table td {
          padding: 10px 0; font-size: 13px; color: rgba(255,255,255,0.75);
          border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .badge {
          display: inline-block; padding: 3px 8px; border-radius: 20px;
          font-size: 11px; font-weight: 600;
        }

        /* Note bar inline */
        .note-bar { display: flex; align-items: center; gap: 8px; }
        .note-fill {
          height: 4px; border-radius: 2px;
          transition: width 0.8s ease;
        }

        /* Stage info */
        .stage-info { display: flex; flex-direction: column; gap: 10px; }
        .stage-row { display: flex; justify-content: space-between; align-items: center; }
        .stage-key { font-size: 13px; color: rgba(255,255,255,0.4); }
        .stage-val { font-size: 13px; font-weight: 500; color: #fff; }

        /* Power BI */
        .powerbi-section { max-width: 860px; }
        .pbi-info-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 16px; padding: 32px;
        }
        .pbi-info-card h3 {
          font-family: 'Syne', sans-serif;
          font-size: 18px; font-weight: 700;
          margin-bottom: 8px;
        }
        .pbi-info-card > p { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 24px; }
        .pbi-config { display: flex; flex-direction: column; gap: 0; margin-bottom: 28px; }
        .pbi-row {
          display: flex; justify-content: space-between;
          padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .pbi-key { font-size: 13px; color: rgba(255,255,255,0.4); }
        .pbi-val { font-size: 13px; font-weight: 500; }
        .pbi-mono { font-family: monospace; font-size: 12px; color: rgba(255,255,255,0.5); }
        .pbi-placeholder { margin-top: 24px; }
        .pbi-mock {
          background: rgba(255,255,255,0.02);
          border: 2px dashed rgba(255,255,255,0.1);
          border-radius: 12px; padding: 60px;
          text-align: center;
        }
        .pbi-mock p { font-size: 16px; font-weight: 500; margin-top: 12px; }
        .pbi-mock-hint { font-size: 12px; color: rgba(255,255,255,0.3); margin-top: 8px; line-height: 1.8; }
        code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-size: 11px; }

        /* Power BI open button */
        .pbi-open-section { margin-top: 24px; text-align: center; }
        .pbi-open-hint { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 24px; line-height: 1.8; }
        .pbi-open-btn {
          display: inline-flex; align-items: center; gap: 12px;
          padding: 16px 32px; border-radius: 12px;
          color: #fff; font-size: 16px; font-weight: 600;
          text-decoration: none;
          font-family: 'DM Sans', sans-serif;
          transition: opacity 0.2s, transform 0.15s;
          box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .pbi-open-btn:hover { opacity: 0.9; transform: translateY(-2px); }

        /* Loading */
        .dash-loading {
          min-height: 100vh; display: flex; flex-direction: column;
          align-items: center; justify-content: center; gap: 20px; color: rgba(255,255,255,0.5);
        }
        .loading-ring {
          width: 44px; height: 44px;
          border: 3px solid rgba(255,255,255,0.1);
          border-top-color: var(--c);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

// ── Render KPIs par rôle ─────────────────────────────────────
function renderKpis(stats, color) {
  const k = stats.kpis;
  if (stats.role === "Directeur") return [
    <KpiCard key="e"  label="Étudiants"       value={k.nb_etudiants}         icon="🎓" color={color} />,
    <KpiCard key="p"  label="Professeurs"      value={k.nb_professeurs}       icon="👨‍🏫" color="#3498db" />,
    <KpiCard key="r"  label="Taux de réussite" value={k.taux_reussite}        icon="📈" color="#2ecc71" unit="%" />,
    <KpiCard key="s"  label="Taux stage trouvé" value={k.taux_stage_trouve}   icon="🏢" color="#f39c12" unit="%" />,
    <KpiCard key="em" label="Embauche PFE"     value={k.taux_embauche_pfe}    icon="✅" color="#9b59b6" unit="%" />,
  ];
  if (stats.role === "Chef_Filiere") return [
    <KpiCard key="m"  label="Moyenne filière"   value={k.moyenne_filiere}      icon="📊" color={color} unit="/20" />,
    <KpiCard key="a"  label="Moy. absences"     value={k.moy_heures_absence}   icon="⏰" color="#e67e22" unit="h" />,
  ];
  if (stats.role === "Professeur") return [
    <KpiCard key="h"  label="Heures assurées"   value={k.heures_assurees}      icon="🕐" color={color} unit="h" />,
    <KpiCard key="hs" label="Heures suppl."     value={k.heures_supplementaires} icon="➕" color="#f39c12" unit="h" />,
  ];
  if (stats.role === "Etudiant") return [
    <KpiCard key="mp" label="Ma moyenne"        value={k.moyenne_personnelle}  icon="⭐" color={color} unit="/20" />,
    <KpiCard key="pr" label="Moy. promo"        value={k.moyenne_promo}        icon="👥" color="#95a5a6" unit="/20" />,
    <KpiCard key="mv" label="Modules validés"   value={k.modules_valides}      icon="✅" color="#2ecc71" />,
    <KpiCard key="mr" label="En rattrapage"     value={k.modules_rattrapage}   icon="⚠️" color="#e74c3c" />,
    <KpiCard key="ab" label="Total absences"    value={k.total_heures_absence} icon="⏱" color="#e67e22" unit="h" />,
  ];
  return [];
}

// ── Render détail par rôle ───────────────────────────────────
function renderDetail(stats, color) {
  if (stats.role === "Directeur") return [
    <div key="fil" className="detail-card">
      <h3>Répartition par filière</h3>
      {stats.repartition_filieres?.map(f => (
        <ProgressBar
          key={f.Filiere}
          label={f.Filiere}
          value={Math.round((f.nb / stats.kpis.nb_etudiants) * 100)}
          color={color}
        />
      ))}
    </div>,
  ];

  if (stats.role === "Chef_Filiere") return [
    <div key="mod" className="detail-card">
      <h3>Top modules en difficulté</h3>
      <table className="data-table">
        <thead><tr><th>Module</th><th>Taux échec</th></tr></thead>
        <tbody>
          {stats.top_modules_echec?.map(m => (
            <tr key={m.Intitule_Module}>
              <td>{m.Intitule_Module}</td>
              <td>
                <span className="badge" style={{
                  background: m.taux_echec > 40 ? "#e74c3c22" : "#f39c1222",
                  color: m.taux_echec > 40 ? "#e74c3c" : "#f39c12"
                }}>
                  {m.taux_echec}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>,
  ];

  if (stats.role === "Professeur") return [
    <div key="mod" className="detail-card">
      <h3>Mes modules</h3>
      <table className="data-table">
        <thead><tr><th>Module</th><th>Moy.</th><th>Réussite</th></tr></thead>
        <tbody>
          {stats.modules?.map(m => (
            <tr key={m.Intitule_Module}>
              <td>{m.Intitule_Module}</td>
              <td style={{ color }}>{m.moyenne}/20</td>
              <td>
                <div className="note-bar">
                  <div className="note-fill" style={{ width: `${m.taux_reussite}%`, background: color, height: 4, borderRadius: 2 }} />
                  <span style={{ fontSize: 12 }}>{m.taux_reussite}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>,
    stats.alertes_absences?.length > 0 && (
      <div key="alrt" className="detail-card">
        <h3>Alertes absences</h3>
        <table className="data-table">
          <thead><tr><th>Étudiant</th><th>Total abs.</th></tr></thead>
          <tbody>
            {stats.alertes_absences.map(a => (
              <tr key={a.Nom_Complet}>
                <td>{a.Nom_Complet}</td>
                <td><span className="badge" style={{ background: "#e74c3c22", color: "#e74c3c" }}>{a.total_abs}h</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    ),
  ].filter(Boolean);

  if (stats.role === "Etudiant") return [
    <div key="notes" className="detail-card">
      <h3>Mes résultats</h3>
      <table className="data-table">
        <thead><tr><th>Module</th><th>Note</th><th>Statut</th></tr></thead>
        <tbody>
          {stats.notes?.map((n, i) => (
            <tr key={i}>
              <td>{n.Intitule_Module}</td>
              <td style={{ color: n.Note_Obtenue >= 12 ? "#2ecc71" : "#e74c3c", fontWeight: 600 }}>
                {n.Note_Obtenue}/20
              </td>
              <td>
                <span className="badge" style={{
                  background: n.Validation ? "#2ecc7122" : n.Est_Rattrapage ? "#f39c1222" : "#e74c3c22",
                  color:      n.Validation ? "#2ecc71"   : n.Est_Rattrapage ? "#f39c12"   : "#e74c3c",
                }}>
                  {n.Validation ? "Validé" : n.Est_Rattrapage ? "Rattrapage" : "Échec"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>,
    stats.stage && (
      <div key="stage" className="detail-card">
        <h3>Mon stage</h3>
        <div className="stage-info">
          <div className="stage-row">
            <span className="stage-key">Type</span>
            <span className="stage-val" style={{ color }}>{stats.stage.Type_Stage}</span>
          </div>
          <div className="stage-row">
            <span className="stage-key">Entreprise</span>
            <span className="stage-val">{stats.stage.Nom_Entreprise || "—"}</span>
          </div>
          <div className="stage-row">
            <span className="stage-key">Stage trouvé</span>
            <span className="badge" style={{ background: stats.stage.Stage_Trouve ? "#2ecc7122" : "#e74c3c22", color: stats.stage.Stage_Trouve ? "#2ecc71" : "#e74c3c" }}>
              {stats.stage.Stage_Trouve ? "Oui" : "Non"}
            </span>
          </div>
          {stats.stage.Note_Soutenance && (
            <div className="stage-row">
              <span className="stage-key">Note soutenance</span>
              <span className="stage-val" style={{ color }}>{stats.stage.Note_Soutenance}/20</span>
            </div>
          )}
          {stats.stage.Type_Stage === "Stage PFE" && (
            <div className="stage-row">
              <span className="stage-key">Embauché</span>
              <span className="badge" style={{ background: stats.stage.Embauche_Post_Stage ? "#2ecc7122" : "#95a5a622", color: stats.stage.Embauche_Post_Stage ? "#2ecc71" : "#95a5a6" }}>
                {stats.stage.Embauche_Post_Stage ? "Oui" : "Non"}
              </span>
            </div>
          )}
        </div>
      </div>
    ),
  ].filter(Boolean);

  return [];
}
