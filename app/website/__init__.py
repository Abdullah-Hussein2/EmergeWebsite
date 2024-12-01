from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_user import UserManager
from flask_bcrypt import Bcrypt

# Initialize db and bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    # Configuration of the app
    app.config['SECRET_KEY'] = "helloworld"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config['USER_ENABLE_EMAIL'] = False
    app.config['USER_APP_NAME'] = 'Emarge'  # Change app name as needed

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .admindash import admindash

    app.register_blueprint(admindash, url_prefix='')
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Role

    # Initialize user_manager
    user_manager = UserManager(app, db, User)

    # Adding the roles
    def setup_roles():
        roles = ['User', 'Admin', 'Poster', 'Doctor']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name)
                db.session.add(new_role)
        db.session.commit()

    with app.app_context():
        # Ensure roles are set up and tables are created
        db.create_all()  # Create tables (if they don't exist)
        setup_roles()    # Add default roles if they don't exist

        # Create an admin user if it doesn't exist
        create_admin_user()

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

from .models import User, Role

def create_admin_user():

    # Check if there is already an admin user
    admin_role = Role.query.filter_by(name='Admin').first()
    if admin_role and not User.query.filter_by(email='ab@gmail.com').first():

        # Create an admin user
        admin_user = User(
            first_name="Admin",
            last_name="User",
            email="ab@gmail.com",
            password='123123'  # Store the hashed password
        )

        # Assign the admin role
        admin_user.roles.append(admin_role)

        try:
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            db.session.rollback()  # Rollback if there was an error
            print(f"Error creating admin user: {e}")
