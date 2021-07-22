from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from forms import MyForm
import os

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

db.create_all()

# test = EmailTemplate(title="Test", subject="Test Subject", body="Test body")
# db.session.add(test)
# db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/email-templates')
    return render_template('temp-index.html', name='Test', form=form)

@app.route('/email-templates')
def templates():
    return 'Have fun'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')