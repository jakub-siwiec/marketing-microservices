from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_login import (
    LoginManager,
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

from forms import MyForm

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@mysql-email_sender:3306/main'
app.config['SECRET_KEY'] = SECRET_KEY

oauth = OAuth()
CORS(app)
db = SQLAlchemy(app)

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

@app.route('/login')
def login():
    return gmail.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    resp = gmail.authorized_response()
    print(resp)
    return redirect('/list')

@app.route('/list')
def index():
    email_templates = EmailTemplate.query.all()
    return render_template('temp-index.html', emailTemplates=email_templates)


@app.route('/', methods=['GET', 'POST'])
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