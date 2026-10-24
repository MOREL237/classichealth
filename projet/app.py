# Application Flask : ClassicHealth (étapes 1-2 : accueil + médecins & spécialités)
import os
import re
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import securite
from admin import admin_bp
from db import get_db, init_app as init_db
from flask import Flask, Response, abort, g, jsonify, redirect, render_template, request, session, url_for

DOSSIER = Path(__file__).resolve().parent
IMAGES = DOSSIER / "static" / "images"

app = Flask(__name__)
# Sert à mémoriser le dernier rendez-vous pris (page de confirmation). À changer en production.
app.secret_key = os.environ.get("SECRET_KEY", "dev-changez-moi")
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)
init_db(app)
securite.init_app(app)
app.register_blueprint(admin_bp)

HEURES = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
JOURS_COURTS = {1: "Lun", 2: "Mar", 3: "Mer", 4: "Jeu", 5: "Ven", 6: "Sam", 7: "Dim"}
JOURS_NOMS = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi", 6: "Samedi", 7: "Dimanche"}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOTIFS = [
    "Première consultation",
    "Suivi et renouvellement",
    "Bilan préventif",
    "Avis médical prioritaire",
    "Contrôle après traitement",
]
VILLES = ["Douala", "Bonabéri", "Édéa", "Yaoundé", "Kribi", "Limbé", "Nkongsamba", "Bafoussam", "Autre"]
PASTILLES = [(1, "L"), (2, "M"), (3, "M"), (4, "J"), (5, "V"), (6, "S")]

DESCRIPTIONS = {
    "Médecine générale": "Consultations courantes, bilans de santé annuels, dépistage et prise en charge globale des pathologies.",
    "Cardiologie": "Bilan cardiovasculaire, suivi de l'hypertension artérielle, électrocardiogramme (ECG) et échodoppler.",
    "Pédiatrie": "Suivi pédiatrique du nourrisson à l'adolescent, calendrier vaccinal camerounais et urgences de l'enfant.",
    "Dermatologie": "Maladies de peau tropicales, acné, dermatoses allergiques et dépistage des lésions cutanées.",
}


def initiales(nom):
    """'Dr Jean-Pierre Mbarga' -> 'JM'."""
    mots = nom.replace("Dr ", "").split()
    return (mots[0][0] + mots[-1][0]).upper()


def jours_du_medecin(texte):
    return {int(j) for j in texte.split(",")}


def creneaux_pris(medecin_id, jour_iso):
    """Heures déjà prises ce jour-là (un rendez-vous annulé libère le créneau)."""
    lignes = get_db().execute(
        "SELECT heure FROM rendez_vous WHERE medecin_id = ? AND date = ? AND statut != 'annule'",
        (medecin_id, jour_iso),
    ).fetchall()
    return {l["heure"] for l in lignes}


def prochain_creneau(medecin_id, jours):
    """Premier créneau libre dans les 14 prochains jours, sous forme de texte lisible."""
    maintenant = datetime.now()
    for decalage in range(15):
        jour = date.today() + timedelta(days=decalage)
        if jour.isoweekday() not in jours:
            continue
        pris = creneaux_pris(medecin_id, jour.isoformat())
        for h in HEURES:
            if h in pris or (decalage == 0 and h <= maintenant.strftime("%H:%M")):
                continue
            heure = h.replace(":", "h")
            if decalage == 0:
                return f"Aujourd'hui à {heure}"
            if decalage == 1:
                return f"Demain à {heure}"
            return f"{JOURS_NOMS[jour.isoweekday()]} {jour:%d/%m} à {heure}"
    return None


def charger_specialites():
    """Spécialités avec nombre de médecins et jours de consultation."""
    medecins = get_db().execute(
        "SELECT nom, specialite, jours_consultation FROM medecins ORDER BY specialite, nom"
    ).fetchall()
    groupes = {}
    for m in medecins:
        s = groupes.setdefault(m["specialite"], {"nb": 0, "jours": set()})
        s["nb"] += 1
        s["jours"] |= jours_du_medecin(m["jours_consultation"])
    return [
        {
            "nom": nom,
            "description": DESCRIPTIONS.get(nom, ""),
            "nb_medecins": infos["nb"],
            "jours": ", ".join(JOURS_COURTS[j] for j in sorted(infos["jours"])),
        }
        for nom, infos in groupes.items()
    ]


@app.context_processor
def donnees_communes():
    """Variables disponibles dans tous les templates (pied de page, etc.)."""
    return {"specialites": charger_specialites(), "annee": date.today().year}


