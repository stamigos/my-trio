from wtforms import Form, StringField, validators


class RegistrationForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=35)])