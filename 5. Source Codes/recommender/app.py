from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

from apiv1 import blueprint as apiv1

app = Flask(__name__)
app.register_blueprint(apiv1)

if __name__ == '__main__':
    app.run(port=5001, debug=True, use_reloader=False)