@app.route("/")
def accueil():
    db = get_db()
    nb_medecins = db.execute("SELECT COUNT(*) FROM medecins").fetchone()[0]
    premier = db.execute("SELECT nom, specialite FROM medecins ORDER BY id LIMIT 1").fetchone()
    vedette = (
        {"nom": premier["nom"], "specialite": premier["specialite"], "initiales": initiales(premier["nom"])}
        if premier else None
    )
    return render_template("accueil.html", nb_medecins=nb_medecins, vedette=vedette)


def charger_medecins():
    lignes = get_db().execute(
        "SELECT id, nom, specialite, photo, jours_consultation FROM medecins ORDER BY specialite, nom"
    ).fetchall()
    liste = []
    for m in lignes:
        jours = jours_du_medecin(m["jours_consultation"])
        liste.append({
            "id": m["id"],
            "nom": m["nom"],
            "specialite": m["specialite"],
            "initiales": initiales(m["nom"]),
            "photo": m["photo"] if m["photo"] and (IMAGES / m["photo"]).exists() else None,
            "jours": ",".join(str(j) for j in sorted(jours)),
            "jours_texte": ", ".join(JOURS_COURTS[j] for j in sorted(jours)),
            "pastilles": [(lettre, JOURS_NOMS[n], n in jours) for n, lettre in PASTILLES],
            "prochain": prochain_creneau(m["id"], jours),
        })
    return liste


@app.route("/medecins")
def medecins():
    liste = charger_medecins()
    filtre = request.args.get("specialite", "")
    if filtre not in {m["specialite"] for m in liste}:
        filtre = ""
    return render_template("medecins.html", medecins=liste, filtre=filtre, aujourdhui=date.today().isoformat())


@app.route("/api/creneaux/<int:medecin_id>")
def api_creneaux(medecin_id):
    """Créneaux d'un médecin pour une date (AAAA-MM-JJ), utilisé par la fenêtre de disponibilités."""
    m = get_db().execute("SELECT jours_consultation FROM medecins WHERE id = ?", (medecin_id,)).fetchone()
    if m is None:
        abort(404)
    try:
        jour = date.fromisoformat(request.args.get("date", ""))
    except ValueError:
        return jsonify(erreur="Date invalide."), 400
    if jour < date.today():
        return jsonify(erreur="Cette date est passée."), 400
    if jour.isoweekday() not in jours_du_medecin(m["jours_consultation"]):
        return jsonify(ouvert=False, creneaux=[], message=f"Pas de consultation le {JOURS_NOMS[jour.isoweekday()].lower()}.")
    pris = creneaux_pris(medecin_id, jour.isoformat())
    maintenant = datetime.now().strftime("%H:%M")
    creneaux = [
        {"heure": h, "libre": h not in pris and not (jour == date.today() and h <= maintenant)}
        for h in HEURES
    ]
    return jsonify(ouvert=True, creneaux=creneaux)


# ---------------------------------------------------------------------
# Prise de rendez-vous
# ---------------------------------------------------------------------
class CreneauPris(Exception):
    pass


class MauvaiseIdentite(Exception):
    pass


def normaliser_telephone(brut):
    """'699 45 88 12' ou '+237 699458812' -> '699458812' (9 chiffres, commence par 6), sinon None."""
    chiffres = re.sub(r"\D", "", brut or "")
    if len(chiffres) == 12 and chiffres.startswith("237"):
        chiffres = chiffres[3:]
    return chiffres if re.fullmatch(r"6\d{8}", chiffres) else None


def telephone_lisible(tel):
    return f"+237 {tel[0:3]} {tel[3:5]} {tel[5:7]} {tel[7:9]}"


def erreur(champ, message, code=400):
    return jsonify(champ=champ, erreur=message), code


def date_longue(jour):
    return f"{JOURS_NOMS[jour.isoweekday()]} {jour.day} {MOIS[jour.month - 1]} {jour.year}"


def heure_fin(heure):
    h, m = map(int, heure.split(":"))
    m += 30
    return f"{h + m // 60:02d}:{m % 60:02d}"


def reference(rdv_id, date_prise):
    return f"CH-{date_prise[:4]}-{rdv_id:04d}"


