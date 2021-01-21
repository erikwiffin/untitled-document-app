from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from document_app.application import app
from document_app.extensions import db, login_manager
from document_app.models.account import Account


BP = Blueprint('auth',
               __name__,
               url_prefix='/auth',
               template_folder='templates')


@BP.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.jinja2')


@BP.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    account = Account.query.filter_by(username=username).first()

    if not account:
        flash('Account not found.')
        return render_template('auth/login.jinja2')

    if not account.check_password(password):
        flash('Invalid password.')
        return render_template('auth/login.jinja2')

    login_user(account)

    return redirect(url_for('main.index'))



@BP.route('/register', methods=['GET'])
def register():
    return render_template('auth/register.jinja2')


@BP.route('/register', methods=['POST'])
def handle_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    password_check = request.form['password_check']

    account = Account()
    account.username = username
    account.email = email
    account.set_password(password)

    db.session.add(account)
    db.session.commit()

    login_user(account)

    return redirect(url_for('main.index'))


@BP.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@login_manager.user_loader
def load_account(username):
    return db.session.query(Account).filter_by(username=username).first()


def groups_required(*groups):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_a(*groups):
                raise Forbidden()
            return func(*args, **kwargs)

        return wrapper

    return decorator
