from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
import logging
from .app import app, db  # Importa de manera relativa
from .forms import AddRoomForm, AddUserForm, DeleteRoomForm, DeleteUserForm, EditReservationForm, EditRoomForm, EditUserForm, RegistrationForm, LoginForm, ReservationForm, CancelReservationForm, ManageRoomForm
from .models import User, Room, RoomCategory, Reservation, Cancellation
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
# Configuración del registro de errores
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s: %(message)s')


# Ruta de inicio
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Usuario ya autenticado', 'info')
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('home'))  # Redirige a 'home' después del inicio de sesión
            else:
                flash('Contraseña incorrecta', 'danger')
                logging.error(f'Intento de inicio de sesión fallido para el usuario {form.username.data}')
        else:
            flash('Usuario no encontrado', 'danger')
            logging.error(f'Intento de inicio de sesión para un usuario no existente: {form.username.data}')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

# Ruta para el registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            role='guest',
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dni=form.dni.data,
            birthdate=form.birthdate.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# Rutas protegidas (requieren inicio de sesión)
# Rutas para administradores
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    # Calcular estadísticas generales
    total_users = User.query.count()
    total_rooms = Room.query.count()
    total_guests = db.session.query(db.func.sum(Reservation.num_people)).scalar() or 0
    total_reservations = Reservation.query.count()

    return render_template('dashboard.html', user=current_user,
                           total_users=total_users, total_rooms=total_rooms,total_guests=total_guests,
                           total_reservations=total_reservations)

#Rutas para Manejo de Usuarios
@app.route('/manage_users/view_users', methods=['GET'])
@login_required
def view_users():
    users = User.query.all()
    return render_template('manage_users/view_users.html', users=users)

@app.route('/manage_users/add_user', methods=['GET', 'POST'])
@login_required  # Assuming you have a login_required decorator for protecting routes
def add_user():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('index'))

    form = AddUserForm()

    if form.validate_on_submit():
        # Check if the username is already taken
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso. Por favor, elija otro.', 'danger')
        else:
            # Create a new user object and add it to the database
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                password= hashed_password,
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                dni=form.dni.data,
                birthdate=form.birthdate.data
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Usuario agregado exitosamente', 'success')
            return redirect(url_for('dashboard'))

    return render_template('manage_users/add_user.html', form=form)

@app.route('/manage_users/edit_user', methods=['GET', 'POST'])
@login_required  # Assuming you have a login_required decorator for protecting routes
def edit_user():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard'))

    form = EditUserForm()
    form.user_id.choices = [(user.id, f'{user.username} - {user.role}') for user in User.query.all()]  # Ajusta según tu modelo

    if form.validate_on_submit():
        user_id = form.user_id.data
        new_role = form.role.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        dni = form.dni.data
        birthdate = form.birthdate.data

        user = User.query.get(user_id)
        if user:
            user.role = new_role
            user.first_name = first_name
            user.last_name = last_name
            user.dni = dni
            user.birthdate = birthdate

            db.session.commit()
            flash(f'Usuario {user.username} actualizado con éxito', 'success')
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('manage_users/edit_user.html', form=form)

