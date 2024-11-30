from flask import Blueprint, render_template , redirect , url_for, flash , Response
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
def dashboard():
    total_users = User.query.count()
    return render_template("dashboard.html", total_user=total_users)



@admindash.route('/add_role_to_user', methods=['POST'])
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
def edit_user(user_id):
    # Fetch the user from the database
    user = User.query.get_or_404(user_id)

    # If the form is submitted via POST method
    if request.method == 'POST':
        # Get the form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role_ids = request.form.getlist('role_ids')  # Get selected role IDs

        # Handle optional password update (Hash the password if it's being updated)
        if password:
            user.set_password(password)  # Make sure to hash the password (use a method like set_password)

        # Update the user information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Handle image upload (optional)
        image = request.files.get('image')
        if image:
            user.image = image.read()  # Store the image as binary (or use a path to save it on disk)

        # Assign roles
        user.roles.clear()  # Clear existing roles
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        # Save the changes to the database
        db.session.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))  # Redirect to users dashboard

    # Fetch all roles for the select input
    all_roles = Role.query.all()

    return render_template('edit_user.html', user=user, all_roles=all_roles)

@admindash.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role_ids = request.form.getlist('role_ids')  # Get the selected role IDs

        # Handle image upload
        image = request.files['image']
        image_binary = None
        if image:
            image_binary = image.read()  # Read image as binary data

        # Create new user instance
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,  # You should hash the password before saving
            image=image_binary
        )

        # Assign roles
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_user.roles.append(role)

        # Save the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))  # Redirect to users dashboard

    # Retrieve all roles to populate the dropdown
    all_roles = Role.query.all()

    return render_template('add_user.html', all_roles=all_roles)


@admindash.route('/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    user = User.query.get_or_404(user_id)

    # Return the image as a response in a format that the browser can display
    if user.image:
        return Response(user.image, mimetype='image/jpeg')  # Or image/png, depending on your image format
    else:
        return "No image available", 404

# <img src="{{ url_for('admindash.view_user', user_id=user.id) }}" alt="User Image"> Display Image in a Template
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
