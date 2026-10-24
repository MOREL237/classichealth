# Protections communes : jeton CSRF sur tous les POST et limitation des tentatives de connexion
import secrets
import time

from flask import abort, jsonify, request, session

FENETRE = 600      # secondes
MAX_ECHECS = 5     # échecs autorisés par fenêtre et par clé
_echecs = {}


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def verifier_csrf():
    if request.method != "POST":
        return
    envoye = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    attendu = session.get("csrf", "")
    if not envoye or not attendu or not secrets.compare_digest(envoye.encode(), attendu.encode()):
        abort(400)


def bloque(cle):
    tentatives = [t for t in _echecs.get(cle, []) if time.time() - t < FENETRE]
    _echecs[cle] = tentatives
    return len(tentatives) >= MAX_ECHECS


def echec(cle):
    _echecs.setdefault(cle, []).append(time.time())


def reussite(cle):
    _echecs.pop(cle, None)


def init_app(app):
    app.before_request(verifier_csrf)
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.errorhandler(400)
    def mauvaise_requete(_e):
        message = "Session expirée ou requête invalide : rechargez la page."
        if request.path.startswith("/api") or "/api/" in request.path:
            return jsonify(champ=None, erreur=message), 400
        return message, 400
