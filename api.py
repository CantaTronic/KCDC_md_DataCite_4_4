
import os
import json
import flask

PORT = 5001

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'UL7VRVFEoT8rbCq2LoHrOjEkufrGrfW2'
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

with open('experimental.json') as _f:
    EXPERIMENTAL_FILES = json.load(_f)
    EXPERIMENTAL_FILES_NAMES = set(i['name'] for i in EXPERIMENTAL_FILES)

@app.route('/experimental', methods=['GET'])
def experimental():
    return flask.jsonify(EXPERIMENTAL_FILES)

@app.route('/experimental/<string:filename>', methods=['GET'])
def get_md(filename):
    if filename not in EXPERIMENTAL_FILES_NAMES:
        flask.abort(404, f'File {filename} not available')
    with open(os.path.join('md_json', filename)) as _f:
        md = json.load(_f)
    return flask.jsonify(md)

if __name__ == '__main__':
    from gunicorn.app.base import Application
    class WSGIServer(Application):
        def __init__(self, app, **kwargs):
            self._app = app
            self._opt = kwargs
            super().__init__()
        def load_config(self):
            for key, value in self._opt.items():
                if key not in self.cfg.settings: continue
                if value is None: continue
                self.cfg.set(key.lower(), value)
        def load(self):
            return self._app
    WSGIServer(app, bind=f'127.0.0.1:{PORT}', workers=4, threads=100).run()
