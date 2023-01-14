from flask import Flask, request, send_file
from sys import gettrace
from gevent import pywsgi
import logging
import time

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

count = 0


@app.route('/upload', methods=['POST'])
def upload():
  app.logger.info('upload')
  file = request.files.get('file')
  file.save(f'photos/{time.strftime("%Y-%m-%d %H %M %S")} [{count}].png')


@app.route('/')
def index():
  return send_file('index.html')


if __name__ == '__main__':
  app.logger.info('started')
  if gettrace():  # check whether program is running under debug mode
    app.run(host='0.0.0.0')
  else:
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
