import pandas as pd
import numpy as np
import random
import unicodedata
from faker import Faker

fake = Faker('fr_FR')
random.seed(42)
np.random.seed(42)

def clean_email(name):
    """Nettoie un nom pour en faire un email valide sans double point."""
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
    # Supprimer les préfixes Dr. / Pr. avant de transformer en email
    for prefix in ['Dr. ', 'Pr. ', 'Dr.', 'Pr.']:
        name = name.replace(prefix, '')
    name = name.strip()
    return name.lower().replace(' ', '.').replace('-', '.')

print("Génération du modèle complet (13 Tables)...")

# ==========================================
# 1. DIM_TEMPS
# ==========================================
dates = pd.date_range(start="2024-09-01", end="2025-06-30")
df_dim_temps = pd.DataFrame({
    'ID_Temps':            dates.strftime('%Y%m%d').astype(int),
    'Date_Complete':       dates.strftime('%Y-%m-%d'),
    'Annee_Universitaire': '2024-2025',
    'Semestre':            np.where(dates.month.isin([9,10,11,12,1]), 'S1', 'S2'),
    'Mois':                dates.month
})

# ==========================================
# 2. DIM_FILIERE_MODULE
# ==========================================
modules_data = [
    (1,  'M-CP101', 'Analyse Mathématique 1',      'CP1', 'Cycle Préparatoire'),
    (2,  'M-CP102', 'Physique Mécanique',           'CP1', 'Cycle Préparatoire'),
    (3,  'M-CP103', 'Informatique Générale',        'CP1', 'Cycle Préparatoire'),
    (4,  'M-CP104', 'Chimie Générale',              'CP1', 'Cycle Préparatoire'),
    (5,  'M-CP201', 'Algèbre Linéaire',             'CP2', 'Cycle Préparatoire'),
    (6,  'M-CP202', 'Électronique de Base',         'CP2', 'Cycle Préparatoire'),
    (7,  'M-CP203', 'Thermodynamique',              'CP2', 'Cycle Préparatoire'),
    (8,  'M-CP204', 'Probabilités & Statistiques',  'CP2', 'Cycle Préparatoire'),
    (9,  'M-GI101', 'Bases de Données Avancées',    'CI1', 'Génie Informatique'),
    (10, 'M-GI102', 'Développement Full-Stack',     'CI1', 'Génie Informatique'),
    (11, 'M-GI103', "Systèmes d'Exploitation",      'CI1', 'Génie Informatique'),
    (12, 'M-GI201', 'Machine Learning & IA',        'CI2', 'Génie Informatique'),
    (13, 'M-GI202', 'Réseaux & Sécurité',           'CI2', 'Génie Informatique'),
    (14, 'M-GI203', 'Architecture Logicielle',      'CI2', 'Génie Informatique'),
    (15, 'M-GI301', 'Big Data & Cloud',             'CI3', 'Génie Informatique'),
    (16, 'M-GI302', 'Cybersécurité Avancée',        'CI3', 'Génie Informatique'),
    (17, 'M-IND101', 'Recherche Opérationnelle',    'CI1', 'Génie Industriel'),
    (18, 'M-IND102', 'Gestion de Production',       'CI1', 'Génie Industriel'),
    (19, 'M-IND103', 'Méthodes Lean',               'CI1', 'Génie Industriel'),
    (20, 'M-IND201', 'Supply Chain Management',     'CI2', 'Génie Industriel'),
    (21, 'M-IND202', 'Qualité & Normes ISO',        'CI2', 'Génie Industriel'),
    (22, 'M-IND301', 'Industrie 4.0',               'CI3', 'Génie Industriel'),
    (23, 'M-IND302', 'Management de Projet',        'CI3', 'Génie Industriel'),
    (24, 'M-GE101', 'Électronique Analogique',      'CI1', 'Génie Électrique'),
    (25, 'M-GE102', 'Électrotechnique',             'CI1', 'Génie Électrique'),
    (26, 'M-GE201', 'Automatique & Contrôle',       'CI2', 'Génie Électrique'),
    (27, 'M-GE202', 'Énergie Renouvelable',         'CI2', 'Génie Électrique'),
    (28, 'M-GE301', 'Systèmes Embarqués',           'CI3', 'Génie Électrique'),
    (29, 'M-MCT101', 'Mécanique des Solides',       'CI1', 'Mécatronique'),
    (30, 'M-MCT102', 'Hydraulique & Pneumatique',   'CI1', 'Mécatronique'),
    (31, 'M-MCT201', 'Robotique Industrielle',      'CI2', 'Mécatronique'),
    (32, 'M-MCT202', 'Conception Assistée',         'CI2', 'Mécatronique'),
    (33, 'M-MCT301', 'Systèmes Mécatroniques',      'CI3', 'Mécatronique'),
    (34, 'M-RST101', 'Protocoles Réseaux',          'CI1', 'RST'),
    (35, 'M-RST102', 'Télécommunications',          'CI1', 'RST'),
    (36, 'M-RST201', 'Réseaux Sans Fil',            'CI2', 'RST'),
    (37, 'M-RST202', 'VoIP & Multimédia',           'CI2', 'RST'),
    (38, 'M-RST301', 'Sécurité Réseaux',            'CI3', 'RST'),
]
df_dim_module = pd.DataFrame(modules_data,
    columns=['ID_Module','Code_Module','Intitule_Module','Niveau','Nom_Filiere'])

