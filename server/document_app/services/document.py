from datetime import datetime
#import mimetypes
from pathlib import Path

import filetype
import shortuuid
import textract
from werkzeug.datastructures import FileStorage

from document_app.application import app
from document_app.models.document import Document


class DocumentService:

    def handle_upload(self, input_stream, filename, project):
        input_path = Path(filename)
        id = shortuuid.uuid()

        # Put it somewhere useful
        path = Path(app.instance_path) / 'uploads' / project.shortid / id
        path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(input_stream, FileStorage):
            print(path)
            res = input_stream.save(path)
            print(res)
        else:
            with open(path, 'wb') as wh:
                wh.write(input_stream.read())

        # Figure out what it is
        kind = filetype.guess(str(path))
        #mimetype, encoding = mimetypes.guess_type(path)

        # Get the text out of it
        text = textract.process(path, extension='pdf', layout=True)

        # Create a Document
        document = Document()
        document.shortid = id
        document.name = input_path.stem
        document.project = project
        document.text = text.decode('utf-8')
        document.uploaded_on = datetime.utcnow()
        #document.mimetype = mimetype
        #document.encoding = encoding
        document.mimetype = kind.mime
        document.encoding = None
        document.filename = input_path.name

        return document
