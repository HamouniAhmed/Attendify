from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class AttendanceCheckForm(FlaskForm):
    """Form for checking in/out by ID"""
    id_value = StringField('ID or Card Number', validators=[DataRequired()])
    facility_location = HiddenField('Facility Location', validators=[DataRequired()])
    submit = SubmitField('Process Attendance')


class VisitorRegistrationForm(FlaskForm):
    """Form for registering visitors"""
    visitor_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=128)])
    visit_purpose = StringField('Visit Purpose', validators=[DataRequired(), Length(min=3, max=256)])
    visit_host = StringField('Organization/Entity', validators=[DataRequired(), Length(min=2, max=128)])
    facility_location = SelectField('Facility Location', 
                                   choices=[('Site 1', 'Site 1'), 
                                           ('Site 2', 'Site 2'),
                                           ('Site 3', 'Site 3'),
                                           ('Site 4', 'Site 4'),
                                           ('Site 5', 'Site 5')],
                                   validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Register & Check In')


class SupplierAttendanceForm(FlaskForm):
    """Form for supplier attendance details when checking in"""
    presence_type = SelectField('Presence Type', 
                               choices=[('Visit', 'Visit'), 
                                       ('Intervention', 'Intervention')],
                               validators=[DataRequired()])
    department_visited = StringField('Department Visited', validators=[DataRequired()])
    person_visited = StringField('Person to Meet', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Confirm Check In')

