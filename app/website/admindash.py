from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from .models import User, Role
from . import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError

# Blueprint definition
admindash = Blueprint("admindash", __name__)

# Users Dashboard
@admindash.route('/Users_dashboard', methods=['GET', 'POST'])
def Users_dashboard():
    if 'Admin' not in [role.name for role in current_user.roles]:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('views.home'))

    roles = Role.query.all()  # Get all roles to display in tabs
    # Add logic to fetch users based on their roles
    for role in roles:
        role.users = User.query.filter(User.roles.any(id=role.id)).all()

    return render_template("Users_dashboard.html", roles=roles, current_user=current_user)

# Add Role to User
@admindash.route('/add_role_to_user', methods=['POST'])
def add_role_to_user():
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    user = User.query.get(user_id)
    role = Role.query.get(role_id)

    if not user or not role:
        flash("User or Role not found!", "danger")
    else:
        # Update user roles
        user.roles = [role]
        db.session.commit()
        flash("Role assigned successfully!", "success")

    return redirect(url_for('admindash.Users_dashboard'))

# Delete User
@admindash.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        try:
            db.session.delete(user)  # Delete the user
            db.session.commit()
            flash('User deleted successfully!', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while deleting the user.', 'danger')
    else:
        flash('User not found!', 'danger')

    return redirect(url_for('admindash.Users_dashboard'))

# Edit User
@admindash.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)  # Get the user by ID

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.description = request.form['description']  # Update description

        # Handle roles
        role_ids = request.form.getlist('role_ids')  # Get the selected roles
        new_roles = Role.query.filter(Role.id.in_(role_ids)).all()  # Fetch roles based on selected IDs
        user.roles = new_roles  # Update user's roles

        # Handle image upload (optional)
        image = request.files['image']
        if image:
            user.image = image.read()

        try:
            db.session.commit()  # Commit changes to the database
            flash('User updated successfully!', 'success')
            return redirect(url_for('admindash.Users_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()  # Rollback if there is an error
            flash('An error occurred while updating the user.', 'danger')

    return render_template('edit_user.html', user=user, roles=Role.query.all())

# Add User
@admindash.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']  # Capturing phone number
        description = request.form['description']
        role_ids = request.form.getlist('role_ids')

        image = request.files['image']
        image_binary = image.read() if image else None

        # Create a new user object
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=generate_password_hash(password),
            phone_number=phone_number,  # Assigning phone number
            description=description,
            image=image_binary
        )

        # Add selected roles to the user
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_user.roles.append(role)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))

    all_roles = Role.query.all()
    return render_template('add_user.html', all_roles=all_roles)

# Display User Profile Image
@admindash.route('/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.image:
        return Response(user.image, mimetype='image/jpeg')
    return "No image available", 404




@admindash.route('/Anlytics')
def Anlytics():
# Query total users
    total_users_count = User.query.count()

    # Query active users
    active_users_count = User.query.filter_by(is_active=True).count()

    # Query roles and user counts for each role
    roles_data = []
    roles = Role.query.all()
    for role in roles:
        # Directly use len() on the InstrumentedList
        role_user_count = len(role.users)  # Get the length of the InstrumentedList
        roles_data.append({
            "name": role.name,
            "count": role_user_count
        })

    # Pass data to the template
    return render_template(
        'Anlytics.html',
        total_users_count=total_users_count,
        active_users_count=active_users_count,
        roles_data=roles_data
    )
