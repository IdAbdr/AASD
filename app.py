"""Local research image-analysis web application."""
import csv
import io
import json
import sqlite3
import warnings
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, Response, abort, redirect, render_template, request, url_for
from PIL import Image, UnidentifiedImageError

from analysis import extract_features


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / 'research.db'),
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config['DATABASE']) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS analysis (
            id TEXT PRIMARY KEY, created_at TEXT NOT NULL, features TEXT NOT NULL
        )''')

    def records():
        with sqlite3.connect(app.config['DATABASE']) as db:
            rows = db.execute(
                'SELECT id, created_at, features FROM analysis ORDER BY created_at DESC'
            ).fetchall()
        return [dict(id=r[0], created_at=r[1], **json.loads(r[2])) for r in rows]

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.post('/upload')
    def upload():
        image = request.files.get('image')
        if image is None or not image.filename:
            return render_template('index.html', error='Select an image.'), 400
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                features = extract_features(image.stream)
        except (ValueError, OSError, UnidentifiedImageError,
                Image.DecompressionBombError, Image.DecompressionBombWarning):
            return render_template('index.html', error='Invalid image. Use JPEG/PNG up to 20 MP.'), 400
        record_id = uuid4().hex
        with sqlite3.connect(app.config['DATABASE']) as db:
            db.execute('INSERT INTO analysis VALUES (?, ?, ?)', (
                record_id, datetime.now(timezone.utc).isoformat(), json.dumps(features)
            ))
        return redirect(url_for('result', record_id=record_id))

    @app.get('/result/<record_id>')
    def result(record_id):
        with sqlite3.connect(app.config['DATABASE']) as db:
            row = db.execute(
                'SELECT created_at, features FROM analysis WHERE id = ?', (record_id,)
            ).fetchone()
        if row is None:
            abort(404)
        return render_template('result.html', data=json.loads(row[1]), created_at=row[0])

    @app.get('/history')
    def history():
        return render_template('history.html', data=records())

    @app.get('/export.csv')
    def export():
        output = io.StringIO(newline='')
        fields = ['id', 'created_at', 'analysis_version', 'width', 'height',
                  'mean_red', 'mean_green', 'mean_blue', 'brightness', 'contrast']
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records())
        return Response(output.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': 'attachment; filename=image_features.csv'
        })

    @app.errorhandler(413)
    def too_large(error):
        return render_template('index.html', error='Upload exceeds the 8 MB limit.'), 413

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', debug=False)
