from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@db/main'
CORS(app)
db = SQLAlchemy(app)

class EmailTemplate(db.Model):
    __tablename__ = 'email-templates'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    db.UniqueConstraint(subject, body)


@app.route('/')
def index():
    return 'Hello'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')