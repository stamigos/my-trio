from wtforms import Form, StringField, BooleanField, SelectField, validators


class RegistrationForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email(),
                                  validators.Length(min=6, max=320, message=u'Maximum email length is 320')])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired(u'You must accept our Terms of Service')])


DEFAULT_LANGUAGES = [("en", "English"), ("ru", "Russian"), ("ua", "Ukrainian")]


class ProfileForm(Form):
    first_name = StringField('First name')
    middle_name = StringField('Middle name')
    last_name = StringField('Last name')
    passport_code = StringField('Passport_code')
    default_lang = SelectField('Default_language', choices=DEFAULT_LANGUAGES)
