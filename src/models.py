from datetime import datetime
from flask_login import UserMixin
from .app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(10), nullable=False, unique=True)
    birthdate = db.Column(db.Date, nullable=False)

    def __init__(self, userid=None, username=None, password=None, role=None, first_name=None, last_name=None, dni=None, birthdate=None):
        self.id = userid
        self.username = username
        self.password = password
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.dni = dni
        self.birthdate = birthdate

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Disponible')
    category_id = db.Column(db.Integer, db.ForeignKey('room_category.id'), nullable=False)
    category = db.relationship('RoomCategory', backref='rooms')
    name = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.String(200)) 

    def __init__(self, number, category_id, name, description, status):
        self.number = number
        self.category_id = category_id
        self.name = name
        self.description = description
        self.status =  status

    def __repr__(self):
        return f'<Room {self.number}>'


class RoomCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    max_capacity = db.Column(db.Integer, nullable=False) 
    
    def __init__(self, name, description, max_capacity):
        self.name = name
        self.description = description
        self.max_capacity = max_capacity

    def __repr__(self):
        return f'<RoomCategory {self.name}>'
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False , default='Activo')
    check_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship('Room', backref='reservations')
    cancellation = db.relationship('Cancellation', backref='reservation', uselist=False, cascade='all, delete-orphan')
    num_people = db.Column(db.Integer, nullable=False) 


    def __init__(self, user_id, check_in, check_out, room_id, num_people):
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.room_id = room_id
        self.num_people = num_people

    def __repr__(self):
        return f'<Reservation {self.id}>'

class Cancellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), unique=True, nullable=False)
    cancellation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)