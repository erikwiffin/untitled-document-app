from datetime import datetime
import json
import mimetypes
from pathlib import Path

import click
from flask import Blueprint
import shortuuid
import textract
import yaml

from document_app.application import app
from document_app.extensions import db, es
from document_app.models.account import Account
from document_app.models.project import Project
from document_app.models.document import Document
from document_app.services.document import DocumentService


BP = Blueprint('cli', __name__)


@app.cli.command()
def initdb():
    ''' Initialize the database.
    '''
    db.create_all()


@app.cli.command()
def resetdb():
    ''' Reset the documents table.
    '''
    try:
        es.indices.delete('document')
    except:
        pass

    db.drop_all()
    db.create_all()

    path = Path(app.instance_path) / 'fixtures'

    with open(path / 'accounts.yml') as fh:
        data = yaml.safe_load(fh)

        for row in data:
            account = Account(**{k: row[k] for k in row if k not in ['password']})
            account.set_password(row['password'])
            db.session.add(account)
            click.echo(account)

    db.session.commit()

    with open(path / 'projects.yml') as fh:
        data = yaml.safe_load(fh)

        for row in data:
            project = Project(**{k: row[k] for k in row if k not in ['accounts']})
            project.shortid = shortuuid.uuid()
            project.accounts = [Account.query.get(id) for id in row['accounts']]
            db.session.add(project)
            click.echo(project)

    db.session.commit()


@app.cli.command()
@click.argument('username')
@click.argument('email')
def create_account(username, email):
    ''' Create an account.
    '''
    account = Account(username=username, email=email)

    db.session.add(account)
    db.session.commit()

    click.echo(account)


@app.cli.command()
@click.argument('name')
def create_project(name):
    ''' Create a project.
    '''
    project = Project(name=name)
    project.shortid = shortuuid.uuid()

    db.session.add(project)
    db.session.commit()

    click.echo(project)


@app.cli.command()
def list_projects():
    ''' List all projects.
    '''
    projects = Project.query.all()

    for project in projects:
        click.echo(project)


@app.cli.command()
@click.argument('project_id', metavar='<project>')
@click.argument('input_path', type=click.Path(exists=True), metavar='<input>')
def upload_document(project_id, input_path):
    ''' Upload a document.
    '''
    project = Project.query.filter_by(shortid=project_id).first()

    service = DocumentService()

    input_path = Path(input_path)
    with open(input_path, 'rb') as input_stream:
        document = service.handle_upload(input_stream, input_path.name, project)

    db.session.add(document)
    db.session.commit()

    click.echo(document)
    click.echo(document.text)