def verifier_creneau(medecin_id, date_txt, heure):
    """Contrôle médecin, jour de consultation et heure. Retourne (medecin_id, jour, None) ou (None, None, (champ, message))."""
    try:
        medecin_id = int(medecin_id)
    except (TypeError, ValueError):
        return None, None, ("medecin", "Veuillez choisir un médecin.")
    m = get_db().execute("SELECT jours_consultation FROM medecins WHERE id = ?", (medecin_id,)).fetchone()
    if m is None:
        return None, None, ("medecin", "Médecin introuvable.")
    try:
        jour = date.fromisoformat(str(date_txt or ""))
    except ValueError:
        return None, None, ("date", "Veuillez choisir une date.")
    if jour < date.today():
        return None, None, ("date", "Cette date est passée.")
    if jour.isoweekday() not in jours_du_medecin(m["jours_consultation"]):
        return None, None, ("date", f"Ce médecin ne consulte pas le {JOURS_NOMS[jour.isoweekday()].lower()}.")
    if heure not in HEURES:
        return None, None, ("heure", "Veuillez choisir un créneau.")
    if jour == date.today() and heure <= datetime.now().strftime("%H:%M"):
        return None, None, ("heure", "Ce créneau est déjà passé.")
    return medecin_id, jour, None


def reserver(db, patient_id, medecin_id, jour, heure, motif):
    """Réserve un créneau et retourne l'id du rendez-vous (la ligne d'un rendez-vous annulé est réutilisée).
    À appeler dans un bloc `with db:`. Lève CreneauPris si le créneau est occupé."""
    ligne = db.execute("SELECT id, statut FROM rendez_vous WHERE medecin_id = ? AND date = ? AND heure = ?",
                       (medecin_id, jour.isoformat(), heure)).fetchone()
    if ligne is None:
        return db.execute(
            "INSERT INTO rendez_vous (patient_id, medecin_id, date, heure, motif) VALUES (?, ?, ?, ?, ?)",
            (patient_id, medecin_id, jour.isoformat(), heure, motif)).lastrowid
    if ligne["statut"] == "annule":
        db.execute("UPDATE rendez_vous SET patient_id = ?, motif = ?, statut = 'prevu', date_prise = datetime('now') WHERE id = ?",
                   (patient_id, motif, ligne["id"]))
        return ligne["id"]
    raise CreneauPris


@app.route("/rendez-vous")
def rendez_vous():
    return render_template("rendezvous.html", medecins=charger_medecins(), motifs=MOTIFS, villes=VILLES,
                           aujourdhui=date.today().isoformat())


@app.route("/api/rendez-vous", methods=["POST"])
def api_rendez_vous():
    d = request.get_json(silent=True) or {}
    db = get_db()

    medecin_id, jour, err = verifier_creneau(d.get("medecin_id"), d.get("date"), d.get("heure"))
    if err:
        return erreur(*err)
    heure = d["heure"]

    nom = str(d.get("nom", "")).strip()
    prenom = str(d.get("prenom", "")).strip()
    if not 2 <= len(nom) <= 60:
        return erreur("nom", "Indiquez votre nom (2 à 60 caractères).")
    if not 2 <= len(prenom) <= 60:
        return erreur("prenom", "Indiquez votre prénom (2 à 60 caractères).")
    tel = normaliser_telephone(d.get("telephone"))
    if tel is None:
        return erreur("telephone", "Numéro camerounais invalide : 9 chiffres commençant par 6.")
    try:
        naissance = date.fromisoformat(str(d.get("date_naissance", "")))
    except ValueError:
        return erreur("date_naissance", "Indiquez votre date de naissance.")
    if not date(1900, 1, 1) <= naissance <= date.today():
        return erreur("date_naissance", "Date de naissance invalide.")
    ville = str(d.get("ville", "")).strip()
    if not 2 <= len(ville) <= 60:
        return erreur("ville", "Indiquez votre ville.")
    motif = str(d.get("motif", "")).strip()
    if motif not in MOTIFS:
        return erreur("motif", "Choisissez un motif de consultation.")
    notes = str(d.get("notes", "")).strip()[:300]
    motif_final = f"{motif} : {notes}" if notes else motif

    try:
        with db:
            patient = db.execute("SELECT id, date_naissance FROM patients WHERE telephone = ?", (tel,)).fetchone()
            if patient is None:
                patient_id = db.execute(
                    "INSERT INTO patients (nom, prenom, telephone, date_naissance, ville) VALUES (?, ?, ?, ?, ?)",
                    (nom, prenom, tel, naissance.isoformat(), ville)).lastrowid
            elif patient["date_naissance"] == naissance.isoformat():
                patient_id = patient["id"]
            else:  # le téléphone identifie le patient : on ne rattache pas un rendez-vous au dossier d'un autre
                raise MauvaiseIdentite
            rdv_id = reserver(db, patient_id, medecin_id, jour, heure, motif_final)
    except MauvaiseIdentite:
        return erreur("date_naissance", "Ces informations ne correspondent pas au dossier associé à ce numéro.")
    except (CreneauPris, sqlite3.IntegrityError):
        return erreur("creneau", "Ce créneau vient d'être pris. Choisissez-en un autre.", 409)

    session["dernier_rdv"] = rdv_id
    session["patient_id"] = patient_id
    return jsonify(ok=True, url=url_for("confirmation", rdv_id=rdv_id, nouveau=1))


