"""
app.py — Backend Flask ENSA Power BI Portal
Port : 5001 (5000 réservé par AirPlay sur macOS)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Autorise tous les origines en dev

app.config["JWT_SECRET_KEY"]           = "ensa-secret-2025"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
jwt = JWTManager(app)

DB_PATH = os.environ.get("DB_PATH", "../ensa_dw.db")

# ── Helpers ─────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query(sql, params=()):
    conn = get_db()
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()

def query_one(sql, params=()):
    conn = get_db()
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

DASHBOARD_PAGES = {
    "Directeur":    "ReportSection_Directeur",
    "Chef_Filiere": "ReportSection_ChefFiliere",
    "Professeur":   "ReportSection_Professeur",
    "Etudiant":     "ReportSection_Etudiant",
}

# ── AUTH ────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    user = query_one(
        "SELECT * FROM Dim_Utilisateur_Systeme WHERE LOWER(Email_Connexion) = ?",
        (email,)
    )
    if not user:
        return jsonify({"error": "Email inconnu"}), 401
    if user["Mot_De_Passe"] != password:
        return jsonify({"error": "Mot de passe incorrect"}), 401

    token = create_access_token(identity=user["ID_Utilisateur"])
    return jsonify({
        "access_token": token,
        "user": {
            "id":       user["ID_Utilisateur"],
            "email":    user["Email_Connexion"],
            "role":     user["Role_Securite"],
            "id_cible": user["ID_Cible"],
            "filiere":  user["Nom_Filiere_Supervisee"],
        }
    })


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    uid  = get_jwt_identity()
    user = query_one(
        "SELECT * FROM Dim_Utilisateur_Systeme WHERE ID_Utilisateur = ?", (uid,)
    )
    if not user:
        return jsonify({"error": "Introuvable"}), 404
    return jsonify({
        "id":       user["ID_Utilisateur"],
        "email":    user["Email_Connexion"],
        "role":     user["Role_Securite"],
        "id_cible": user["ID_Cible"],
        "filiere":  user["Nom_Filiere_Supervisee"],
    })


@app.route("/api/auth/users", methods=["GET"])
def list_users():
    """Liste tous les utilisateurs groupés par rôle — pour la connexion rapide."""
    rows = query(
        "SELECT ID_Utilisateur, Email_Connexion, Role_Securite, Nom_Filiere_Supervisee "
        "FROM Dim_Utilisateur_Systeme ORDER BY Role_Securite, Email_Connexion"
    )
    grouped = {}
    for r in rows:
        role = r["Role_Securite"]
        grouped.setdefault(role, []).append({
            "id":      r["ID_Utilisateur"],
            "email":   r["Email_Connexion"],
            "filiere": r["Nom_Filiere_Supervisee"],
        })
    return jsonify(grouped)

# ── POWER BI EMBED ───────────────────────────────────────────

@app.route("/api/dashboard/embed", methods=["GET"])
@jwt_required()
def embed_token():
    uid  = get_jwt_identity()
    user = query_one(
        "SELECT * FROM Dim_Utilisateur_Systeme WHERE ID_Utilisateur = ?", (uid,)
    )
    role  = user["Role_Securite"]
    email = user["Email_Connexion"]
    page  = DASHBOARD_PAGES.get(role, "ReportSection_Etudiant")
    return jsonify({
        "embed_url":    os.environ.get("POWERBI_EMBED_URL", "https://app.powerbi.com/reportEmbed?reportId=VOTRE_REPORT_ID"),
        "access_token": os.environ.get("POWERBI_ACCESS_TOKEN", "POWERBI_TOKEN_PLACEHOLDER"),
        "report_id":    os.environ.get("POWERBI_REPORT_ID", "VOTRE_REPORT_ID"),
        "page_name":    page,
        "rls_username": email,
        "rls_roles":    ["Role_Securite_Global"],
    })

# ── STATS ────────────────────────────────────────────────────

@app.route("/api/stats/summary", methods=["GET"])
@jwt_required()
def stats_summary():
    uid  = get_jwt_identity()
    user = query_one(
        "SELECT * FROM Dim_Utilisateur_Systeme WHERE ID_Utilisateur = ?", (uid,)
    )
    role     = user["Role_Securite"]
    id_cible = user["ID_Cible"]
    filiere  = user["Nom_Filiere_Supervisee"]

    if role == "Directeur":
        return jsonify(_stats_directeur())
    elif role == "Chef_Filiere":
        return jsonify(_stats_chef_filiere(filiere))
    elif role == "Professeur":
        return jsonify(_stats_professeur(id_cible))
    elif role == "Etudiant":
        return jsonify(_stats_etudiant(id_cible))
    return jsonify({"error": "Rôle non reconnu"}), 400


def _stats_directeur():
    nb_etudiants  = query_one("SELECT COUNT(*) as n FROM Dim_Etudiant")["n"]
    nb_profs      = query_one("SELECT COUNT(*) as n FROM Dim_Professeur")["n"]
    taux_reussite = query_one("SELECT ROUND(AVG(Validation)*100,1) as t FROM Fait_Resultat_Academique")["t"]
    taux_embauche = query_one(
        "SELECT ROUND(AVG(Embauche_Post_Stage)*100,1) as t FROM Fait_Stage_Insertion WHERE Type_Stage='Stage PFE'"
    )["t"]
    taux_stage    = query_one(
        "SELECT ROUND(AVG(Stage_Trouve)*100,1) as t FROM Fait_Stage_Insertion"
    )["t"]
    repartition   = query(
        "SELECT Filiere, COUNT(*) as nb FROM Dim_Etudiant GROUP BY Filiere ORDER BY nb DESC"
    )
    return {
        "role": "Directeur",
        "kpis": {
            "nb_etudiants":      nb_etudiants,
            "nb_professeurs":    nb_profs,
            "taux_reussite":     taux_reussite,
            "taux_embauche_pfe": taux_embauche,
            "taux_stage_trouve": taux_stage,
        },
        "repartition_filieres": repartition,
    }


def _stats_chef_filiere(filiere):
    moyenne = query_one(
        """SELECT ROUND(AVG(r.Note_Obtenue),2) as moy
           FROM Fait_Resultat_Academique r
           JOIN Dim_Etudiant e ON r.ID_Etudiant = e.ID_Etudiant
           WHERE e.Filiere = ?""", (filiere,)
    )
    top_echec = query(
        """SELECT m.Intitule_Module,
                  ROUND(AVG(CASE WHEN r.Validation=0 THEN 1.0 ELSE 0 END)*100,1) as taux_echec
           FROM Fait_Resultat_Academique r
           JOIN Dim_Filiere_Module m ON r.ID_Module = m.ID_Module
           JOIN Dim_Etudiant e ON r.ID_Etudiant = e.ID_Etudiant
           WHERE e.Filiere = ?
           GROUP BY m.Intitule_Module
           ORDER BY taux_echec DESC LIMIT 5""", (filiere,)
    )
    absences = query_one(
        """SELECT ROUND(AVG(a.Heures_Absence),2) as moy_abs
           FROM Fait_Assiduite a
           JOIN Dim_Etudiant e ON a.ID_Etudiant = e.ID_Etudiant
           WHERE e.Filiere = ?""", (filiere,)
    )
    return {
        "role": "Chef_Filiere",
        "filiere": filiere,
        "kpis": {
            "moyenne_filiere":    moyenne["moy"],
            "moy_heures_absence": absences["moy_abs"],
        },
        "top_modules_echec": top_echec,
    }


def _stats_professeur(id_prof):
    modules = query(
        """SELECT m.Intitule_Module,
                  ROUND(AVG(r.Note_Obtenue),2) as moyenne,
                  ROUND(AVG(r.Validation)*100,1) as taux_reussite,
                  COUNT(DISTINCT r.ID_Etudiant) as nb_etudiants
           FROM Fait_Resultat_Academique r
           JOIN Dim_Filiere_Module m ON r.ID_Module = m.ID_Module
           WHERE r.ID_Professeur = ?
           GROUP BY m.Intitule_Module""", (id_prof,)
    )
    charge = query_one(
        """SELECT SUM(Heures_Assurees) as total_assure,
                  SUM(Heures_Supplementaires) as total_supp
           FROM Fait_Charge_Enseignement WHERE ID_Professeur = ?""", (id_prof,)
    )
    alertes = query(
        """SELECT e.Nom_Complet, SUM(a.Heures_Absence) as total_abs
           FROM Fait_Assiduite a
           JOIN Dim_Etudiant e ON a.ID_Etudiant = e.ID_Etudiant
           WHERE a.ID_Professeur = ? AND a.Sanction_Declenchee = 1
           GROUP BY e.Nom_Complet ORDER BY total_abs DESC LIMIT 5""", (id_prof,)
    )
    return {
        "role": "Professeur",
        "kpis": {
            "heures_assurees":        charge["total_assure"],
            "heures_supplementaires": charge["total_supp"],
        },
        "modules": modules,
        "alertes_absences": alertes,
    }


def _stats_etudiant(id_etu):
    notes = query(
        """SELECT m.Intitule_Module, m.Nom_Filiere,
                  r.Note_Obtenue, r.Validation, r.Est_Rattrapage
           FROM Fait_Resultat_Academique r
           JOIN Dim_Filiere_Module m ON r.ID_Module = m.ID_Module
           WHERE r.ID_Etudiant = ?
           ORDER BY m.Nom_Filiere, m.Intitule_Module""", (id_etu,)
    )
    moyenne_perso = query_one(
        "SELECT ROUND(AVG(Note_Obtenue),2) as moy FROM Fait_Resultat_Academique WHERE ID_Etudiant = ?",
        (id_etu,)
    )
    etu_info = query_one(
        "SELECT Filiere, Niveau FROM Dim_Etudiant WHERE ID_Etudiant = ?", (id_etu,)
    )
    moyenne_promo = query_one(
        """SELECT ROUND(AVG(r.Note_Obtenue),2) as moy
           FROM Fait_Resultat_Academique r
           JOIN Dim_Etudiant e ON r.ID_Etudiant = e.ID_Etudiant
           WHERE e.Filiere = ? AND e.Niveau = ?""",
        (etu_info["Filiere"], etu_info["Niveau"])
    ) if etu_info else {"moy": None}
    absences_total = query_one(
        "SELECT SUM(Heures_Absence) as total FROM Fait_Assiduite WHERE ID_Etudiant = ?",
        (id_etu,)
    )
    stage = query_one(
        """SELECT s.Type_Stage, s.Stage_Trouve, s.Note_Soutenance,
                  s.Embauche_Post_Stage, e.Nom_Entreprise
           FROM Fait_Stage_Insertion s
           LEFT JOIN Dim_Entreprise e ON s.ID_Entreprise = e.ID_Entreprise
           WHERE s.ID_Etudiant = ?
           ORDER BY s.ID_Stage DESC LIMIT 1""", (id_etu,)
    )
    return {
        "role": "Etudiant",
        "kpis": {
            "moyenne_personnelle":   moyenne_perso["moy"],
            "moyenne_promo":         moyenne_promo["moy"],
            "total_heures_absence":  absences_total["total"] or 0,
            "modules_valides":       sum(1 for n in notes if n["Validation"] == 1),
            "modules_rattrapage":    sum(1 for n in notes if n["Est_Rattrapage"] == 1),
        },
        "notes":   notes,
        "stage":   stage,
        "filiere": etu_info["Filiere"] if etu_info else None,
        "niveau":  etu_info["Niveau"]  if etu_info else None,
    }

# ── HEALTH ───────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "port": 5001, "db": DB_PATH})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
