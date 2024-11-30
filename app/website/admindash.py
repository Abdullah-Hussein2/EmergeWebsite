from flask import Blueprint, render_template , redirect , url_for, flash
from flask_login import login_required , current_user
from .models import User, Role
from flask_user import roles_required
from . import db

admindash = Blueprint("admindash", __name__)

from flask import render_template, request, redirect, url_for, flash
from . import db
from .models import User, Role
from flask_login import login_required

@admindash.route('/Users_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def Users_dashboard():
    # Ensure that the user has the 'Admin' role
    if 'Admin' not in [role.name for role in current_user.roles]:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('views.home'))

    # Get the section from the query string or default to 'overview'
    section = request.args.get('section', 'overview')

    # Initialize the search term, if present in the query string
    search_term = request.args.get('search', '').strip()  # Default to an empty string if no search term

    # Fetch the roles
    roles = Role.query.all()

    # Fetch admins (users with the 'Admin' role)
    admins = User.query.filter(User.roles.any(name='Admin')).all()

    # If there's a search term, filter the users by name or email
    if search_term:
        admins = User.query.filter(
            (User.first_name.ilike(f"%{search_term}%")) |
            (User.last_name.ilike(f"%{search_term}%")) |
            (User.email.ilike(f"%{search_term}%"))
        ).all()

    # Pass the admins and their roles to the template
    return render_template("Users_dashboard.html", section=section, admins=admins, roles=roles, search_term=search_term)

@admindash.route("/dashboard")
@login_required
@roles_required('Admin')
def dashboard():
    total_users = User.query.count()
    return render_template("dashboard.html", total_user=total_users)



@admindash.route('/add_role_to_user', methods=['POST'])
@login_required
@roles_required('Admin')
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

    return redirect(url_for('admindash.Users_dashboard'))



@admindash.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@roles_required('Admin')
def delete_user(user_id):
    # Fetch the user by ID
    user = User.query.get(user_id)

    if user:
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')

    return redirect(url_for('admindash.Users_dashboard'))


@admindash.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_user(user_id):
    user = User.query.get(user_id)  # Retrieve the user by ID
    all_roles = Role.query.all()  # Fetch all roles

    if request.method == 'POST':
        # Get the form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_ids = request.form.getlist('role_id')  # Get selected role IDs

        # Update basic user info
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Update password if a new password is provided
        if password:
            user.set_password(password)  # Assuming you have a set_password method to hash the password

        # Update roles
        roles = Role.query.filter(Role.id.in_(role_ids)).all()  # Get the selected roles
        user.roles = roles  # Assign the roles to the user

        db.session.commit()

        return redirect(url_for('admindash.Users_dashboard'))

    return render_template('edit_user.html', user=user, all_roles=all_roles)