def charger_rdv(rdv_id):
    r = get_db().execute(
        """SELECT r.id, r.date, r.heure, r.motif, r.date_prise, p.nom AS patient_nom, p.prenom, p.telephone,
                  p.ville, m.nom AS medecin_nom, m.specialite
           FROM rendez_vous r JOIN patients p ON p.id = r.patient_id JOIN medecins m ON m.id = r.medecin_id
           WHERE r.id = ?""",
        (rdv_id,),
    ).fetchone()
    if r is None:
        abort(404)
    jour = date.fromisoformat(r["date"])
    return r, {
        "ref": reference(r["id"], r["date_prise"]),
        "date_longue": date_longue(jour),
        "fin": heure_fin(r["heure"]),
        "telephone": telephone_lisible(r["telephone"]),
        "jour": jour,
    }


def peut_voir(rdv_id):
    """Seul l'auteur du rendez-vous ou le patient connecté peut voir la convocation."""
    if session.get("dernier_rdv") == rdv_id:
        return True
    pid = session.get("patient_id")
    return bool(pid) and get_db().execute(
        "SELECT 1 FROM rendez_vous WHERE id = ? AND patient_id = ?", (rdv_id, pid)).fetchone() is not None


@app.route("/confirmation/<int:rdv_id>")
def confirmation(rdv_id):
    if not peut_voir(rdv_id):
        return redirect(url_for("mes_consultations"))
    r, info = charger_rdv(rdv_id)
    return render_template("confirmation.html", r=r, info=info, nouveau=request.args.get("nouveau") == "1")


@app.route("/confirmation/<int:rdv_id>.ics")
def confirmation_ics(rdv_id):
    if not peut_voir(rdv_id):
        return redirect(url_for("mes_consultations"))
    r, info = charger_rdv(rdv_id)
    jour = r["date"].replace("-", "")
    debut = f"{jour}T{r['heure'].replace(':', '')}00"
    fin = f"{jour}T{info['fin'].replace(':', '')}00"
    lignes = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ClassicHealth Douala//Consultation//FR",
        "BEGIN:VEVENT", f"UID:{info['ref']}@classichealth.cm",
        f"DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}", f"DTSTART:{debut}", f"DTEND:{fin}",
        f"SUMMARY:Consultation - {r['medecin_nom']}",
        f"DESCRIPTION:{r['specialite']} - dossier {info['ref']}",
        "LOCATION:ClassicHealth Clinique Privée\\, Boulevard de la Liberté\\, Akwa\\, Douala",
        "STATUS:CONFIRMED", "END:VEVENT", "END:VCALENDAR",
    ]
    return Response("\r\n".join(lignes), mimetype="text/calendar",
                    headers={"Content-Disposition": f"attachment; filename=RDV_{info['ref']}.ics"})


# ---------------------------------------------------------------------
# Espace patient : « Mes consultations » (téléphone + date de naissance)
# ---------------------------------------------------------------------
LIBELLES_STATUT = {"prevu": "Passé", "effectue": "Effectué", "annule": "Annulé"}


def patient_connecte():
    pid = session.get("patient_id")
    if not pid:
        return None
    return get_db().execute("SELECT * FROM patients WHERE id = ?", (pid,)).fetchone()


def debut_rdv(r):
    return datetime.fromisoformat(f"{r['date']}T{r['heure']}")


