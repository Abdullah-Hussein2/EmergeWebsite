from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from flask_user import roles_required
from .models import User, Role , Doctor
from . import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError


admindash = Blueprint("admindash", __name__)

# Users Dashboard
@admindash.route('/Users_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def Users_dashboard():
    roles = Role.query.all()  # Get all roles to display in tabs

    # Add logic to fetch users based on their roles
    for role in roles:
        role.users = User.query.filter(User.roles.any(id=role.id)).all()

    return render_template("Adminstartion/users_dashboard.html", roles=roles, current_user=current_user)

# Add Role to User
@admindash.route('/add_role_to_user', methods=['POST'])
@login_required
@roles_required('Admin')
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
@login_required
@roles_required('Admin')
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

        # Update basic user details
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.description = request.form['description']  # Update description

        # Handle roles
        role_ids = request.form.getlist('role_ids')  # Get the selected roles
        new_roles = Role.query.filter(Role.id.in_(role_ids)).all()  # Fetch roles based on selected IDs
        user.roles = new_roles  # Update user's roles

        # Handle password update (optional)
        new_password = request.form.get('password')  # Get the new password from the form
        if new_password:  # Check if the password field is not empty
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('Adminstartion/edit_user.html', user=user, roles=Role.query.all())
            else:
                user.password = generate_password_hash(new_password)  # Hash and update password

        # Handle image upload
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

    return render_template('Adminstartion/edit_user.html', user=user, roles=Role.query.all())

# Add User
@admindash.route('/add_user', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def add_user():
    if request.method == 'POST':
        # Retrieve form fields
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']
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
            phone_number=phone_number,
            description=description,
            image=image_binary
        )

        # Add selected roles to the user
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_user.roles.append(role)

        db.session.add(new_user)
        db.session.commit()

        # Check if the new user has the "Doctor" role
        doctor_role = Role.query.filter_by(name='Doctor').first()
        if doctor_role and doctor_role in new_user.roles:
            # Capture doctor-specific fields
            specialization = request.form.get('specialization') or request.form.get('new_specialization')
            available = request.form.get('available') == 'Yes'

            # Create a Doctor entry
            new_doctor = Doctor(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password),
                specialization=specialization,
                phone_number=phone_number,
                available=available
            )

            db.session.add(new_doctor)
            db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))

    # Query the 20 most common specializations
    most_common_specializations = db.session.query(
        Doctor.specialization, db.func.count(Doctor.specialization).label('count')
    ).group_by(Doctor.specialization).order_by(db.desc('count')).limit(20).all()

    specializations = [s[0] for s in most_common_specializations]  # Extract specialization names
    all_roles = Role.query.all()

    return render_template('Adminstartion/add_user.html', all_roles=all_roles, specializations=specializations)
# Display User Profile Image
@admindash.route('/view_user/<int:user_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.image:
        return Response(user.image, mimetype='image/jpeg')
    return "No image available", 404




@admindash.route('/Anlytics')
@login_required
@roles_required('Admin')
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
        'Adminstartion/Anlytics.html',
        total_users_count = total_users_count,
        active_users_count = active_users_count,
        roles_data = roles_data
    )


@admindash.route('/Doctors_dashboard', methods=['GET'])
@login_required
@roles_required('Admin')
def Doctors_dashboard():
    from collections import defaultdict

    # Fetch all doctors from the database
    doctors = Doctor.query.all()

    # Group doctors by specialization
    grouped_doctors = defaultdict(list)
    for doctor in doctors:
        grouped_doctors[doctor.specialization].append(doctor)

    return render_template("Adminstartion/doctors_dashboard.html", grouped_doctors=grouped_doctors,
                           current_user=current_user)