from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from app import db

class Workspace(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=True)
    # weitere Metadaten möglich

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'))
    data = db.Column(JSON)

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'))
    filename = db.Column(db.String(256))