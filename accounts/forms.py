from wtforms import Form, StringField, PasswordField, validators


class RegistrationForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password')