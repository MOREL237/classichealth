"""
ClassicHealth : remplissage de la base de données de test.

Usage :  python donnees_test.py
Résultat : crée projet.db (à partir de schema.sql) et export_projet.sql.

Volumes : 8 médecins (4 spécialités), 50 patients, 150 rendez-vous
répartis sur deux mois (30 jours avant et 30 jours après aujourd'hui).
Le tirage est reproductible (graine fixe) : mêmes noms, mêmes numéros.
"""
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

DOSSIER = Path(__file__).resolve().parent
DB = DOSSIER / "projet.db"
SCHEMA = DOSSIER / "schema.sql"
EXPORT = DOSSIER / "export_projet.sql"

# Compte administrateur de test (à indiquer dans le README)
ADMIN_LOGIN = "admin"
ADMIN_MOT_DE_PASSE = "Admin@2026"

random.seed(2026)
AUJOURDHUI = date.today()

HEURES = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]

# ---------------------------------------------------------------------
# Médecins : 8 médecins, 4 spécialités (jours : 1 = lundi ... 7 = dimanche)
# ---------------------------------------------------------------------
MEDECINS = [
    ("Dr Jean-Pierre Mbarga",   "Médecine générale", "dr_mbarga.jpg",   "1,2,3,4,5"),
    ("Dr Estelle Nkoulou",      "Médecine générale", "dr_nkoulou.jpg",  "1,3,5"),
    ("Dr Alain Fotso",          "Cardiologie",       "dr_fotso.jpg",    "2,4"),
    ("Dr Carine Tchamba",       "Cardiologie",       "dr_tchamba.jpg",  "1,3,6"),
    ("Dr Paul Essomba",         "Pédiatrie",         "dr_essomba.jpg",  "1,2,4,5"),
    ("Dr Mireille Ekambi",      "Pédiatrie",         "dr_ekambi.jpg",   "3,4,6"),
    ("Dr Serge Kamdem",         "Dermatologie",      "dr_kamdem.jpg",   "2,3,5"),
    ("Dr Brenda Ngwa",          "Dermatologie",      "dr_ngwa.jpg",     "1,4,5"),
]
# Poids de popularité (certains médecins sont plus demandés que d'autres)
POIDS_MEDECINS = [10, 7, 8, 5, 9, 6, 6, 4]

# ---------------------------------------------------------------------
# Noms et prénoms courants au Cameroun (Douala et environs)
# ---------------------------------------------------------------------
NOMS = [
    "Mbarga", "Nkoulou", "Fotso", "Tchamba", "Essomba", "Ekambi", "Kamdem",
    "Ngwa", "Kamga", "Njoya", "Tagne", "Nana", "Mballa", "Atangana", "Ndongo",
    "Biyong", "Owona", "Manga", "Eyenga", "Kouam", "Tchinda", "Djomo",
    "Mvondo", "Etoundi", "Ndzie", "Bekolo", "Ayissi", "Ngono", "Tabi",
    "Njock", "Bell", "Moukouri", "Dikongue", "Penda", "Ebanda", "Kotto",
    "Mouelle", "Sone", "Mbassi", "Fokou", "Tsafack", "Wouambo", "Nguemo",
    "Ndam", "Abena", "Bikoula", "Ngassa", "Simo", "Kenfack", "Youmbi",
]
PRENOMS_H = [
    "Jean", "Paul", "Patrick", "Serge", "Alain", "Blaise", "Christian",
    "Hervé", "Rodrigue", "Éric", "Landry", "Cédric", "Thierry", "Martial",
    "Arnaud", "Fabrice", "Ulrich", "Boris", "Brice", "Yannick",
]
PRENOMS_F = [
    "Marie", "Estelle", "Carine", "Mireille", "Sandrine", "Nadège", "Julienne",
    "Rosine", "Flore", "Clarisse", "Pélagie", "Michèle", "Annie", "Brenda",
    "Larissa", "Prisca", "Ornella", "Chantal", "Joëlle", "Danielle",
]
# Douala très majoritaire, quelques autres villes
VILLES = (["Douala"] * 34 + ["Bonabéri"] * 4 + ["Édéa"] * 3 + ["Yaoundé"] * 3
          + ["Kribi"] * 2 + ["Limbé"] * 2 + ["Nkongsamba"] * 1 + ["Bafoussam"] * 1)

MOTIFS = {
    "Médecine générale": [
        "Consultation générale", "Fièvre persistante", "Paludisme (suspicion)",
        "Maux de tête fréquents", "Douleurs abdominales", "Bilan de santé",
        "Certificat médical", "Suivi hypertension", "Fatigue inhabituelle",
    ],
    "Cardiologie": [
        "Douleurs thoraciques", "Contrôle de la tension", "Palpitations",
        "Électrocardiogramme", "Suivi cardiaque", "Essoufflement à l'effort",
    ],
    "Pédiatrie": [
        "Vaccination", "Fièvre de l'enfant", "Toux persistante",
        "Suivi de croissance", "Diarrhée", "Visite de contrôle",
    ],
    "Dermatologie": [
        "Éruption cutanée", "Acné", "Mycose", "Démangeaisons",
        "Contrôle d'un grain de beauté", "Eczéma",
    ],
}


