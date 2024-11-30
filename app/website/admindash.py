from flask import Blueprint, render_template , redirect , url_for, flash
from flask_login import login_required
from .models import User, Role
from . import db

admindash = Blueprint("admindash", __name__)

from flask import render_template, request, redirect, url_for, flash
from . import db
from .models import User, Role
from flask_login import login_required

@admindash.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    search_query = request.args.get('search')  # Get the search term from the query string
    if search_query:
        # If a search query is provided, filter users based on the query (name or email)
        users = User.query.filter(
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        ).all()
    else:
        # If no search query, get all users
        users = User.query.all()

    all_roles = Role.query.all()  # Get all roles
    return render_template("admin_dashboard.html", user=users, all_roles=all_roles)





@admindash.route('/add_role_to_user', methods=['POST'])
@login_required
def add_role_to_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role_id = request.form.get('role_id')

        # Debugging output
        print(f"Received user_id: {user_id}, role_id: {role_id}")

        # Ensure both user and role exist
        user = User.query.get(user_id)
        role = Role.query.get(role_id)

        if not user:
            print(f"User with ID {user_id} not found!")
        if not role:
            print(f"Role with ID {role_id} not found!")

        if user and role:
            # Debugging output
            print(f"User: {user.first_name} {user.last_name}, Role: {role.name}")

            # Clear existing roles before adding new one
            user.roles = []  # Optional: Clear previous roles
            user.roles.append(role)
            db.session.commit()

            flash('Role assigned successfully!', 'success')
        else:
            print(f"Invalid user or role. User: {user}, Role: {role}")
            flash('Invalid user or role!', 'danger')

    return redirect(url_for('admindash.admin_dashboard'))
