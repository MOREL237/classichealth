# Accès à la base SQLite (une connexion par requête, clés étrangères toujours activées)
import os
import sqlite3
from pathlib import Path

from flask import g

DB = Path(os.environ.get("CLINIQUE_DB", Path(__file__).resolve().parent / "projet.db"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")  # exigé par schema.sql, à chaque connexion
    return g.db


def fermer_db(_erreur=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(fermer_db)
