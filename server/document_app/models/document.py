from document_app.extensions import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortid = db.Column(db.String(32), unique=True)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)

    uploaded_on = db.Column(db.DateTime, nullable=False)

    mimetype = db.Column(db.String(32), nullable=False)
    encoding = db.Column(db.String(32), nullable=True)
    filename = db.Column(db.Text, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref=db.backref('documents', lazy=True))

    def __repr__(self):
        return f'<Document(id={self.shortid}, name="{self.name}">'
