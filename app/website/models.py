from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(500))
    image = db.Column(db.LargeBinary)
    is_active = db.Column(db.Boolean(), nullable=False, server_default='1')
    roles = db.relationship('Role', secondary='user_roles', backref='users')
    def has_roles(self, *role_names):
        role_names_set = set(role_names)
        user_roles = {role.name for role in self.roles}
        return bool(role_names_set & user_roles)






class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Role name
    label = db.Column(db.String(255), nullable=True) 



class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))

