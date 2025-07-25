import os
import uuid
import zipfile
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'workspaces'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

ALLOWED_EXTENSIONS = {'zip'}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Workspace, Record, Screenshot

# Hilfsfunktionen

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_workspace_dir(workspace_id):
    path = os.path.join(app.config['UPLOAD_FOLDER'], workspace_id)
    os.makedirs(path, exist_ok=True)
    return path

# Routen
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt!')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Ungültige Datei! Bitte ZIP-Archiv hochladen.')
        return redirect(url_for('index'))
    # Workspace anlegen
    workspace_id = str(uuid.uuid4())
    workspace_dir = create_workspace_dir(workspace_id)
    zip_path = os.path.join(workspace_dir, secure_filename(file.filename))
    file.save(zip_path)
    # Entpacken
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(workspace_dir)
    os.remove(zip_path)
    # CSV und Screenshots finden
    csv_file = None
    screenshots = []
    for fname in os.listdir(workspace_dir):
        if fname.lower().endswith('.csv'):
            csv_file = os.path.join(workspace_dir, fname)
        elif fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshots.append(fname)
    if not csv_file:
        shutil.rmtree(workspace_dir)
        flash('Keine CSV-Datei im ZIP gefunden!')
        return redirect(url_for('index'))
    # CSV in DB importieren
    df = pd.read_csv(csv_file)
    workspace = Workspace(id=workspace_id)
    db.session.add(workspace)
    db.session.commit()
    for _, row in df.iterrows():
        record = Record(workspace_id=workspace_id, data=row.to_dict())
        db.session.add(record)
    for s in screenshots:
        screenshot = Screenshot(workspace_id=workspace_id, filename=s)
        db.session.add(screenshot)
    db.session.commit()
    return redirect(url_for('workspace', workspace_id=workspace_id))

@app.route('/workspace/<workspace_id>', methods=['GET', 'POST'])
def workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if workspace.password_hash and 'auth_'+workspace_id not in session:
        return redirect(url_for('auth_workspace', workspace_id=workspace_id))
    records = Record.query.filter_by(workspace_id=workspace_id).all()
    screenshots = Screenshot.query.filter_by(workspace_id=workspace_id).all()
    columns = []
    if records:
        columns = list(records[0].data.keys())
    return render_template('workspace.html', workspace=workspace, records=records, screenshots=screenshots, columns=columns)

@app.route('/workspace/<workspace_id>/set_password', methods=['POST'])
def set_password(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if workspace.password_hash:
        abort(403)
    password = request.form.get('password')
    if not password or len(password) < 4:
        flash('Passwort zu kurz!')
        return redirect(url_for('workspace', workspace_id=workspace_id))
    workspace.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.commit()
    flash('Passwort gesetzt! Speichern Sie den Link und das Passwort.')
    return redirect(url_for('workspace', workspace_id=workspace_id))

@app.route('/workspace/<workspace_id>/auth', methods=['GET', 'POST'])
def auth_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if request.method == 'POST':
        password = request.form.get('password')
        if workspace.password_hash and bcrypt.check_password_hash(workspace.password_hash, password):
            session['auth_'+workspace_id] = True
            return redirect(url_for('workspace', workspace_id=workspace_id))
        else:
            flash('Falsches Passwort!')
    return render_template('auth.html', workspace=workspace)

@app.route('/workspaces/<workspace_id>/screenshots/<filename>')
def serve_screenshot(workspace_id, filename):
    workspace_dir = os.path.join(app.config['UPLOAD_FOLDER'], workspace_id)
    return send_from_directory(workspace_dir, filename)

# API für CRUD, Filter, Suche, Graphen etc. folgt in weiteren Schritten

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)