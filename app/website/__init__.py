from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_user import UserManager

# Initialize db
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = "helloworld"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config['USER_ENABLE_EMAIL'] = False  # Disable email if not needed
    app.config['USER_APP_NAME'] = 'Emarge'  # Change app name as needed

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .admindash import admindash

    app.register_blueprint(admindash, url_prefix='')

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Role

    user_manager = UserManager(app, db, User)

    def setup_roles():
        roles = ['User', 'Admin', 'Poster' , 'Doctor']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name)
                db.session.add(new_role)
        db.session.commit()

    with app.app_context():
        # Ensure roles are set up and tables are created
        db.create_all()  # Create tables (if they don't exist)
        setup_roles()    # Add default roles if they don't exist

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
