# app/forms/supplier_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from flask_wtf.file import FileAllowed

class SupplierForm(FlaskForm):
    manual_id = StringField("ID manuel", validators=[DataRequired(message="Ce champ est obligatoire"), Length(max=64)])
    rfid_uid = StringField("UID RFID (Facultatif)", validators=[Optional(), Length(max=64)])
    first_name = StringField("Prénom", validators=[DataRequired(message="Ce champ est obligatoire"), Length(max=64)])
    last_name = StringField("Nom", validators=[DataRequired(message="Ce champ est obligatoire"), Length(max=64)])
    company = StringField("Entreprise", validators=[DataRequired(message="Ce champ est obligatoire"), Length(max=128)])
    cin = StringField("CIN", validators=[
        DataRequired(message="Ce champ est obligatoire"),
        Length(max=64),
        Regexp('^[A-Za-z0-9]+$', message="Le CIN ne doit contenir que des lettres et des chiffres.")
    ])
    chef_name = StringField("Nom du chef (Facultatif)", validators=[Optional(), Length(max=128)])
    chef_number = StringField("Numéro du chef (Facultatif)", validators=[Optional(), Length(max=64)])
    cnss = StringField("CNSS (Facultatif)", validators=[Optional(), Length(max=64)])
    facility_location = StringField("Emplacement", validators=[DataRequired(message="Ce champ est obligatoire"), Length(max=128)])
    picture = FileField("Photo (Facultatif)", validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], "Uniquement des images (jpg, png, jpeg)")
    ])
    is_active = BooleanField("Actif", default=True)
    submit = SubmitField("Enregistrer le fournisseur")
