# Projet 1 : Prise de rendez-vous dans une clinique (ClassicHealth, Douala)

Application web Flask + SQLite. Les patients consultent les médecins, réservent un créneau de 30 minutes
(consultations du matin, 08h00 – 11h30), puis retrouvent, déplacent ou annulent leurs rendez-vous.
Le secrétariat dispose d'un espace administrateur avec statistiques et gestion des rendez-vous.

## Installation

Python 3.10 ou plus récent est nécessaire.

```bash
cd projet
python -m venv venv
# Windows : venv\Scripts\activate        macOS / Linux : source venv/bin/activate
pip install -r requirements.txt
```

La base `projet.db` est fournie, déjà remplie (8 médecins, 50 patients, 150 rendez-vous, 1 administrateur).
Pour la régénérer : `python donnees_test.py` (ou, avec le client sqlite3 : `sqlite3 projet.db < export_projet.sql`).

## Lancement

```bash
python app.py
```

Ouvrir ensuite http://127.0.0.1:5000

En production, définir une clé secrète : `SECRET_KEY=une-longue-valeur-aleatoire` (variable d'environnement).

## Comptes de test

| Rôle | Identifiants | Où |
|------|--------------|----|
| Administrateur | login `admin` / mot de passe `Admin@2026` | http://127.0.0.1:5000/admin/connexion (lien « Espace secrétariat » en bas de page) |
| Patient (avec historique) | téléphone `650 61 84 86` / date de naissance `12/07/1971` (Brice Tabi) | « Mes consultations » |

Un patient qui réserve un rendez-vous est connecté automatiquement à son espace.

## Pages

| URL | Contenu |
|-----|---------|
| `/` | Accueil : spécialités et chiffres lus dans la base |
| `/medecins` | Médecins, recherche en direct, filtre par spécialité, fenêtre de disponibilités |
| `/rendez-vous` | Réservation en 4 étapes (médecin, créneau, coordonnées, vérification) |
| `/confirmation/<id>` | Convocation imprimable et export agenda `.ics` |
| `/mes-consultations` | Espace patient : rendez-vous à venir, historique, déplacer, annuler |
| `/admin/` | Tableau de bord : indicateurs, rendez-vous par statut / spécialité / médecin, nouveaux patients par semaine |
| `/admin/rendez-vous` | Liste filtrable (patient, médecin, statut, dates), changement de statut, export CSV |
| `/admin/patients` | Liste et recherche des patients |

## Règles importantes

- **Pas de double rendez-vous** : la contrainte `UNIQUE (medecin_id, date, heure)` de la base est la protection réelle.
  Si deux patients valident en même temps, le second reçoit « Ce créneau vient d'être pris ».
- **Créneau annulé = créneau libre** : la ligne du rendez-vous annulé est réutilisée par la nouvelle réservation.
- **Déplacer un rendez-vous** = réserver le nouveau créneau et annuler l'ancien dans une seule transaction.
- **Le téléphone identifie le patient** (format `6XXXXXXXX`). Un rendez-vous n'est rattaché à un dossier existant que si la
  date de naissance saisie correspond ; la même paire (téléphone + date de naissance) ouvre « Mes consultations ».
- **Sécurité** : mots de passe hachés (scrypt), requêtes SQL paramétrées, jeton CSRF sur tous les envois,
  limitation à 5 échecs de connexion par tranche de 10 minutes, `PRAGMA foreign_keys = ON` à chaque connexion.

## Organisation du code

```
projet/
├── app.py            routes publiques, réservation, espace patient
├── admin.py          espace administrateur (Blueprint)
├── db.py             connexion SQLite
├── securite.py       jeton CSRF, limitation des tentatives
├── schema.sql / projet.db / export_projet.sql / donnees_test.py   base de données
├── templates/        pages (base.html, partials/, admin/)
└── static/           css/, js/, images/
```

## Captures d'écran

À placer dans `captures/ordinateur/` et `captures/telephone/` (à la racine du dépôt) : accueil, médecins, les 4 étapes
de réservation, confirmation, mes consultations, tableau de bord et liste des rendez-vous de l'administrateur.

## Photos des médecins

Facultatif : déposer dans `static/images/` les fichiers `dr_mbarga.jpg`, `dr_nkoulou.jpg`, `dr_fotso.jpg`, `dr_tchamba.jpg`,
`dr_essomba.jpg`, `dr_ekambi.jpg`, `dr_kamdem.jpg` et `dr_ngwa.jpg`. Sans photo, les initiales du médecin s'affichent.

## Limites connues

- Aucun SMS ni e-mail n'est envoyé : la confirmation se fait à l'écran, par la convocation imprimable et le fichier `.ics`.
- Les honoraires, assurances et tiers-payant ne sont pas gérés (absents du schéma de la base).
