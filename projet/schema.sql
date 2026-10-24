-- =====================================================================
-- ClassicHealth : schéma de la base de données (SQLite)
-- Projet 1 : Prise de rendez-vous dans une clinique
-- =====================================================================
-- IMPORTANT : SQLite n'active pas les clés étrangères par défaut.
-- Dans app.py, exécuter à CHAQUE connexion : PRAGMA foreign_keys = ON;
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS rendez_vous;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS medecins;
DROP TABLE IF EXISTS administrateurs;

-- ---------------------------------------------------------------------
-- Médecins
-- jours_consultation : numéros des jours séparés par des virgules,
-- 1 = lundi ... 7 = dimanche (ex. '1,3,5' = lundi, mercredi, vendredi)
-- ---------------------------------------------------------------------
CREATE TABLE medecins (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                 TEXT NOT NULL,
    specialite          TEXT NOT NULL,
    photo               TEXT,                       -- nom du fichier dans static/images/
    jours_consultation  TEXT NOT NULL
        CHECK (jours_consultation GLOB '[1-7]*' AND jours_consultation NOT GLOB '*[^1-7,]*')
);

-- ---------------------------------------------------------------------
-- Patients (le téléphone identifie le patient : il est unique)
-- ---------------------------------------------------------------------
CREATE TABLE patients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,
    prenom          TEXT NOT NULL,
    telephone       TEXT NOT NULL UNIQUE,           -- format normalisé : 6XXXXXXXX (9 chiffres)
    date_naissance  TEXT NOT NULL,                  -- AAAA-MM-JJ
    ville           TEXT NOT NULL,
    date_creation   TEXT NOT NULL DEFAULT (date('now'))   -- sert aux stats "nouveaux patients par semaine"
);

-- ---------------------------------------------------------------------
-- Rendez-vous
-- La contrainte UNIQUE (medecin_id, date, heure) est la VRAIE protection
-- contre les doubles rendez-vous, même si deux patients valident
-- exactement en même temps.
-- ---------------------------------------------------------------------
CREATE TABLE rendez_vous (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    medecin_id  INTEGER NOT NULL REFERENCES medecins(id) ON DELETE RESTRICT,
    date        TEXT NOT NULL,                      -- AAAA-MM-JJ
    heure       TEXT NOT NULL
        CHECK (heure IN ('08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30')),
    motif       TEXT NOT NULL,
    statut      TEXT NOT NULL DEFAULT 'prevu'
        CHECK (statut IN ('prevu','effectue','annule')),
    date_prise  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (medecin_id, date, heure)
);

-- ---------------------------------------------------------------------
-- Administrateurs (le mot de passe n'est JAMAIS stocké en clair)
-- ---------------------------------------------------------------------
CREATE TABLE administrateurs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    login               TEXT NOT NULL UNIQUE,
    mot_de_passe_hash   TEXT NOT NULL               -- généré avec werkzeug.security.generate_password_hash
);

-- ---------------------------------------------------------------------
-- Index pour accélérer les requêtes fréquentes
-- ---------------------------------------------------------------------
CREATE INDEX idx_rdv_patient ON rendez_vous(patient_id);
CREATE INDEX idx_rdv_date    ON rendez_vous(date);
CREATE INDEX idx_rdv_statut  ON rendez_vous(statut);
CREATE INDEX idx_patients_nom ON patients(nom, prenom);
CREATE INDEX idx_medecins_specialite ON medecins(specialite);
