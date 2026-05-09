from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    """
    Formulaire de connexion
    """
    email = StringField('Adresse e-mail', validators=[DataRequired(message="Ce champ est obligatoire"), Email(message="Adresse e-mail invalide")])
    password = PasswordField('Mot de passe', validators=[DataRequired(message="Ce champ est obligatoire")])
    submit = SubmitField('Connexion')


class UserForm(FlaskForm):
    """
    Formulaire de création/modification d'utilisateur (administrateur)
    """
    email = StringField('Adresse e-mail', validators=[DataRequired(message="Ce champ est obligatoire"), Email(message="Adresse e-mail invalide")])
    role = SelectField('Rôle', choices=[('admin', 'Administrateur'), ('user', 'Secrétaire')], validators=[DataRequired(message="Ce champ est obligatoire")])
    facility_location = SelectField('Localisation', 
        choices=[('', 'Sélectionnez un site'), ('Site 1', 'Site 1'), ('Site 2', 'Site 2'),
                 ('Site 3', 'Site 3'), ('Site 4', 'Site 4'), ('Site 5', 'Site 5')],
        validators=[DataRequired(message="Ce champ est obligatoire")])    
    password = PasswordField('Mot de passe', validators=[DataRequired(message="Ce champ est obligatoire"), Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères")])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message="Ce champ est obligatoire"),EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Enregistrer l\'utilisateur')

class CSRFOnlyForm(FlaskForm):
       pass
