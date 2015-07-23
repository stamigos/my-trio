from wtforms import Form, StringField, BooleanField, validators


class RegistrationForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=35)])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired(u'You must accept our Terms of Service')])