from document_app.extensions import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortid = db.Column(db.String(32), unique=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Project(id={self.shortid}, name="{self.name}">'
