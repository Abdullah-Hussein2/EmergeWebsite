from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func






#making the db tablas (***DO NOT CHANGE WITHOUT CONTACTING "ABDULLAH")
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    is_active = db.Column(db.Boolean(), nullable=False, server_default='1')
    phone_number = db.Column(db.String(15), nullable=True)
    image = db.Column(db.LargeBinary)
    description = db.Column(db.String(1000))
    # relationship between the tables (users tables and roles tables)
    roles = db.relationship('Role', secondary='user_roles', backref='users', lazy='dynamic', passive_deletes=True)




    # checking if user has role (NOTE: every user will have a role on registering)
    def has_roles(self, *role_names):
        role_names_set = set(role_names)
        user_roles = {role.name for role in self.roles}
        return bool(role_names_set & user_roles)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(255), nullable=True)



class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))



class DoctorRoles(db.Model):
    __tablename__ = 'doctor_roles'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))





class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(10000))
    image = db.Column(db.LargeBinary)
    phone_number = db.Column(db.String(15), nullable=True)
    specialization = db.Column(db.String(100), nullable=False)
    available = db.Column(db.String(100), nullable=False)
    roles = db.relationship('Role', secondary='doctor_roles', backref='doctors', lazy='dynamic', passive_deletes=True)
