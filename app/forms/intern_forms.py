# app/forms/intern_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from flask_wtf.file import FileAllowed

class InternForm(FlaskForm):
    manual_id = StringField('Manual ID', validators=[DataRequired(), Length(max=64)])
    rfid_uid = StringField('RFID UID (Facultatif)', validators=[Optional(), Length(max=64)])
    first_name = StringField('Prénom', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Nom', validators=[DataRequired(), Length(max=64)])
    # You might want to make intern_type a SelectField if there are predefined types
    intern_type = StringField('Type de stage ', validators=[DataRequired(message='Veuillez sélectionner un département.'), Length(max=64)])
    department = SelectField('Département',choices=[('' , 'Choisissez...'),
        ('HR', 'Ressources Humaines'),
        ('Production', 'Production'),
        ('Logistique', 'Logistique'),
        ('Qualité', 'Qualité'),
        ('Maintenance', 'Maintenance'),
        ('Ingénierie', 'Ingénierie'),
        ('IT', 'Informatique'),
        ('Finance', 'Finance')
], validators=[DataRequired()])
    cin = StringField('CIN', validators=[DataRequired(), Length(max=64), Regexp('^[A-Za-z0-9]+$', message='CIN must contain only letters and numbers.')])
    supervisor = StringField('Superviseur', validators=[DataRequired(), Length(max=128)])
    facility_location = StringField('Emplacement', validators=[DataRequired(), Length(max=128)])
    picture = FileField('Photo (Facultatif)', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    is_active = BooleanField(' Est actif', default=True)
    submit = SubmitField('Enregistrer le stagiaire')