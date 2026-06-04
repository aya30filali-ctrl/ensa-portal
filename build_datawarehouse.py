"""
build_datawarehouse.py
======================
Crée le Data Warehouse SQLite de l'ENSA Kénitra
à partir des fichiers CSV existants.

Usage:
    python build_datawarehouse.py --csv-dir ./data --db ensa_dw.db
"""

import sqlite3
import pandas as pd
import os
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# SCHÉMA DDL — colonnes alignées sur tes CSV
# ─────────────────────────────────────────────

SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ══════════════════════════════
--  DIMENSIONS
-- ══════════════════════════════

CREATE TABLE IF NOT EXISTS Dim_Etudiant (
    ID_Etudiant       INTEGER PRIMARY KEY,
    CNE               TEXT    NOT NULL UNIQUE,
    Nom_Complet       TEXT    NOT NULL,
    Date_Naissance    TEXT,
    Ville_Origine     TEXT,
    Mention_Bac       TEXT,
    Annee_Admission   INTEGER,
    Niveau            TEXT,
    Filiere           TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Temps (
    ID_Temps              INTEGER PRIMARY KEY,
    Date_Complete         TEXT    NOT NULL UNIQUE,
    Annee_Universitaire   TEXT,
    Semestre              TEXT,
    Mois                  INTEGER
);

CREATE TABLE IF NOT EXISTS Dim_Filiere_Module (
    ID_Module       INTEGER PRIMARY KEY,
    Code_Module     TEXT    NOT NULL,
    Intitule_Module TEXT    NOT NULL,
    Niveau          TEXT,
    Nom_Filiere     TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Professeur (
    ID_Professeur   INTEGER PRIMARY KEY,
    Nom_Professeur  TEXT    NOT NULL,
    Statut          TEXT,
    Departement     TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Utilisateur_Systeme (
    ID_Utilisateur         TEXT NOT NULL PRIMARY KEY,
    Email_Connexion        TEXT NOT NULL UNIQUE,
    Mot_De_Passe           TEXT NOT NULL DEFAULT 'ensa2025',
    Role_Securite          TEXT NOT NULL,
    ID_Cible               TEXT,
    Nom_Filiere_Supervisee TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Entreprise (
    ID_Entreprise           INTEGER PRIMARY KEY,
    Nom_Entreprise          TEXT    NOT NULL,
    Raison_Sociale          TEXT,
    Secteur_Activite        TEXT,
    Ville                   TEXT,
    Pays                    TEXT DEFAULT 'Maroc',
    Convention_Partenariat  TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Ressource_Logistique (
    ID_Ressource    INTEGER PRIMARY KEY,
    Type_Ressource  TEXT,
    Capacite        INTEGER,
    Batiment        TEXT
);

-- ══════════════════════════════
--  TABLES DE FAITS
-- ══════════════════════════════

CREATE TABLE IF NOT EXISTS Fait_Resultat_Academique (
    ID_Resultat     INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Etudiant     INTEGER NOT NULL,
    ID_Module       INTEGER NOT NULL,
    ID_Professeur   INTEGER,
    ID_Temps        INTEGER NOT NULL,
    Note_Obtenue    REAL,
    Validation      INTEGER DEFAULT 0,
    Est_Rattrapage  INTEGER DEFAULT 0,
    FOREIGN KEY (ID_Etudiant)   REFERENCES Dim_Etudiant(ID_Etudiant),
    FOREIGN KEY (ID_Module)     REFERENCES Dim_Filiere_Module(ID_Module),
    FOREIGN KEY (ID_Professeur) REFERENCES Dim_Professeur(ID_Professeur),
    FOREIGN KEY (ID_Temps)      REFERENCES Dim_Temps(ID_Temps)
);

CREATE TABLE IF NOT EXISTS Fait_Assiduite (
    ID_Assiduite         INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Etudiant          INTEGER NOT NULL,
    ID_Module            INTEGER NOT NULL,
    ID_Professeur        INTEGER,
    ID_Temps             INTEGER NOT NULL,
    Heures_Absence       REAL    DEFAULT 0,
    Est_Justifie         INTEGER DEFAULT 0,
    Sanction_Declenchee  INTEGER DEFAULT 0,
    FOREIGN KEY (ID_Etudiant)   REFERENCES Dim_Etudiant(ID_Etudiant),
    FOREIGN KEY (ID_Module)     REFERENCES Dim_Filiere_Module(ID_Module),
    FOREIGN KEY (ID_Professeur) REFERENCES Dim_Professeur(ID_Professeur),
    FOREIGN KEY (ID_Temps)      REFERENCES Dim_Temps(ID_Temps)
);

CREATE TABLE IF NOT EXISTS Fait_Charge_Enseignement (
    ID_Charge                INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Professeur            INTEGER NOT NULL,
    ID_Module                INTEGER NOT NULL,
    ID_Temps                 INTEGER NOT NULL,
    Heures_Assurees          REAL    DEFAULT 0,
    Heures_Supplementaires   REAL    DEFAULT 0,
    FOREIGN KEY (ID_Professeur) REFERENCES Dim_Professeur(ID_Professeur),
    FOREIGN KEY (ID_Module)     REFERENCES Dim_Filiere_Module(ID_Module),
    FOREIGN KEY (ID_Temps)      REFERENCES Dim_Temps(ID_Temps)
);

CREATE TABLE IF NOT EXISTS Fait_Stage_Insertion (
    ID_Stage             INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Etudiant          INTEGER NOT NULL,
    ID_Entreprise        INTEGER,
    ID_Temps             INTEGER NOT NULL,
    Type_Stage           TEXT,
    Duree_Stage_Mois     REAL,
    Note_Soutenance      REAL,
    Stage_Trouve         INTEGER DEFAULT 0,
    Embauche_Post_Stage  INTEGER DEFAULT 0,
    FOREIGN KEY (ID_Etudiant)   REFERENCES Dim_Etudiant(ID_Etudiant),
    FOREIGN KEY (ID_Entreprise) REFERENCES Dim_Entreprise(ID_Entreprise),
    FOREIGN KEY (ID_Temps)      REFERENCES Dim_Temps(ID_Temps)
);

CREATE TABLE IF NOT EXISTS Fait_Occupation_Locaux (
    ID_Occupation            INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Ressource             INTEGER NOT NULL,
    ID_Module                INTEGER,
    ID_Temps                 INTEGER NOT NULL,
    Heures_Reservees         REAL,
    Heures_Effectives        REAL,
    Taux_Remplissage_Moyen   REAL,
    FOREIGN KEY (ID_Ressource) REFERENCES Dim_Ressource_Logistique(ID_Ressource),
    FOREIGN KEY (ID_Module)    REFERENCES Dim_Filiere_Module(ID_Module),
    FOREIGN KEY (ID_Temps)     REFERENCES Dim_Temps(ID_Temps)
);

CREATE TABLE IF NOT EXISTS Fait_Audit_Securite (
    ID_Audit             INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Utilisateur       TEXT    NOT NULL,
    ID_Temps             INTEGER NOT NULL,
    Nom_Dashboard        TEXT,
    Duree_Session        REAL,
    Nombre_Connexions    INTEGER DEFAULT 0,
    Tentatives_Echouees  INTEGER DEFAULT 0,
    FOREIGN KEY (ID_Utilisateur) REFERENCES Dim_Utilisateur_Systeme(ID_Utilisateur),
    FOREIGN KEY (ID_Temps)       REFERENCES Dim_Temps(ID_Temps)
);

-- ══════════════════════════════
--  INDEX pour performances
-- ══════════════════════════════
CREATE INDEX IF NOT EXISTS idx_resultat_etudiant   ON Fait_Resultat_Academique(ID_Etudiant);
CREATE INDEX IF NOT EXISTS idx_resultat_module     ON Fait_Resultat_Academique(ID_Module);
CREATE INDEX IF NOT EXISTS idx_assiduite_etudiant  ON Fait_Assiduite(ID_Etudiant);
CREATE INDEX IF NOT EXISTS idx_assiduite_prof      ON Fait_Assiduite(ID_Professeur);
CREATE INDEX IF NOT EXISTS idx_charge_prof         ON Fait_Charge_Enseignement(ID_Professeur);
CREATE INDEX IF NOT EXISTS idx_stage_etudiant      ON Fait_Stage_Insertion(ID_Etudiant);
CREATE INDEX IF NOT EXISTS idx_stage_type          ON Fait_Stage_Insertion(Type_Stage);
CREATE INDEX IF NOT EXISTS idx_utilisateur_email   ON Dim_Utilisateur_Systeme(Email_Connexion);
CREATE INDEX IF NOT EXISTS idx_utilisateur_role    ON Dim_Utilisateur_Systeme(Role_Securite);
"""

# ─────────────────────────────────────────────
# MAPPING: nom fichier CSV → nom table SQLite
# ─────────────────────────────────────────────

CSV_TABLE_MAP = {
    "dim_etudiant":               "Dim_Etudiant",
    "dim_temps":                  "Dim_Temps",
    "dim_filiere_module":         "Dim_Filiere_Module",
    "dim_professeur":             "Dim_Professeur",
    "dim_utilisateur_systeme":    "Dim_Utilisateur_Systeme",
    "dim_entreprise":             "Dim_Entreprise",
    "dim_ressource_logistique":   "Dim_Ressource_Logistique",
    "fait_resultat_academique":   "Fait_Resultat_Academique",
    "fait_assiduite":             "Fait_Assiduite",
    "fait_charge_enseignement":   "Fait_Charge_Enseignement",
    "fait_stage_insertion":       "Fait_Stage_Insertion",
    "fait_occupation_locaux":     "Fait_Occupation_Locaux",
    "fait_audit_securite":        "Fait_Audit_Securite",
}

# Ordre de chargement : dimensions d'abord, faits ensuite
LOAD_ORDER = [
    "Dim_Temps",
    "Dim_Filiere_Module",
    "Dim_Etudiant",
    "Dim_Professeur",
    "Dim_Entreprise",
    "Dim_Ressource_Logistique",
    "Dim_Utilisateur_Systeme",
    "Fait_Resultat_Academique",
    "Fait_Assiduite",
    "Fait_Charge_Enseignement",
    "Fait_Stage_Insertion",
    "Fait_Occupation_Locaux",
    "Fait_Audit_Securite",
]

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def create_schema(conn):
    log.info("Création du schéma...")
    conn.executescript(SCHEMA)
    conn.commit()
    log.info("✅ Schéma créé avec succès.")


def detect_csv_files(csv_dir):
    csv_path = Path(csv_dir)
    found = {}
    for csv_file in csv_path.glob("*.csv"):
        stem = csv_file.stem.lower().replace(" ", "_").replace("-", "_")
        for key, table in CSV_TABLE_MAP.items():
            if key in stem or stem in key:
                found[table] = csv_file
                log.info(f"  ✅ Reconnu: {csv_file.name} → {table}")
                break
        else:
            log.warning(f"  ⚠️  Non reconnu, ignoré: {csv_file.name}")
    return found


def load_csv_to_table(conn, csv_file, table_name):
    log.info(f"  → Chargement {csv_file.name} dans {table_name}...")
    try:
        df = pd.read_csv(csv_file, encoding="utf-8", sep=None, engine="python")
        df.columns = [c.strip() for c in df.columns]
        df = df.where(pd.notnull(df), None)

        # Corriger le double point dans les emails (dr..nom → dr.nom)
        if "Email_Connexion" in df.columns:
            df["Email_Connexion"] = df["Email_Connexion"].str.replace(r'\.\.+', '.', regex=True)

        # Supprimer les doublons sur la clé primaire et Email_Connexion
        pk_map = {
            "Dim_Utilisateur_Systeme": ["ID_Utilisateur", "Email_Connexion"],
            "Dim_Etudiant":            ["ID_Etudiant"],
            "Dim_Professeur":          ["ID_Professeur"],
            "Dim_Filiere_Module":      ["ID_Module"],
            "Dim_Temps":               ["ID_Temps"],
            "Dim_Entreprise":          ["ID_Entreprise"],
            "Dim_Ressource_Logistique":["ID_Ressource"],
        }
        if table_name in pk_map:
            cols_dedup = [c for c in pk_map[table_name] if c in df.columns]
            before = len(df)
            df = df.drop_duplicates(subset=cols_dedup, keep="first")
            if len(df) < before:
                log.warning(f"     ⚠️  {before - len(df)} doublon(s) supprimé(s).")

        # Ne garde que les colonnes existantes dans la table SQLite
        existing_cols = [
            row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]
        common_cols = [c for c in df.columns if c in existing_cols]
        df = df[common_cols]

        df.to_sql(table_name, conn, if_exists="append", index=False, method="multi")
        log.info(f"     ✅ {len(df)} lignes insérées ({len(common_cols)} colonnes).")
    except Exception as e:
        log.error(f"     ❌ Erreur sur {table_name}: {e}")
        raise


def verify_integrity(conn):
    log.info("\n📊 RÉSUMÉ DU DATA WAREHOUSE:")
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for (table,) in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0]
        log.info(f"   {table:<35} → {count:>6} lignes")

    log.info("\n🔍 Vérification des clés étrangères...")
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        log.warning(f"⚠️  {len(violations)} violations FK détectées:")
        for v in violations[:10]:
            log.warning(f"   {v}")
    else:
        log.info("✅ Aucune violation de clé étrangère.")


def build(csv_dir, db_path):
    log.info(f"🚀 Construction du Data Warehouse: {db_path}")
    log.info(f"   Source CSV: {csv_dir}\n")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        create_schema(conn)

        csv_map = detect_csv_files(csv_dir)
        if not csv_map:
            log.error(f"Aucun CSV reconnu dans '{csv_dir}'.")
            return

        log.info(f"\n📂 {len(csv_map)} fichier(s) CSV détecté(s):\n")

        for table in LOAD_ORDER:
            if table in csv_map:
                load_csv_to_table(conn, csv_map[table], table)
            else:
                log.warning(f"  ⚠️  Pas de CSV pour {table}, table vide.")

        conn.commit()
        verify_integrity(conn)
        log.info(f"\n🎉 Data Warehouse prêt : {db_path}")

    except Exception as e:
        log.error(f"Erreur critique: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-dir", default="./data", help="Dossier des CSV")
    parser.add_argument("--db", default="ensa_dw.db", help="Fichier SQLite de sortie")
    args = parser.parse_args()
    build(args.csv_dir, args.db)