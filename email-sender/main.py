from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@mysql-email_sender:3306/main'
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


@app.route('/')
def index():
    return render_template('temp-index.html', name='Test')

@app.route('/email-templates')
def templates():
    return 'Have fun'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')