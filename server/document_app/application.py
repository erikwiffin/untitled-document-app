# pylint: disable=missing-docstring
import os

from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Elasticsearch
app.config['ELASTICSEARCH_DATABASE_URI'] = os.getenv('ELASTICSEARCH_DATABASE_URI')


def create_app():
    from document_app import extensions
    from document_app.lib import filters
    from document_app.views.auth.views import BP as auth_blueprint
    from document_app.views.cli.views import BP as cli_blueprint
    from document_app.views.main.views import BP as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(cli_blueprint)
    app.register_blueprint(main_blueprint)

    extensions.db.init_app(app)
    extensions.es.init_app(app)
    extensions.login_manager.init_app(app)

    return app
