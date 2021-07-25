from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    id_field = HiddenField()
    title = StringField('Title', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Add/Update Record')