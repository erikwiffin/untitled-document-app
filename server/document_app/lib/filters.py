from datetime import datetime
import json

import arrow
import jinja2

from document_app.application import app


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.template_filter('jsonify')
def jsonify_filter(target):
    return json.dumps(target)


@app.template_filter('humanize')
def humanize_filter(target):
    return arrow.get(target).humanize()