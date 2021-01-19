from pathlib import Path
import re

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from document_app.application import app
from document_app.extensions import db, es
from document_app.models.project import Project
from document_app.models.document import Document
from document_app.services.document import DocumentService


BP = Blueprint('main',
               __name__,
               template_folder='templates')


@BP.route('/')
def index():
    return render_template('main/index.jinja2')


@BP.route('/projects')
def projects():
    projects = Project.query.all()

    return render_template('main/projects.jinja2', projects=projects)


@BP.route('/projects/<project_id>')
def search(project_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    documents = []

    if request.args.get('q'):
        service = DocumentService()
        doc_ids = service.search(request.args, project)
        documents = Document.query.filter(Document.id.in_(doc_ids)).all()
    else:
        query = Document.query\
            .filter_by(project_id=project.id)\
            .order_by(Document.uploaded_on.desc())\

        if request.args.get('tags'):
            for tag in request.args.getlist('tags'):
                query = query.filter(Document.tags.contains(tag))

        documents = query.all()

    return render_template('main/project.jinja2',
                           project=project,
                           documents=documents,
                           query=request.args.get('q', ''))


@BP.route('/projects/<project_id>/docs/<doc_id>')
def doc(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()
    res_url = f'/projects/{ project.shortid }/res/{ document.shortid }'

    return render_template('main/document.jinja2', document=document, project=project, res_url=res_url)


@BP.route('/projects/<project_id>/docs/<doc_id>', methods=['POST'])
def update_doc(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()

    tags = [tag for tag in re.split(r'\W+', request.form['tags']) if tag]

    document.tags = tags

    db.session.commit()

    return redirect(f'/projects/{project_id}/docs/{doc_id}')


@BP.route('/projects/<project_id>/res/<doc_id>')
def res(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()
    path = Path(app.instance_path) / 'uploads' / f'{project_id}' / f'{doc_id}'

    return send_file(path,
                     mimetype=document.mimetype,
                     as_attachment='download' in request.args,
                     attachment_filename=document.filename)


@BP.route('/projects/<project_id>/upload', methods=['POST'])
def upload(project_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()

    return_to = f'/projects/{ project_id }'

    if 'document' not in request.files:
        flash('Missing file')
        return redirect(return_to)

    file = request.files['document']

    if file.filename == '':
        flash('Missing file')
        return redirect(return_to)

    filename = secure_filename(file.filename)

    service = DocumentService()

    document = service.handle_upload(file, filename, project)

    db.session.add(document)
    db.session.commit()

    return redirect(return_to)