# ==========================================
# 3. DIM_PROFESSEUR
# ==========================================
profs_data = [
    (1,  'Alami Ahmed',       'Permanent',  'Informatique'),
    (2,  'Benjelloun Sanaa',  'Permanent',  'Informatique'),
    (3,  'Tazi Amine',        'Vacataire',  'Informatique'),
    (4,  'Idrissi Omar',      'Permanent',  'Génie Industriel'),
    (5,  'El Amrani Fatima',  'Permanent',  'Génie Industriel'),
    (6,  'Chraibi Mehdi',     'Vacataire',  'Génie Industriel'),
    (7,  'Jouhari Kamal',     'Permanent',  'Mathématiques'),
    (8,  'Meziane Yousra',    'Permanent',  'Physique'),
    (9,  'Benali Rachid',     'Permanent',  'Génie Électrique'),
    (10, 'Filali Meryem',     'Permanent',  'Génie Électrique'),
    (11, 'Ouali Hamza',       'Vacataire',  'Génie Électrique'),
    (12, 'Bouhsine Nadia',    'Permanent',  'Mécatronique'),
    (13, 'Cherkaoui Yassine', 'Permanent',  'Mécatronique'),
    (14, 'Lahlou Imane',      'Vacataire',  'RST'),
    (15, 'Mansouri Tarek',    'Permanent',  'RST'),
    (16, 'Berrada Souad',     'Permanent',  'Mathématiques'),
    (17, 'Kettani Adil',      'Permanent',  'Informatique'),
    (18, 'Hajji Loubna',      'Permanent',  'Génie Industriel'),
]
df_dim_professeur = pd.DataFrame(profs_data,
    columns=['ID_Professeur','Nom_Professeur','Statut','Departement'])

module_to_prof = {
    1:7, 2:8, 3:1, 4:8, 5:16, 6:9, 7:8, 8:16,
    9:1, 10:2, 11:17, 12:3, 13:17, 14:2, 15:1, 16:3,
    17:4, 18:5, 19:6, 20:4, 21:18, 22:5, 23:6,
    24:9, 25:10, 26:9, 27:11, 28:10,
    29:12, 30:13, 31:12, 32:13, 33:12,
    34:14, 35:15, 36:14, 37:15, 38:14,
}

# ==========================================
# 4. DIM_ETUDIANT
# ==========================================
villes = ['Kénitra','Rabat','Casablanca','Fès','Tanger','Salé','Marrakech','Oujda']
filieres_ingenieur = ['Génie Informatique','Génie Industriel','Génie Électrique','Mécatronique','RST']
niveaux_filieres = (
    [('CP1','Cycle Préparatoire')] * 2 +
    [('CP2','Cycle Préparatoire')] * 2 +
    [(niv, fil) for fil in filieres_ingenieur for niv in ['CI1','CI2','CI3']]
)

etudiants = []