@app.route('/manage_users/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUserForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        confirm_username = form.confirm_username.data

        user = User.query.get(user_id)
        if user and user.username == confirm_username:
            db.session.delete(user)
            db.session.commit()
            flash(f'Usuario {user.username} eliminado exitosamente', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error al eliminar el usuario. Verifica la información ingresada.', 'danger')

    return render_template('manage_users/delete_user.html', form=form)


# Rutas para habitaciones
@app.route('/rooms')
def list_rooms():
    rooms = Room.query.all()
    return render_template('rooms/list_rooms.html', rooms=rooms)

@app.route('/rooms/filter', methods=['POST'])
@login_required
def filter_rooms():
    status_filter = request.form.get('status')

    if current_user.role == 'admin':
        if status_filter == 'all':
            rooms = Room.query.all()
        else:
            rooms = Room.query.filter_by(status=status_filter).all()
        return render_template('rooms/list_rooms.html', rooms=rooms)
    elif current_user.role == 'guest':
        user_rooms = Room.query.filter_by(user_id=current_user.id, status=status_filter).all()
        return render_template('rooms/list_rooms.html', rooms=user_rooms)
    else:
        return redirect(url_for('home.html'))

@app.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard'))

    form = AddRoomForm()
    form.category.choices = [(category.id, category.name) for category in RoomCategory.query.all()]

    if form.validate_on_submit():
        new_room = Room(
            number=form.number.data,
            status=form.status.data,
            category_id=form.category.data,
            name=form.name.data,
            description=form.description.data
        )

        db.session.add(new_room)
        db.session.commit()

        flash(f'Habitación {new_room.number} añadida con éxito', 'success')
        return redirect(url_for('dashboard'))

    return render_template('rooms/add_room.html', form=form)

@app.route('/rooms/edit_room', methods=['GET', 'POST'])
@login_required
def edit_room():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard'))

    all_rooms = Room.query.all()
    form = EditRoomForm()

    # Rellenar las opciones de categoría
    form.category.choices = [(category.id, category.name) for category in RoomCategory.query.all()]

    # Rellenar las opciones de habitación
    form.room.choices = [(room.id, room.number) for room in all_rooms]

    if form.validate_on_submit():
        room_id = form.room.data
        room = Room.query.get_or_404(room_id)
        form.populate_obj(room)
        db.session.commit()
        flash(f'Habitación {room.number} actualizada con éxito', 'success')
        return redirect(url_for('dashboard'))

    return render_template('rooms/edit_room.html', form=form)

@app.route('/rooms/delete_room', methods=['GET', 'POST'])
@login_required
def delete_room():
    if current_user.role != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('dashboard'))

    form = DeleteRoomForm()

    # Filtrar habitaciones disponibles para eliminar
    available_rooms = Room.query.filter_by(status='Disponible').all()
    form.room.choices = [(room.id, room.number) for room in available_rooms]

    if form.validate_on_submit():
        room_id = form.room.data
        room = Room.query.get(room_id)

        if room:
            db.session.delete(room)
            db.session.commit()
            flash(f'Habitación {room.number} eliminada con éxito', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Habitación no encontrada', 'danger')

    return render_template('rooms/delete_room.html', form=form)


# Rutas para reservas
@app.route('/reservations/list')
@login_required
def list_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('reservations/list_reservations.html', reservations=reservations)

@app.route('/reservations/filter', methods=['GET', 'POST'])
@login_required
def filter_reservations():
    status_filter = None  # Inicializa la variable con un valor predeterminado
    reservations = None   # Inicializa reservations también

    try:
        if request.method == 'POST':
            status_filter = request.form.get('status')

            if current_user.role == 'admin':
                if status_filter == 'all':
                    reservations = Reservation.query.all()
                else:
                    reservations = Reservation.query.filter_by(status=status_filter).all()
            elif current_user.role == 'guest':
                if status_filter == 'all':
                    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
                else:
                    reservations = Reservation.query.filter_by(user_id=current_user.id, status=status_filter).all()
            else:
                return redirect(url_for('home'))

        if reservations is not None:
            if not reservations:
                flash('No reservations found.', 'info')
            
        return render_template('reservations/list_reservations.html', reservations=reservations)

    except SQLAlchemyError as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/reservations/book', methods=['GET', 'POST'])
@login_required
def book_reservation():
    form = ReservationForm()
    
    form.user_id.choices = [(user.id, user.username) for user in User.query.all()]
    form.room_id.choices = [(room.id, room.number) for room in Room.query.filter_by(status='Disponible').all()]

    if form.validate_on_submit():
        reservation = Reservation(
            user_id=form.user_id.data,
            room_id=form.room_id.data,
            check_in=form.check_in.data,
            check_out=form.check_out.data
        )

        db.session.add(reservation)
        db.session.commit()

        flash('Reserva realizada exitosamente', 'success')
        return redirect(url_for('list_reservations'))

    return render_template('reservations/book_reservation.html', form=form)

# Rutas para cancelar reservas
@app.route('/reservations/cancel', methods=['GET', 'POST'])
@login_required
def cancel_reservation():
    form = CancelReservationForm()
    form.reservation_id.choices = [(reservation.id, f'{reservation.room.number} - {reservation.check_in}') for reservation in Reservation.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        reservation = Reservation.query.get(form.reservation_id.data)
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            flash('Reserva cancelada exitosamente', 'success')
        else:
            flash('Reserva no encontrada', 'danger')

    return render_template('reservations/cancel_reservation.html', form=form)

@app.route('/reservations/edit', methods=['GET', 'POST'])
@login_required
def edit_reservation():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))

    form = EditReservationForm()
    guest = None  # Initialize guest outside the conditional block

    if form.validate_on_submit():
        reservation_id = form.reservation_id.data
        return redirect(url_for('reservations/edit_reservation', reservation_id=reservation_id))

    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        guest = User.query.get(reservation.user_id)
        form.reservation_id.choices = [(r.id, f'Room: {r.room.number}, Check-In: {r.check_in}') for r in guest.reservations]

        if form.validate_on_submit():
            room = Room.query.get(reservation.room_id)

            if room:
                reservation.room_id = form.reservation_id.data
                db.session.commit()

                flash('Reservation successfully edited', 'success')
                return redirect(url_for('list_reservations'))
            else:
                flash('Room not found', 'danger')

    return render_template('reservations/edit_reservation.html', form=form, guest=guest)


if __name__ == '__main__':
    app.run(debug=True)
