from flask import Flask, flash, redirect, render_template, request, session
from flask.helpers import url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from decouple import config
import requests
import base64


from forms import MyForm

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@mysql-email_sender:3306/main'
app.config['SECRET_KEY'] = SECRET_KEY

oauth = OAuth()
CORS(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

gmail = oauth.remote_app('gmail', 
    register=True,
    consumer_key=config('GMAIL_CONSUMER_KEY'),
    consumer_secret=config('GMAIL_CONSUMER_SECRET'),
    authorize_url=config('GMAIL_AUTHORIZE_URL'),
    access_token_url=config('GMAIL_ACCESS_TOKEN_URL'),
    request_token_params={
        "redirect_uris": config('GMAIL_REDIRECT_URIS'),
        "project_id": config('GMAIL_PROJECT_ID'),
        "auth_provider_x509_cert_url": config('GMAIL_AUTH_PROVIDER_X509_CERT_URL'),
        "scope": config('GMAIL_SCOPE')
    }
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)

    def __init__(self, email):
        self.email = email


class EmailTemplate(db.Model):
    __tablename__ = 'emailTemplates'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(254), unique=True, nullable=False)
    subject = db.Column(db.String(254), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    db.UniqueConstraint(subject, body)

    def __init__(self, title, subject, body):
        self.title = title
        self.subject = subject
        self.body = body

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login')
def login():
    return gmail.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    resp = gmail.authorized_response()
    access_token_auth = resp['access_token']
    resp_get_profile = requests.get("https://www.googleapis.com/gmail/v1/users/me/profile", headers={"Authorization": "Bearer " + access_token_auth}).json()
    email_auth = resp_get_profile['emailAddress']
    user = User.query.filter_by(email=email_auth).first()
    if user == None:
        new_user = User(email=email_auth)
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(email=email_auth).first()
    session['refresh-token'] = resp['refresh_token']
    session['access-token'] = access_token_auth
    session['email'] = email_auth
    login_user(user)
    print(session.get('email'), flush=True)
    return redirect('/list')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('refresh-token', None)
    session.pop('access-token', None)
    session.pop('email', None)
    return redirect(url_for("index"))

@app.route('/list')
def index():
    email_templates = EmailTemplate.query.all()
    return render_template('temp-index.html', emailTemplates=email_templates)


@app.route('/', methods=['GET', 'POST'])
@login_required
def addTemplate():
    form = MyForm()
    if form.validate_on_submit():
        try:
            newTemplate = EmailTemplate(title=form.title.data, subject=form.subject.data, body=form.body.data)
            db.session.add(newTemplate)
            db.session.commit()
            return redirect('/list')
        except:
            return f'''<h1>Error</h1>'''
        
    return render_template('temp-form.html', form=form)

@app.route('/<template_id>', methods=['GET', 'POST'])
@login_required
def updateTemplate(template_id):
    template = EmailTemplate.query.filter_by(id=template_id).first()
    form = MyForm()
    if request.method == "GET":
        form.title.data = template.title
        form.subject.data = template.subject
        form.body.data = template.body
        return render_template('temp-form.html', template=template, form=form)
    elif request.method == "POST":
        try:
            template.title = form.title.data
            template.subject = form.subject.data
            template.body = form.body.data
            db.session.commit()
            return redirect('/list')
        except:
            return f'''<h1>Error</h1>'''

@app.route('/<template_id>/delete', methods=['POST'])
@login_required
def deleteTemplate(template_id):
    try:
        template = EmailTemplate.query.filter_by(id=template_id)
        template.delete()
        db.session.commit()
        email_templates = EmailTemplate.query.all()
        return render_template('temp-deleted.html', emailTemplates=email_templates)
    except:
        return f'''<h1>Error</h1>'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')