# Étudiant de démo fixe (ID=999, CI3 GI, email fixe pour la présentation)
etudiants.append({
    "ID_Etudiant":     999,
    "CNE":             "G123456789",
    "Nom_Complet":     "Aya Filali",
    "Date_Naissance":  "2001-03-15",
    "Ville_Origine":   "Kénitra",
    "Mention_Bac":     "Très Bien",
    "Annee_Admission": 2020,
    "Niveau":          "CI3",
    "Filiere":         "Génie Informatique",
})

for i in range(1, 501):
    niv, fil = random.choice(niveaux_filieres)
    annee = {"CP1":2024,"CP2":2023,"CI1":2022,"CI2":2021,"CI3":2020}[niv]
    etudiants.append({
        "ID_Etudiant":     i,
        "CNE":             f"{random.choice([chr(71),chr(75),chr(82)])}{random.randint(100000000,999999999)}",
        "Nom_Complet":     fake.name(),
        "Date_Naissance":  fake.date_of_birth(minimum_age=19, maximum_age=26).strftime("%Y-%m-%d"),
        "Ville_Origine":   random.choice(villes),
        "Mention_Bac":     random.choice(["Assez Bien","Bien","Très Bien"]),
        "Annee_Admission": annee,
        "Niveau":          niv,
        "Filiere":         fil,
    })
df_dim_etudiant = pd.DataFrame(etudiants)

# ==========================================
# 5. DIM_ENTREPRISE
# ==========================================
entreprises_names = [
    'OCP Group','Maroc Telecom','Renault Maroc','CIH Bank','Inwi','Lydec',
    'BMCE Bank','OnshoreMorocco','CGI Maroc','Capgemini Maroc','IBM Maroc',
    'Oracle Maroc','Huawei Maroc','Leoni Maroc','Yazaki Maroc','Delphi Maroc',
    'Safran Maroc','Altran Maroc','SQLI Maroc','Sofrecom','Atos Maroc',
    'Accenture Maroc','Deloitte Maroc','PwC Maroc','RAM Maroc',
    'TotalEnergies Maroc','Siemens Maroc','ABB Maroc','Schneider Electric','Valeo Maroc',
]
secteurs = {
    'OCP Group':'Industrie Minière','Maroc Telecom':'Télécommunications',
    'Renault Maroc':'Automobile','CIH Bank':'Banque/Finance','Inwi':'Télécommunications',
    'Lydec':'Énergie','BMCE Bank':'Banque/Finance','OnshoreMorocco':'Énergie Renouvelable',
    'CGI Maroc':'IT & Software','Capgemini Maroc':'IT & Software','IBM Maroc':'IT & Software',
    'Oracle Maroc':'IT & Software','Huawei Maroc':'Télécommunications','Leoni Maroc':'Automobile',
    'Yazaki Maroc':'Automobile','Delphi Maroc':'Automobile','Safran Maroc':'Aéronautique',
    'Altran Maroc':'Conseil IT','SQLI Maroc':'IT & Software','Sofrecom':'Télécommunications',
    'Atos Maroc':'IT & Software','Accenture Maroc':'Conseil','Deloitte Maroc':'Audit/Conseil',
    'PwC Maroc':'Audit/Conseil','RAM Maroc':'Transport','TotalEnergies Maroc':'Énergie',
    'Siemens Maroc':'Industrie','ABB Maroc':'Énergie','Schneider Electric':'Énergie',
    'Valeo Maroc':'Automobile',
}
entreprises = []
for i, nom in enumerate(entreprises_names, 1):
    entreprises.append({
        'ID_Entreprise':          i,
        'Nom_Entreprise':         nom,
        'Raison_Sociale':         nom,
        'Secteur_Activite':       secteurs.get(nom, 'IT & Software'),
        'Ville':                  random.choice(['Casablanca','Rabat','Kénitra','Tanger','Fès']),
        'Pays':                   'Maroc',
        'Convention_Partenariat': random.choice(['Oui','Non']),
    })
df_dim_entreprise = pd.DataFrame(entreprises)

# ==========================================
# 6. DIM_RESSOURCE_LOGISTIQUE
# ==========================================
ressources = []
for i in range(1, 21):
    ressources.append({
        'ID_Ressource':   i,
        'Type_Ressource': random.choice(['Amphi','Salle TP','Salle de Cours','Labo Informatique']),
        'Capacite':       random.choice([30,45,60,120,200]),
        'Batiment':       random.choice(['Bloc A','Bloc B','Bloc C','Bloc D']),
    })
