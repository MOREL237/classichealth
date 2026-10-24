# Espace administrateur : connexion, tableau de bord, rendez-vous, patients
import csv
import io
from datetime import date, timedelta
from functools import wraps

from flask import Blueprint, Response, abort, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

import securite
from db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
PAR_PAGE = 20
STATUTS = {"prevu": "Prévu", "effectue": "Effectué", "annule": "Annulé"}


def admin_requis(vue):
    @wraps(vue)
    def enveloppe(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin.connexion", suivant=request.full_path.rstrip("?")))
        return vue(*args, **kwargs)
    return enveloppe


@admin_bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    suivant = request.values.get("suivant", "")
    if not suivant.startswith("/admin") or suivant.startswith("//"):
        suivant = url_for("admin.tableau_de_bord")
    if session.get("admin_id"):
        return redirect(suivant)
    erreur = None
    if request.method == "POST":
        cle = f"admin:{request.remote_addr}"
        if securite.bloque(cle):
            erreur = "Trop de tentatives. Réessayez dans quelques minutes."
        else:
            ligne = get_db().execute(
                "SELECT id, login, mot_de_passe_hash FROM administrateurs WHERE login = ?",
                (request.form.get("login", "").strip(),),
            ).fetchone()
            if ligne and check_password_hash(ligne["mot_de_passe_hash"], request.form.get("mot_de_passe", "")):
                securite.reussite(cle)
                session["admin_id"], session["admin_login"] = ligne["id"], ligne["login"]
                return redirect(suivant)
            securite.echec(cle)
            erreur = "Identifiant ou mot de passe incorrect."
    return render_template("admin/connexion.html", erreur=erreur, suivant=suivant), (401 if erreur else 200)


@admin_bp.route("/deconnexion", methods=["POST"])
def deconnexion():
    session.pop("admin_id", None)
    session.pop("admin_login", None)
    return redirect(url_for("admin.connexion"))


def semaines_patients(db, nombre=8):
    """Nouveaux patients par semaine (lundi -> dimanche) sur les dernières semaines."""
    lundi = date.today() - timedelta(days=date.today().weekday())
    sortie = []
    for i in range(nombre - 1, -1, -1):
        debut = lundi - timedelta(weeks=i)
        n = db.execute("SELECT COUNT(*) FROM patients WHERE date_creation BETWEEN ? AND ?",
                       (debut.isoformat(), (debut + timedelta(days=6)).isoformat())).fetchone()[0]
        sortie.append({"debut": debut, "n": n})
    return sortie


def en_pourcent(lignes, cle):
    maxi = max([l[cle] for l in lignes] + [1])
    for l in lignes:
        l["pct"] = round(100 * l[cle] / maxi)
    return lignes


@admin_bp.route("/")
@admin_requis
def tableau_de_bord():
    db = get_db()
    aujourdhui = date.today().isoformat()
    un = lambda sql, *p: db.execute(sql, p).fetchone()[0]
    total = un("SELECT COUNT(*) FROM rendez_vous")
    annules = un("SELECT COUNT(*) FROM rendez_vous WHERE statut = 'annule'")
    chiffres = {
        "patients": un("SELECT COUNT(*) FROM patients"),
        "medecins": un("SELECT COUNT(*) FROM medecins"),
        "total": total,
        "aujourdhui": un("SELECT COUNT(*) FROM rendez_vous WHERE date = ? AND statut != 'annule'", aujourdhui),
        "a_venir": un("SELECT COUNT(*) FROM rendez_vous WHERE date >= ? AND statut = 'prevu'", aujourdhui),
        "taux_annulation": round(100 * annules / total) if total else 0,
    }
    par_statut = [dict(l) for l in db.execute("SELECT statut, COUNT(*) AS n FROM rendez_vous GROUP BY statut")]
    par_statut = en_pourcent(sorted(par_statut, key=lambda l: ["prevu", "effectue", "annule"].index(l["statut"])), "n")
    par_specialite = en_pourcent([dict(l) for l in db.execute(
        """SELECT m.specialite AS nom, COUNT(*) AS n FROM rendez_vous r JOIN medecins m ON m.id = r.medecin_id
           WHERE r.statut != 'annule' GROUP BY m.specialite ORDER BY n DESC""")], "n")
    par_medecin = [dict(l) for l in db.execute(
        """SELECT m.nom, m.specialite,
                  SUM(r.statut = 'effectue') AS effectues, SUM(r.statut = 'prevu') AS prevus,
                  SUM(r.statut = 'annule') AS annules, COUNT(r.id) AS n
           FROM medecins m LEFT JOIN rendez_vous r ON r.medecin_id = m.id
           GROUP BY m.id ORDER BY n DESC""")]
    semaines = en_pourcent(semaines_patients(db), "n")
    du_jour = db.execute(
        """SELECT r.id, r.heure, r.statut, p.nom, p.prenom, p.telephone, m.nom AS medecin
           FROM rendez_vous r JOIN patients p ON p.id = r.patient_id JOIN medecins m ON m.id = r.medecin_id
           WHERE r.date = ? ORDER BY r.heure, m.nom""", (aujourdhui,)).fetchall()
    return render_template("admin/tableau_de_bord.html", c=chiffres, par_statut=par_statut, par_specialite=par_specialite,
                           par_medecin=par_medecin, semaines=semaines, du_jour=du_jour, statuts=STATUTS)


def filtrer_rendez_vous():
    """Construit la clause WHERE à partir des filtres de l'URL."""
    conditions, params = [], []
    q = request.args.get("q", "").strip()
    if q:
        conditions.append("(p.nom LIKE ? OR p.prenom LIKE ? OR p.telephone LIKE ?)")
        params += [f"%{q}%"] * 3
    if request.args.get("medecin", "").isdigit():
        conditions.append("r.medecin_id = ?")
        params.append(int(request.args["medecin"]))
    if request.args.get("statut") in STATUTS:
        conditions.append("r.statut = ?")
        params.append(request.args["statut"])
    for champ, signe in (("du", ">="), ("au", "<=")):
        try:
            conditions.append(f"r.date {signe} ?")
            params.append(date.fromisoformat(request.args.get(champ, "")).isoformat())
        except ValueError:
            conditions.pop()
    return (" WHERE " + " AND ".join(conditions)) if conditions else "", params


SELECT_RDV = """SELECT r.id, r.date, r.heure, r.motif, r.statut, p.id AS patient_id, p.nom, p.prenom, p.telephone,
                       m.nom AS medecin, m.specialite
                FROM rendez_vous r JOIN patients p ON p.id = r.patient_id JOIN medecins m ON m.id = r.medecin_id"""


@admin_bp.route("/rendez-vous")
@admin_requis
def rendez_vous():
    db = get_db()
    where, params = filtrer_rendez_vous()
    total = db.execute(f"SELECT COUNT(*) FROM rendez_vous r JOIN patients p ON p.id = r.patient_id{where}", params).fetchone()[0]
    pages = max(1, -(-total // PAR_PAGE))
    page = min(max(request.args.get("page", 1, type=int), 1), pages)
    lignes = db.execute(f"{SELECT_RDV}{where} ORDER BY r.date DESC, r.heure DESC LIMIT ? OFFSET ?",
                        params + [PAR_PAGE, (page - 1) * PAR_PAGE]).fetchall()
    medecins = db.execute("SELECT id, nom, specialite FROM medecins ORDER BY nom").fetchall()
    filtres = {k: v for k, v in request.args.items() if k != "page" and v}
    return render_template("admin/rendez_vous.html", lignes=lignes, medecins=medecins, total=total, page=page,
                           pages=pages, filtres=filtres, statuts=STATUTS)


@admin_bp.route("/rendez-vous.csv")
@admin_requis
def rendez_vous_csv():
    where, params = filtrer_rendez_vous()
    lignes = get_db().execute(f"{SELECT_RDV}{where} ORDER BY r.date, r.heure", params).fetchall()
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, delimiter=";")
    ecrivain.writerow(["id", "date", "heure", "patient", "telephone", "medecin", "specialite", "motif", "statut"])
    for l in lignes:
        ecrivain.writerow([l["id"], l["date"], l["heure"], f"{l['prenom']} {l['nom']}", l["telephone"],
                           l["medecin"], l["specialite"], l["motif"], l["statut"]])
    return Response("\ufeff" + sortie.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=rendez-vous.csv"})


@admin_bp.route("/api/rendez-vous/<int:rdv_id>/statut", methods=["POST"])
def changer_statut(rdv_id):
    if not session.get("admin_id"):
        return jsonify(erreur="Connexion requise."), 401
    statut = (request.get_json(silent=True) or {}).get("statut")
    if statut not in STATUTS:
        return jsonify(erreur="Statut invalide."), 400
    db = get_db()
    with db:
        n = db.execute("UPDATE rendez_vous SET statut = ? WHERE id = ?", (statut, rdv_id)).rowcount
    if n == 0:
        abort(404)
    return jsonify(ok=True, statut=statut, libelle=STATUTS[statut])


@admin_bp.route("/patients")
@admin_requis
def patients():
    db = get_db()
    q = request.args.get("q", "").strip()
    where, params = ("", [])
    if q:
        where, params = " WHERE p.nom LIKE ? OR p.prenom LIKE ? OR p.telephone LIKE ? OR p.ville LIKE ?", [f"%{q}%"] * 4
    total = db.execute(f"SELECT COUNT(*) FROM patients p{where}", params).fetchone()[0]
    pages = max(1, -(-total // PAR_PAGE))
    page = min(max(request.args.get("page", 1, type=int), 1), pages)
    lignes = db.execute(
        f"""SELECT p.id, p.nom, p.prenom, p.telephone, p.date_naissance, p.ville, p.date_creation,
                   COUNT(r.id) AS nb_rdv, MAX(r.date) AS dernier_rdv
            FROM patients p LEFT JOIN rendez_vous r ON r.patient_id = p.id{where}
            GROUP BY p.id ORDER BY p.nom, p.prenom LIMIT ? OFFSET ?""",
        params + [PAR_PAGE, (page - 1) * PAR_PAGE]).fetchall()
    return render_template("admin/patients.html", lignes=lignes, q=q, total=total, page=page, pages=pages)
