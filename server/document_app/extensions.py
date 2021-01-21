from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from document_app.lib.elasticsearch import ElasticsearchExtension


db = SQLAlchemy()
es = ElasticsearchExtension()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
