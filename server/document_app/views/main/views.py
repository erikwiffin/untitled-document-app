from pathlib import Path
import re

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
import shortuuid
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
@login_required
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.projects'))

    return render_template('main/index.jinja2')


@BP.route('/projects')
@login_required
def projects():
    projects = Project.query.filter(Project.accounts.contains(current_user)).all()

    return render_template('main/projects.jinja2', projects=projects)


@BP.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    project = Project()
    project.shortid = shortuuid.uuid()
    project.name = request.form['name']

    db.session.add(project)
    db.session.commit()

    return redirect(url_for('.projects'))


@BP.route('/projects/<project_id>')
@login_required
def project(project_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    documents = []

    service = DocumentService()
    doc_ids = service.search(request.args, project)
    documents = Document.query\
        .filter(Document.id.in_(doc_ids))\
        .order_by(Document.uploaded_on.desc())\
        .all()

    return render_template('main/project.jinja2',
                           project=project,
                           documents=documents,
                           query=request.args.get('q', ''))


@BP.route('/projects/<project_id>/docs/<doc_id>')
@login_required
def doc(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()
    res_url = f'/projects/{ project.shortid }/res/{ document.shortid }'

    return render_template('main/document.jinja2', document=document, project=project, res_url=res_url)


@BP.route('/projects/<project_id>/docs/<doc_id>', methods=['POST'])
@login_required
def update_doc(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()

    tags = [tag for tag in re.split(r'\W+', request.form['tags']) if tag]

    document.tags = tags

    db.session.commit()

    return redirect(url_for('.doc', project_id=project_id, doc_id=doc_id))


@BP.route('/projects/<project_id>/docs/<doc_id>/delete', methods=['POST'])
@login_required
def delete_doc(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()

    db.session.delete(document)
    db.session.commit()

    return redirect(url_for('.project', project_id=project_id))


@BP.route('/projects/<project_id>/res/<doc_id>')
@login_required
def res(project_id, doc_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()
    document = Document.query.filter_by(shortid=doc_id, project_id=project.id).first_or_404()
    path = Path(app.instance_path) / 'uploads' / f'{project_id}' / f'{doc_id}'

    return send_file(path,
                     mimetype=document.mimetype,
                     as_attachment='download' in request.args,
                     attachment_filename=document.filename)


@BP.route('/projects/<project_id>/upload', methods=['POST'])
@login_required
def upload(project_id):
    project = Project.query.filter_by(shortid=project_id).first_or_404()

    return_to = f'/projects/{ project_id }'

    def validate():
        if 'document' not in request.files:
            raise Exception('Missing file')

        file = request.files['document']

        if file.filename == '':
            raise Exception('Missing file')

        uploaded_on = request.form.get('uploadedOn')

        return file, uploaded_on

    try:
        file, uploaded_on = validate()
        filename = secure_filename(file.filename)

        service = DocumentService()

        document = service.handle_upload(file, filename, project, uploaded_on)

        db.session.add(document)
        db.session.commit()
    except Exception as error:
        if request.headers['Accept'] == 'application/json':
            return jsonify({
                'error': 'FileUploadError',
                'message': f'{error}',
            }), 422
        else:
            flash(error)
            return redirect(return_to)

    if request.headers['Accept'] == 'application/json':
        return jsonify({
            'Success': True,
            'URL': url_for('.doc', project_id=project_id, doc_id=document.shortid),
        })
    else:
        return redirect(return_to)
