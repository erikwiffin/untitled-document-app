from document_app.extensions import db

project_account_map = db.Table(
    'project_account_map',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('account_id', db.Integer, db.ForeignKey('account.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortid = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)

    accounts = db.relationship('Account', secondary=project_account_map, lazy='subquery', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f'<Project(id={self.shortid}, name="{self.name}">'