def numero_unique(deja_pris):
    """Génère un numéro camerounais de 9 chiffres (6XX XX XX XX), jamais utilisé."""
    while True:
        prefixe = random.choice(["650", "651", "652", "655", "670", "671", "675",
                                 "677", "678", "680", "681", "690", "691", "694",
                                 "695", "696", "697", "699"])
        numero = prefixe + "".join(random.choices("0123456789", k=6))
        if numero not in deja_pris:
            deja_pris.add(numero)
            return numero


def creer_patients():
    """Retourne 50 patients (sans date_creation : calculée après les rendez-vous)."""
    patients, tels, identites = [], set(), set()
    while len(patients) < 50:
        feminin = random.random() < 0.55
        prenom = random.choice(PRENOMS_F if feminin else PRENOMS_H)
        nom = random.choice(NOMS)
        if (nom, prenom) in identites:
            continue
        identites.add((nom, prenom))
        naissance = date(1950, 1, 1) + timedelta(days=random.randint(0, 365 * 70))
        patients.append({
            "nom": nom, "prenom": prenom,
            "telephone": numero_unique(tels),
            "date_naissance": naissance.isoformat(),
            "ville": random.choice(VILLES),
        })
    return patients


def jours_ouvres_du_medecin(jours_str):
    """Liste des dates de la fenêtre (-30 j ... +30 j) où le médecin consulte."""
    jours = {int(j) for j in jours_str.split(",")}
    debut = AUJOURDHUI - timedelta(days=30)
    return [debut + timedelta(days=i) for i in range(61)
            if (debut + timedelta(days=i)).isoweekday() in jours]


def creer_rendez_vous(patients, medecins_ids):
    """150 rendez-vous sans doublon, cohérents avec les jours de consultation."""
    pris = set()            # (medecin_id, date, heure) déjà utilisés
    rdvs = []
    jours_par_medecin = {i + 1: jours_ouvres_du_medecin(m[3]) for i, m in enumerate(MEDECINS)}

    # Chaque patient a au moins 1 rendez-vous (50), puis 100 autres au hasard
    patients_cibles = list(range(50)) + random.choices(range(50), k=100)
    random.shuffle(patients_cibles)

    for idx_patient in patients_cibles:
        while True:
            mid = random.choices(medecins_ids, weights=POIDS_MEDECINS)[0]
            jour = random.choice(jours_par_medecin[mid])
            heure = random.choice(HEURES[:6] if random.random() < 0.7 else HEURES)
            if (mid, jour, heure) not in pris:
                pris.add((mid, jour, heure))
                break

        specialite = MEDECINS[mid - 1][1]
        # Statut cohérent avec la date : le passé est effectué ou annulé, jamais "prévu"
        if jour < AUJOURDHUI:
            statut = "annule" if random.random() < 0.17 else "effectue"
        else:
            statut = "annule" if random.random() < 0.08 else "prevu"
        # Date de prise : quelques jours avant le rendez-vous (et jamais dans le futur)
        prise = min(jour - timedelta(days=random.randint(1, 10)), AUJOURDHUI)
        prise_dt = datetime.combine(prise, datetime.min.time()) + timedelta(
            hours=random.randint(8, 18), minutes=random.randint(0, 59))
        rdvs.append({
            "patient_idx": idx_patient, "medecin_id": mid,
            "date": jour.isoformat(), "heure": heure,
            "motif": random.choice(MOTIFS[specialite]),
            "statut": statut, "date_prise": prise_dt.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rdvs


def main():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    # Médecins
    for m in MEDECINS:
        conn.execute("INSERT INTO medecins (nom, specialite, photo, jours_consultation) "
                     "VALUES (?, ?, ?, ?)", m)
    medecins_ids = [r[0] for r in conn.execute("SELECT id FROM medecins ORDER BY id")]

    # Patients + rendez-vous
    patients = creer_patients()
    rdvs = creer_rendez_vous(patients, medecins_ids)

    # Un patient est "créé" le jour de sa première prise de rendez-vous
    # (permet d'avoir des nouveaux patients répartis sur plusieurs semaines)
    for i, p in enumerate(patients):
        premiere = min(r["date_prise"] for r in rdvs if r["patient_idx"] == i)
        p["date_creation"] = premiere[:10]
        cur = conn.execute(
            "INSERT INTO patients (nom, prenom, telephone, date_naissance, ville, date_creation) "
            "VALUES (:nom, :prenom, :telephone, :date_naissance, :ville, :date_creation)", p)
        p["id"] = cur.lastrowid

    for r in rdvs:
        conn.execute(
            "INSERT INTO rendez_vous (patient_id, medecin_id, date, heure, motif, statut, date_prise) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patients[r["patient_idx"]]["id"], r["medecin_id"], r["date"], r["heure"],
             r["motif"], r["statut"], r["date_prise"]))

    # Administrateur (mot de passe hashé, jamais en clair)
    conn.execute("INSERT INTO administrateurs (login, mot_de_passe_hash) VALUES (?, ?)",
                 (ADMIN_LOGIN, generate_password_hash(ADMIN_MOT_DE_PASSE)))
    conn.commit()

    # Export complet de la base
    EXPORT.write_text("\n".join(conn.iterdump()) + "\n", encoding="utf-8")

    for table in ("medecins", "patients", "rendez_vous", "administrateurs"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:<16} {n:>4} lignes")
    print(f"\nBase créée : {DB.name} | export : {EXPORT.name}")
    print(f"Compte admin : {ADMIN_LOGIN} / {ADMIN_MOT_DE_PASSE}")
    conn.close()


if __name__ == "__main__":
    main()
