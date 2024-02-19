# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/gestion_hotel'  # Update with your actual database URI
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'home'
login_manager.login_message_category = 'info'


from .routes import *
with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin')
        admin_user = User(
            username='admin',
            password= hashed_password,
            role='admin',
            first_name='Admin',
            last_name='User',
            dni='12345678',
            birthdate=datetime(1990, 1, 1)
        )
        db.session.add(admin_user)

    # Crea tres usuarios con rol 'guest' si no existen
    for i in range(1, 4):
        username = f'guest{i}'
        if not User.query.filter_by(username=username).first():
            hashed_password = bcrypt.generate_password_hash(f'password{i}')
            guest_user = User(
                username=username,
                password= hashed_password,
                role='guest',
                first_name=f'Guest{i}',
                last_name='User',
                dni=f'1234567{i}',
                birthdate=datetime(1990, 1, 1)
            )
            db.session.add(guest_user)

    db.session.commit()

    # Crea una categoría de habitación predeterminada si no existe
    default_category = RoomCategory.query.filter_by(name='Default').first()
    if not default_category:
        default_category = RoomCategory(
            name='Default',
            description='Default room category',
            max_capacity=2
        )
        db.session.add(default_category)
        db.session.commit()

    # Crea una habitación predeterminada si no existe
    default_room = Room.query.filter_by(number='101').first()
    if not default_room:
        default_room = Room(
            number='101',
            category_id=default_category.id,  # Ajusta según la relación en tu modelo
            name='Default Room',
            description='Default room description'
        )
        db.session.add(default_room)
        db.session.commit()

    db.session.commit()
    
    
if __name__ == '__main__':
    app.run(debug=True)