df_dim_ressource = pd.DataFrame(ressources)

# ==========================================
# 7. DIM_UTILISATEUR_SYSTEME
# — Mot de passe identique pour tous : ensa2025
# — Déduplication email garantie
# ==========================================
MDP = 'ensa2025'

utilisateurs = [
    {'ID_Utilisateur':'DIR_01', 'Email_Connexion':'directeur.ensa@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Directeur',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Toutes'},
    {'ID_Utilisateur':'CH_GI',  'Email_Connexion':'chef.gi@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Génie Informatique'},
    {'ID_Utilisateur':'CH_IND', 'Email_Connexion':'chef.ind@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Génie Industriel'},
    {'ID_Utilisateur':'CH_GE',  'Email_Connexion':'chef.ge@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Génie Électrique'},
    {'ID_Utilisateur':'CH_MCT', 'Email_Connexion':'chef.mct@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Mécatronique'},
    {'ID_Utilisateur':'CH_RST', 'Email_Connexion':'chef.rst@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'RST'},
    {'ID_Utilisateur':'CH_CP',  'Email_Connexion':'chef.cp@uit.ac.ma',
     'Mot_De_Passe': MDP, 'Role_Securite':'Chef_Filiere',
     'ID_Cible':0, 'Nom_Filiere_Supervisee':'Cycle Préparatoire'},
]

emails_vus = set(u['Email_Connexion'] for u in utilisateurs)

# Étudiants
for _, etu in df_dim_etudiant.iterrows():
    email = f"{clean_email(etu['Nom_Complet'])}@etu.uit.ac.ma"
    if email in emails_vus:
        email = f"{clean_email(etu['Nom_Complet'])}.{etu['ID_Etudiant']}@etu.uit.ac.ma"
    emails_vus.add(email)
    utilisateurs.append({
        'ID_Utilisateur':        f"ETU_{etu['ID_Etudiant']}",
        'Email_Connexion':       email,
        'Mot_De_Passe':          MDP,
        'Role_Securite':         'Etudiant',
        'ID_Cible':              etu['ID_Etudiant'],
        'Nom_Filiere_Supervisee':'Aucune',
    })

# Professeurs
for _, prf in df_dim_professeur.iterrows():
    email = f"{clean_email(prf['Nom_Professeur'])}@uit.ac.ma"
    if email in emails_vus:
        email = f"{clean_email(prf['Nom_Professeur'])}.{prf['ID_Professeur']}@uit.ac.ma"
    emails_vus.add(email)
    utilisateurs.append({
        'ID_Utilisateur':        f"PRF_{prf['ID_Professeur']}",
        'Email_Connexion':       email,
        'Mot_De_Passe':          MDP,
        'Role_Securite':         'Professeur',
        'ID_Cible':              prf['ID_Professeur'],
        'Nom_Filiere_Supervisee':'Aucune',
    })

df_dim_utilisateur = pd.DataFrame(utilisateurs)

# ==========================================
# 8. FAITS
# ==========================================
temps_ids = df_dim_temps['ID_Temps'].tolist()
resultats, absences, charges, stages, occupations = [], [], [], [], []

def clip_note(val):
    return round(max(0.0, min(20.0, val)), 2)

# Fait_Charge_Enseignement
for mod_id, prof_id in module_to_prof.items():
    charges.append({
        'ID_Professeur':          prof_id,
        'ID_Module':              mod_id,
        'ID_Temps':               random.choice(temps_ids[:30]),
        'Heures_Assurees':        random.randint(35, 65),
        'Heures_Supplementaires': random.randint(0, 20),
    })

# Fait_Resultat_Academique + Fait_Assiduite
for _, etu in df_dim_etudiant.iterrows():
    fil, niv = etu['Filiere'], etu['Niveau']
    if fil == 'Cycle Préparatoire':
        mods = df_dim_module[df_dim_module['Niveau'] == niv]
    else:
        mods = df_dim_module[(df_dim_module['Nom_Filiere']==fil) & (df_dim_module['Niveau']==niv)]

    for _, mod in mods.iterrows():
        prof_id = module_to_prof[mod['ID_Module']]
        note = clip_note(np.random.normal(12.5, 3.2))
        resultats.append({
            'ID_Etudiant':    etu['ID_Etudiant'],
            'ID_Module':      mod['ID_Module'],
            'ID_Professeur':  prof_id,
            'ID_Temps':       random.choice(temps_ids[150:200]),
            'Note_Obtenue':   note,
            'Validation':     1 if note >= 12 else 0,
            'Est_Rattrapage': 0 if note >= 12 else 1,
        })
        if random.random() < 0.30:
            heures_abs = random.choice([2, 4, 6])
            sanction = 1 if heures_abs >= 6 and random.random() < 0.3 else 0
            absences.append({
                'ID_Etudiant':         etu['ID_Etudiant'],
                'ID_Module':           mod['ID_Module'],
                'ID_Professeur':       prof_id,
                'ID_Temps':            random.choice(temps_ids[20:150]),
                'Heures_Absence':      heures_abs,
                'Est_Justifie':        random.choice([0, 1]),
                'Sanction_Declenchee': sanction,
            })

# Fait_Stage_Insertion
stage_info = {
    'CI1': ('Stage Initiation', False),
    'CI2': ('Stage PFA',        False),
    'CI3': ('Stage PFE',        True),
}
for _, etu in df_dim_etudiant.iterrows():
    if etu['Filiere'] == 'Cycle Préparatoire' or etu['Niveau'] not in stage_info:
        continue
    type_stage, peut_embauche = stage_info[etu['Niveau']]
    duree = {'CI1':1,'CI2':2,'CI3':4}[etu['Niveau']]
    stage_trouve = 1 if random.random() < 0.85 else 0
    embauche = int(np.random.choice([0,1], p=[0.35,0.65])) if (stage_trouve and peut_embauche) else 0
    stages.append({
        'ID_Etudiant':         etu['ID_Etudiant'],
        'ID_Entreprise':       random.choice(df_dim_entreprise['ID_Entreprise'].tolist()) if stage_trouve else None,
        'ID_Temps':            random.choice(temps_ids[-60:]),
        'Type_Stage':          type_stage,
        'Duree_Stage_Mois':    duree,
        'Note_Soutenance':     round(random.uniform(13.0,19.5),2) if stage_trouve else None,
        'Stage_Trouve':        stage_trouve,
        'Embauche_Post_Stage': embauche,
    })

# Fait_Occupation_Locaux
for _, res in df_dim_ressource.iterrows():
    for _ in range(15):
        occupations.append({
            'ID_Ressource':           res['ID_Ressource'],
            'ID_Module':              random.choice(df_dim_module['ID_Module'].tolist()),
            'ID_Temps':               random.choice(temps_ids),
            'Heures_Reservees':       4,
            'Heures_Effectives':      random.choice([2,3,4]),
            'Taux_Remplissage_Moyen': round(random.uniform(0.4,1.0),2),
        })

# Fait_Audit_Securite
# — Utiliser uniquement les ID_Utilisateur réellement générés
ids_utilisateurs = df_dim_utilisateur['ID_Utilisateur'].tolist()
audits = []
for uid in ids_utilisateurs:
    role = df_dim_utilisateur.loc[df_dim_utilisateur['ID_Utilisateur']==uid, 'Role_Securite'].values[0]
    dashboard = {
        'Directeur':    'Dashboard Directeur',
        'Chef_Filiere': 'Dashboard Chef Filière',
        'Professeur':   'Dashboard Professeur',
        'Etudiant':     'Dashboard Étudiant',
    }.get(role, 'Dashboard Autre')
    for _ in range(random.randint(2, 8)):
        audits.append({
            'ID_Utilisateur':      uid,
            'ID_Temps':            random.choice(temps_ids),
            'Nom_Dashboard':       dashboard,
            'Duree_Session':       round(random.uniform(3.0,45.0),1),
            'Nombre_Connexions':   random.randint(1,10),
            'Tentatives_Echouees': random.randint(0,2),
        })
df_audit = pd.DataFrame(audits)

# ── Données démo pour ETU_DEMO (ID=999, CI3, Génie Informatique)
# Résultats sur les modules CI3 GI (IDs 15 et 16)
for mod_id, note in [(15, 16.5), (16, 14.0)]:
    prof_id = module_to_prof[mod_id]
    resultats.append({
        "ID_Etudiant": 999, "ID_Module": mod_id, "ID_Professeur": prof_id,
        "ID_Temps": temps_ids[170], "Note_Obtenue": note,
        "Validation": 1, "Est_Rattrapage": 0,
    })
# Absence démo
absences.append({
    "ID_Etudiant": 999, "ID_Module": 15, "ID_Professeur": module_to_prof[15],
    "ID_Temps": temps_ids[50], "Heures_Absence": 4,
    "Est_Justifie": 1, "Sanction_Declenchee": 0,
})
# Stage PFE démo
stages.append({
    "ID_Etudiant": 999, "ID_Entreprise": 9,
    "ID_Temps": temps_ids[-10], "Type_Stage": "Stage PFE",
    "Duree_Stage_Mois": 4, "Note_Soutenance": 17.5,
    "Stage_Trouve": 1, "Embauche_Post_Stage": 1,
})

# ==========================================
# 9. EXPORT CSV dans ./data/
# ==========================================
import os
os.makedirs('data', exist_ok=True)

df_dim_temps.to_csv('data/Dim_Temps.csv',                     index=False, encoding='utf-8')
df_dim_module.to_csv('data/Dim_Filiere_Module.csv',           index=False, encoding='utf-8')
df_dim_etudiant.to_csv('data/Dim_Etudiant.csv',               index=False, encoding='utf-8')
df_dim_professeur.to_csv('data/Dim_Professeur.csv',           index=False, encoding='utf-8')
df_dim_entreprise.to_csv('data/Dim_Entreprise.csv',           index=False, encoding='utf-8')
df_dim_ressource.to_csv('data/Dim_Ressource_Logistique.csv',  index=False, encoding='utf-8')
df_dim_utilisateur.to_csv('data/Dim_Utilisateur_Systeme.csv', index=False, encoding='utf-8')
pd.DataFrame(resultats).to_csv('data/Fait_Resultat_Academique.csv', index=False, encoding='utf-8')
pd.DataFrame(absences).to_csv('data/Fait_Assiduite.csv',            index=False, encoding='utf-8')
pd.DataFrame(charges).to_csv('data/Fait_Charge_Enseignement.csv',   index=False, encoding='utf-8')
pd.DataFrame(stages).to_csv('data/Fait_Stage_Insertion.csv',        index=False, encoding='utf-8')
pd.DataFrame(occupations).to_csv('data/Fait_Occupation_Locaux.csv', index=False, encoding='utf-8')
df_audit.to_csv('data/Fait_Audit_Securite.csv',                      index=False, encoding='utf-8')

print("\n✅ Génération terminée !")
print(f"  Dim_Etudiant            : {len(df_dim_etudiant)} étudiants")
print(f"  Dim_Filiere_Module      : {len(df_dim_module)} modules")
print(f"  Dim_Professeur          : {len(df_dim_professeur)} profs")
print(f"  Dim_Entreprise          : {len(df_dim_entreprise)} entreprises")
print(f"  Dim_Ressource_Logistique: {len(df_dim_ressource)} salles")
print(f"  Dim_Utilisateur_Systeme : {len(df_dim_utilisateur)} utilisateurs (0 doublon garanti)")
print(f"  Fait_Resultat_Academique: {len(resultats)} résultats")
print(f"  Fait_Assiduite          : {len(absences)} absences")
print(f"  Fait_Charge_Enseignement: {len(charges)} charges")
print(f"  Fait_Stage_Insertion    : {len(stages)} stages")
print(f"  Fait_Occupation_Locaux  : {len(occupations)} occupations")
print(f"  Fait_Audit_Securite     : {len(df_audit)} audits")
print("\nEmails de connexion:")
print("  Directeur  → directeur.ensa@uit.ac.ma")
print("  Chef GI    → chef.gi@uit.ac.ma")
print("  Chef IND   → chef.ind@uit.ac.ma")
print("  Chef GE    → chef.ge@uit.ac.ma")
print("  Professeur → alami.ahmed@uit.ac.ma")
print("  Étudiant   → etudiant.demo@etu.uit.ac.ma")