from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from flask_user import roles_required
from .models import User, Role , Doctor , Post
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
@roles_required('Admin')
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




# View User profile
@admindash.route('/view_user/<int:user_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def view_user(user_id):
    user = User.query.get_or_404(user_id)  # Fetch user by ID
    roles = user.roles  # Get associated roles
    return render_template('Adminstartion/user_profile.html', user=user, roles=roles)







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






@admindash.route("/edit_doctor/<int:doctor_id>", methods=["GET", "POST"])
@login_required
@roles_required('Admin')
def edit_doctor(doctor_id):
    # Get the doctor record by ID
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        # Retrieve form data from request
        doctor.first_name = request.form.get('first_name', '').strip()
        doctor.last_name = request.form.get('last_name', '').strip()
        doctor.email = request.form.get('email', '').strip()
        doctor.specialization = request.form.get('specialization', '').strip()
        doctor.featured = (request.form.get('featured') == 'True')  # Convert to boolean
        doctor.description = request.form.get('description', '').strip()

        # Handle file upload
        image = request.files.get('image')
        if image:
            doctor.image = image.read()  # Save image data to database

        # Save the updated doctor information to the database
        try:
            db.session.commit()  # Commit changes
            flash("Doctor updated successfully!", "success")
            return redirect(url_for('admindash.Doctors_dashboard'))  # Redirect to dashboard
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            flash("An error occurred while updating the doctor.", "danger")

    # Fetch distinct specializations for the dropdown in the template
    specializations = (
        db.session.query(Doctor.specialization)
        .distinct()
        .order_by(Doctor.specialization)
        .all()
    )
    specializations = [s[0] for s in specializations]  # Convert to a list of values

    # Render the template, passing the doctor and dropdown options
    return render_template('Adminstartion/edit_doctor.html', doctor=doctor, specializations=specializations)





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
        available = request.form.get('available', 'No')
        role_ids = request.form.getlist('role_ids')  # Get selected roles
        image = request.files['image']
        image_binary = image.read() if image else None

        # Handle Specialization
        new_specialization = request.form.get('new_specialization', '').strip()
        existing_specialization = request.form.get('existing_specialization', '').strip()
        specialization = new_specialization if new_specialization else existing_specialization

        # Validate required fields
        if not (email and first_name and last_name and password and specialization):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admindash.add_doctor'))

        # Check if the email already exists
        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('A doctor with this email already exists.', 'danger')
            return redirect(url_for('admindash.add_doctor'))

        # Create a new Doctor record
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

        # Add roles to the doctor
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_doctor.roles.append(role)

        # Save the new doctor to the database
        db.session.add(new_doctor)
        try:
            db.session.commit()
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admindash.Doctors_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while adding the doctor.', 'danger')

    # Fetch specializations and roles for dropdowns
    most_common_specializations = db.session.query(
        Doctor.specialization, db.func.count(Doctor.specialization).label('count')
    ).group_by(Doctor.specialization).order_by(db.desc('count')).limit(20).all()
    specializations = [s[0] for s in most_common_specializations]
    roles = Role.query.all()  # Fetch all roles

    return render_template('Adminstartion/add_doctor.html', roles=roles, specializations=specializations)



@admindash.route('/view_doctor_image/<int:doctor_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def view_doctor_image(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.image:
        return Response(doctor.image, mimetype='image/jpeg')
    return "No image available", 404


@admindash.route('/doctor_profile/<int:doctor_id>', methods=['GET'])
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    page = request.args.get('page', 1, type=int)  # Get the current page from query parameters; default is 1
    posts = Post.query.filter_by(doctor_id=doctor_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5,
                                                                                                 error_out=False)
    return render_template('Auth/doctor_profile.html', doctor=doctor, posts=posts)

@admindash.route('/doctor_analytics', methods=['GET'])
@login_required
@roles_required('Admin')
def doctor_analytics():
    # Query database for specializations and doctor counts
    specializations_data = (
        db.session.query(
            Doctor.specialization,
            func.count(Doctor.id).label('count')
        )
        .group_by(Doctor.specialization)
        .order_by(func.count(Doctor.id).desc())
        .all()
    )

    # Convert the query results into a list of dictionaries
    specializations = [{'name': spec[0], 'count': spec[1]} for spec in specializations_data]

    # Pass to the template
    return render_template('Adminstartion/doctor_analytics.html', specializations=specializations)



@admindash.route('/search_doctors', methods=['GET'])
@login_required
@roles_required('Admin')
def search_doctors():
    query = request.args.get('q', '')  # Get the search query from the request
    if not query:
        flash("Please enter a search term.", "info")
        return redirect(url_for('admindash.Doctors_dashboard'))  # Redirect if no query is entered

    # Perform the search using SQLAlchemy filters
    doctors = Doctor.query.filter(
        (Doctor.first_name.ilike(f'%{query}%')) |
        (Doctor.last_name.ilike(f'%{query}%')) |
        (Doctor.email.ilike(f'%{query}%')) |
        (Doctor.specialization.ilike(f'%{query}%')) |
        (Doctor.phone_number.ilike(f'%{query}%'))
    ).all()

    # Render a result page with the filtered doctors
    return render_template('Adminstartion/search_results.html', doctors=doctors, query=query)





@admindash.route('/add_post/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')  # Ensure only Admins can create posts
def add_post(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        # Get post data
        title = request.form['title']
        content = request.form['content']

        # Create and save new post
        new_post = Post(title=title, content=content, doctor_id=doctor_id)
        db.session.add(new_post)
        try:
            db.session.commit()
            flash('Post added successfully!', 'success')
            return redirect(url_for('admindash.doctor_profile', doctor_id=doctor_id))
        except:
            db.session.rollback()
            flash('An error occurred while adding the post.', 'danger')

    return render_template('Adminstartion/add_post.html', doctor=doctor)


@admindash.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    # Fetch the post by ID
    post = Post.query.get_or_404(post_id)  # Returns 404 if post does not exist
    return render_template('Adminstartion/view_post.html', post=post)

# Edit Post
@admindash.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        # Update post details
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('admindash.post_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while updating the post.', 'danger')

    return render_template('Adminstartion/edit_post.html', post=post)


# Delete Post
@admindash.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
@roles_required('Admin')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while deleting the post.', 'danger')

    return redirect(url_for('admindash.post_dashboard'))


# Post Dashboard (Admin Only) with Search
@admindash.route('/post_dashboard', methods=['GET'])
@login_required
@roles_required('Admin')
def post_dashboard():
    search_query = request.args.get('search', '').strip()  # Get search term from query string, default empty
    posts = Post.query  # Base query

    if search_query:
        # Filter posts by title, doctor's name, or date
        posts = posts.filter(
            Post.title.ilike(f"%{search_query}%") |  # Case-insensitive title match
            Post.doctor.first_name.ilike(f"%{search_query}%") |  # Doctor's first name
            Post.doctor.last_name.ilike(f"%{search_query}%") |  # Doctor's last name
            Post.date_posted.cast(String).ilike(f"%{search_query}%")  # Date as string
        )

    posts = posts.all()  # Execute the query
    return render_template('Adminstartion/post_dashboard.html', posts=posts, search_query=search_query)


@admindash.route('/update_config', methods=['POST'])
@login_required
@roles_required('Admin')
def update_config():
    doctor_limit = request.form.get('DOCTOR_LIMIT', '5')  # Default is 5
    config = SiteConfig.query.filter_by(key='DOCTOR_LIMIT').first()
    if config:
        config.value = doctor_limit
        db.session.commit()
    flash('Config updated successfully!', 'success')
    return redirect(url_for('admindash.doctor_analytics'))
