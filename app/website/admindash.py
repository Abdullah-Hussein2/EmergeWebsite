from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from flask_user import roles_required
from .models import User, Role , Doctor
from . import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func


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

        # Add roles to the user
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_user.roles.append(role)

        # Add and commit the new user
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))

    # Query specializations and all roles
    most_common_specializations = db.session.query(
        Doctor.specialization, db.func.count(Doctor.specialization).label('count')
    ).group_by(Doctor.specialization).order_by(db.desc('count')).limit(20).all()

    specializations = [s[0] for s in most_common_specializations]
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

    doctors = Doctor.query.all()
    grouped_doctors = defaultdict(list)
    for doctor in doctors:
        grouped_doctors[doctor.specialization].append(doctor)

    return render_template("Adminstartion/doctors_dashboard.html",
                           grouped_doctors=grouped_doctors, current_user=current_user)





@admindash.route('/doctor_profile/<int:doctor_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('Adminstartion/doctor_profile.html', doctor=doctor)







@admindash.route("/edit_doctor/<int:doctor_id>", methods=["GET", "POST"])
@login_required
@roles_required('Admin')
def edit_doctor(doctor_id):
    # Fetch the doctor from the database
    doctor = Doctor.query.get_or_404(doctor_id)  # Get the doctor by ID

    if request.method == 'POST':
        specialization = request.form['specialization'] or request.form['new_specialization']
        doctor.specialization = specialization
        # Commit changes to the database
        try:
            db.session.commit()  # Commit changes to the database
            flash('Doctor updated successfully!', 'success')
            return redirect(url_for('admindash.Doctors_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()  # Rollback if there is an error
            flash('An error occurred while updating the doctor.', 'danger')

    # Query specializations list
    most_common_specializations = db.session.query(
        Doctor.specialization, db.func.count(Doctor.specialization).label('count')
    ).group_by(Doctor.specialization).order_by(db.desc('count')).limit(20).all()

    specializations = [s[0] for s in most_common_specializations]

    return render_template('Adminstartion/edit_doctor.html', doctor=doctor, specializations=specializations)






@admindash.route('/doctor_analytics', methods=['GET'])
@login_required
@roles_required('Admin')
def doctor_analytics():
    specializations_data = (
        db.session.query(
            Doctor.specialization,
            func.count(Doctor.id).label('count')
        )
        .group_by(Doctor.specialization)
        .order_by(func.count(Doctor.id).desc())
        .all()
    )

    specializations = [{'name': spec[0], 'count': spec[1]} for spec in specializations_data]

    return render_template('Adminstartion/doctor_analytics.html', specializations=specializations)




@admindash.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
@roles_required('Admin')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while deleting the doctor.', 'danger')

    return redirect(url_for('admindash.Doctors_dashboard'))


@admindash.route('/add_doctor', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def add_doctor():
    if request.method == 'POST':
        # Retrieve form fields
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        phone_number = request.form['phone_number']
        description = request.form['description']
        specialization = request.form['specialization']
        available = request.form.get('available', 'No')
        image = request.files['image']
        image_binary = image.read() if image else None

        if not (email and first_name and last_name and password and specialization):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admindash.add_doctor'))

        # Check if the email already exists in doctors
        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('A doctor with this email already exists.', 'danger')
            return redirect(url_for('admindash.add_doctor'))

        # Create a Doctor record
        new_doctor = Doctor(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=generate_password_hash(password),
            phone_number=phone_number,
            description=description,
            image=image_binary,
            specialization=specialization,
            available=available
        )
        db.session.add(new_doctor)

        try:
            db.session.commit()
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admindash.Doctors_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while adding the doctor.', 'danger')

    return render_template('Adminstartion/add_doctor.html')




@admindash.route('/doctor_profile/<int:doctor_id>', methods=['GET'])
def doctor_detail(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('Adminstartion/doctor_profile.html', doctor=doctor)