@app.route("/mes-consultations")
def mes_consultations():
    patient = patient_connecte()
    a_venir, passes = [], []
    if patient:
        lignes = get_db().execute(
            """SELECT r.id, r.date, r.heure, r.motif, r.statut, r.date_prise, m.id AS medecin_id, m.nom AS medecin,
                      m.specialite FROM rendez_vous r JOIN medecins m ON m.id = r.medecin_id
               WHERE r.patient_id = ? ORDER BY r.date, r.heure""", (patient["id"],)).fetchall()
        maintenant = datetime.now()
        for r in lignes:
            jour = date.fromisoformat(r["date"])
            fiche = {**dict(r), "ref": reference(r["id"], r["date_prise"]), "date_longue": date_longue(jour),
                     "fin": heure_fin(r["heure"]), "initiales": initiales(r["medecin"])}
            if r["statut"] == "prevu" and debut_rdv(r) > maintenant:
                a_venir.append(fiche)
            else:
                fiche["libelle"] = LIBELLES_STATUT[r["statut"]]
                passes.append(fiche)
        passes.reverse()
    return render_template("mes_consultations.html", patient=patient, a_venir=a_venir, passes=passes,
                           telephone=telephone_lisible(patient["telephone"]) if patient else "",
                           erreur=None, aujourdhui=date.today().isoformat())


@app.route("/mes-consultations/connexion", methods=["POST"])
def mes_consultations_connexion():
    cle = f"patient:{request.remote_addr}"
    if securite.bloque(cle):
        message = "Trop de tentatives. Réessayez dans quelques minutes."
    else:
        tel = normaliser_telephone(request.form.get("telephone"))
        patient = get_db().execute("SELECT id FROM patients WHERE telephone = ? AND date_naissance = ?",
                                   (tel, request.form.get("date_naissance", ""))).fetchone() if tel else None
        if patient:
            securite.reussite(cle)
            session["patient_id"] = patient["id"]
            return redirect(url_for("mes_consultations"))
        securite.echec(cle)
        message = "Numéro ou date de naissance incorrect."
    return render_template("mes_consultations.html", patient=None, a_venir=[], passes=[], telephone="",
                           erreur=message, aujourdhui=date.today().isoformat()), 401


@app.route("/mes-consultations/deconnexion", methods=["POST"])
def mes_consultations_deconnexion():
    session.pop("patient_id", None)
    session.pop("dernier_rdv", None)
    return redirect(url_for("mes_consultations"))


def rdv_modifiable(rdv_id):
    """Retourne (patient, rendez-vous, None) ou (None, None, réponse d'erreur) pour annuler/déplacer."""
    patient = patient_connecte()
    if patient is None:
        return None, None, erreur(None, "Connectez-vous pour gérer vos rendez-vous.", 401)
    r = get_db().execute("SELECT * FROM rendez_vous WHERE id = ? AND patient_id = ?", (rdv_id, patient["id"])).fetchone()
    if r is None:
        return None, None, erreur(None, "Rendez-vous introuvable.", 404)
    if r["statut"] != "prevu" or debut_rdv(r) <= datetime.now():
        return None, None, erreur(None, "Ce rendez-vous ne peut plus être modifié.", 400)
    return patient, r, None


@app.route("/api/mes-rdv/<int:rdv_id>/annuler", methods=["POST"])
def api_annuler(rdv_id):
    _, r, err = rdv_modifiable(rdv_id)
    if err:
        return err
    db = get_db()
    with db:
        db.execute("UPDATE rendez_vous SET statut = 'annule' WHERE id = ?", (r["id"],))
    return jsonify(ok=True)


@app.route("/api/mes-rdv/<int:rdv_id>/deplacer", methods=["POST"])
def api_deplacer(rdv_id):
    patient, r, err = rdv_modifiable(rdv_id)
    if err:
        return err
    d = request.get_json(silent=True) or {}
    medecin_id, jour, err = verifier_creneau(r["medecin_id"], d.get("date"), d.get("heure"))
    if err:
        return erreur(*err)
    heure = d["heure"]
    if (jour.isoformat(), heure) == (r["date"], r["heure"]):
        return erreur("heure", "C'est déjà votre créneau actuel.")
    db = get_db()
    try:
        with db:  # nouveau créneau réservé et ancien libéré dans la même transaction
            reserver(db, patient["id"], medecin_id, jour, heure, r["motif"])
            db.execute("UPDATE rendez_vous SET statut = 'annule' WHERE id = ?", (r["id"],))
    except (CreneauPris, sqlite3.IntegrityError):
        return erreur("creneau", "Ce créneau vient d'être pris. Choisissez-en un autre.", 409)
    return jsonify(ok=True)


@app.template_filter("fr_date")
def fr_date(iso):
    """'2026-10-24' -> '24/10/2026'."""
    return f"{iso[8:10]}/{iso[5:7]}/{iso[:4]}" if iso else ""


if __name__ == "__main__":
    app.run(debug=True)
