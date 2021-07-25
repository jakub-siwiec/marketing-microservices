from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from forms import MyForm

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@mysql-email_sender:3306/main'
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)
db = SQLAlchemy(app)

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

# test = EmailTemplate(title="Test", subject="Test Subject", body="Test body")
# db.session.add(test)
# db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def formsPage():
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

@app.route('/list')
def index():
    email_templates = EmailTemplate.query.all()
    return render_template('temp-index.html', name='Test', emailTemplates=email_templates)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')