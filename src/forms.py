from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, PasswordField, SubmitField, SelectField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, ValidationError
from wtforms.fields import DateField
from datetime import date


def validate_birthdate(form, field):
    today = date.today()
    age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
    if age < 18:
        raise ValidationError('Debes tener al menos 18 años para registrarte.')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    birthdate = DateField('Fecha de Nacimiento', validators=[DataRequired(), validate_birthdate])
    dni = StringField('DNI', validators=[DataRequired(), Length(min=7, max=10)])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
    
class AddRoomForm(FlaskForm):
    number = StringField('Número', validators=[DataRequired()])
    status = StringField('Estado') 
    category = SelectField('Categoría', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = StringField('Descripción')
    submit = SubmitField('Añadir')    
    
class EditRoomForm(FlaskForm):
    room = SelectField('Room', coerce=int)
    number = StringField('Número', validators=[DataRequired()])
    status = SelectField('Estado', choices=[('Disponible', 'Disponible'), ('Ocupado', 'Ocupado')], validators=[DataRequired()])
    category = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    submit = SubmitField('Actualizar')
    
class DeleteRoomForm(FlaskForm):
    room = SelectField('Selecciona una habitación', validators=[DataRequired()])
    submit = SubmitField('Eliminar')

class ReservationForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    room_id = SelectField('Room', coerce=int, validators=[DataRequired()])
    check_in = DateField('Check-In Date', format='%Y-%m-%d', validators=[DataRequired()])
    check_out = DateField('Check-Out Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Reservar')
    
class EditReservationForm(FlaskForm):
    DEFAULT_OPTION = (-1, 'No disponibles')
    reservation_id = SelectField('Select Reservation', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Edit Reservation')

    
class CancelReservationForm(FlaskForm):
    reservation_id = SelectField('Reserva a Cancelar', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cancelar Reserva')

class ManageRoomForm(FlaskForm):
    room_id = SelectField('Habitación', coerce=int, validators=[DataRequired()])
    new_status = SelectField('Nuevo Estado', choices=[('Disponible', 'Disponible'), ('Reservado', 'Reservado'), ('Inhabilitado', 'Inhabilitado')], validators=[DataRequired()])
    submit = SubmitField('Actualizar Estado')

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('guest', 'Guest')], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired(), Length(min=7, max=10)])
    birthdate = DateField('Birthdate', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Add User')

class EditUserForm(FlaskForm):
    user_id = SelectField('Select User', coerce=int, validators=[DataRequired()])
    role = SelectField('New Role', choices=[('admin', 'Admin'), ('guest', 'Guest')], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired(), Length(min=7, max=10)])
    birthdate = DateField('Birthdate', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Actualizar')

    
class DeleteUserForm(FlaskForm):
    user_id = SelectField('User ID', validators=[DataRequired()], coerce=int)
    confirm_username = StringField('Confirm User\'s Username', validators=[DataRequired()])
    confirm_delete = StringField('Confirm Deletion', validators=[DataRequired(), EqualTo('confirm_text', message='Confirmation text must be "DELETE"')])
    submit = SubmitField('Delete User')
