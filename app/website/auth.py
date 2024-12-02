from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User, Role
from flask_login import login_user, logout_user, login_required, current_user , login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin
import re


auth = Blueprint("auth", __name__)

# Login route
@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If the user is already logged in, redirect to the home page or dashboard
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('Password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email is incorrect or doesn\'t exist.', category='error')

    return render_template("Auth/login.html", user=current_user)


# Signup route
@auth.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        # Redirect logged-in users
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('Phone_number')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')

        # Input validation
        if not email or not first_name or not last_name or not phone_number or not password1 or not password2:
            flash('All fields are required.', category='error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address.', category='error')
        elif len(first_name) < 2 or len(last_name) < 2:
            flash('First and last name must be at least 2 characters long.', category='error')
        elif not re.match(r'^\d+$', phone_number):
            flash('Phone number must contain only digits.', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters long.', category='error')
        elif not any(char.isdigit() for char in password1):
            flash('Password must include at least one numeric character.', category='error')
        elif not any(char.isupper() for char in password1):
            flash('Password must include at least one uppercase letter.', category='error')
        elif not any(char.islower() for char in password1):
            flash('Password must include at least one lowercase letter.', category='error')
        elif User.query.filter_by(email=email).first():
            flash('Email is already in use.', category='error')
        else:

            # Create default role if it doesn't exist
            default_role = Role.query.filter_by(name='User').first()
            if not default_role:
                default_role = Role(name='User', label='Regular User')
                db.session.add(default_role)
                db.session.commit()


            # Create new user
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                is_active=True,
                password=generate_password_hash(password1)
            )

            # Assign default role to the user
            new_user.roles.append(default_role)
            db.session.add(new_user)
            db.session.commit()

            # Log the user in
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))  # Redirect to home or dashboard

    return render_template("Auth/signup.html", user=current_user)



# Logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))  # Redirect to home page after logout




class AnonymousUser(AnonymousUserMixin):
    def has_roles(self, *role_names):
        return False


login_manager.anonymous_user = AnonymousUser
