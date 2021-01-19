from sqlalchemy import event
from sqlalchemy.types import JSON

from document_app.extensions import db, es

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortid = db.Column(db.String(32), unique=True)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)

    uploaded_on = db.Column(db.DateTime, nullable=False)

    mimetype = db.Column(db.String(32), nullable=False)
    encoding = db.Column(db.String(32), nullable=True)
    filename = db.Column(db.Text, nullable=False)

    tags = db.Column(JSON)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref=db.backref('documents', lazy=True))

    def __repr__(self):
        return f'<Document(id={self.shortid}, name="{self.name}">'


@event.listens_for(Document, 'after_insert')
def post_after_insert(mapper, connection, target: Document):
    repr = {
        'id': target.id,
        'shortid': target.shortid,
        'name': target.name,
        'text': target.text,
        'tags': target.tags,
        'uploaded_on': target.uploaded_on,
        'project_id': target.project_id,
    }

    es.index(index='document', id=target.id, body=repr)


@event.listens_for(Document, 'after_update')
def post_after_update(mapper, connection, target: Document):
    repr = {
        'id': target.id,
        'shortid': target.shortid,
        'name': target.name,
        'text': target.text,
        'tags': target.tags,
        'uploaded_on': target.uploaded_on,
        'project_id': target.project_id,
    }

    es.index(index='document', id=target.id, body=repr)
