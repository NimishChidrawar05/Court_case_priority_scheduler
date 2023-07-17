from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, DateField, SubmitField
from wtforms.validators import InputRequired

class CaseInputForm(FlaskForm):
    caseFile = FileField("PDF"or"Chrome HTML Document", validators=[InputRequired()])
    filingDate= DateField("Date of Filing")
    petitioners = IntegerField("Number of Petitioners")
    respondents = IntegerField("Number of Respondents")
    submit = SubmitField("Submit")
    # makeBatch = SubmitField("Make Batch Now")
