from flask_sqlalchemy import SQLAlchemy

from document_app.lib.elasticsearch import ElasticsearchExtension



db = SQLAlchemy()
es = ElasticsearchExtension()
