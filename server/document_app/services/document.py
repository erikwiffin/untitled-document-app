from datetime import datetime
#import mimetypes
from pathlib import Path

import filetype
import shortuuid
import textract
from werkzeug.datastructures import FileStorage

from document_app.application import app
from document_app.extensions import es
from document_app.models.document import Document


class DocumentService:

    def extract_text(self, path):
        # Figure out what it is
        kind = filetype.guess(str(path))

        # Get the text out of it
        if kind.mime == 'application/pdf':
            text = textract.process(path, extension='pdf', layout=True, method='pdftotext').decode('utf-8')
            if not text.strip():
                text = textract.process(path, extension='pdf', method='tesseract').decode('utf-8')
        elif kind.mime == 'image/png':
            text = textract.process(path, extension='png').decode('utf-8')
        elif kind.mime == 'image/gif':
            text = textract.process(path, extension='gif').decode('utf-8')
        else:
            raise Exception(f'Unrecognized file format "{kind.mime}"')

        return kind, text


    def handle_upload(self, input_stream, filename, project):
        input_path = Path(filename)
        id = shortuuid.uuid()

        # Put it somewhere useful
        path = Path(app.instance_path) / 'uploads' / project.shortid / id
        path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(input_stream, FileStorage):
            res = input_stream.save(path)
        else:
            with open(path, 'wb') as wh:
                wh.write(input_stream.read())

        kind, text = self.extract_text(str(path))

        # Create a Document
        document = Document()
        document.shortid = id
        document.name = input_path.stem
        document.project = project
        document.text = text
        document.tags = []
        document.uploaded_on = datetime.utcnow()
        #document.mimetype = mimetype
        #document.encoding = encoding
        document.mimetype = kind.mime
        document.encoding = None
        document.filename = input_path.name

        return document

    def search(self, query, project):
        params = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                'text': {
                                    'query': query.get('q', ''),
                                },
                            },
                        },
                    ],
                    'filter': [
                        {
                            'term': {
                                'project_id': project.id,
                            },
                        },
                    ],
                },
            },
        }
        for tag in query.getlist('tags'):
            params['query']['bool']['filter'].append({
                'term': {
                    'tags': tag,
                },
            })

        results = es.search(
            index=['document'],
            body=params,
            filter_path=[
                'hits.hits._id',
                'hits.hits._score',
            ]
        )

        try:
            doc_ids = [hit['_id'] for hit in results['hits']['hits']]
        except KeyError:
            doc_ids = []

        return doc_ids
