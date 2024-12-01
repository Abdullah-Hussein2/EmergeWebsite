from flask import Blueprint, render_template , redirect , url_for, flash , Response , request
from flask_login import login_required , current_user
from .models import User, Role
from flask_user import roles_required
from . import db


# the blueprint
admindash = Blueprint("admindash", __name__)






#Users dash shows all the names of the users and admin and other roles

@admindash.route('/Users_dashboard', methods=['GET', 'POST'])
def Users_dashboard():
    if 'Admin' not in [role.name for role in current_user.roles]:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('views.home'))

    section = request.args.get('section', 'overview')

    search_term = request.args.get('search', '').strip()  # Default to an empty string if no search term

    roles = Role.query.all()

    admins = User.query.filter(User.roles.any(name='Admin')).all()

    if search_term:
        admins = User.query.filter(
            (User.first_name.ilike(f"%{search_term}%")) |
            (User.last_name.ilike(f"%{search_term}%")) |
            (User.email.ilike(f"%{search_term}%"))
        ).all()

    return render_template("Users_dashboard.html", section=section, admins=admins, roles=roles, search_term=search_term)





#TODO

@admindash.route("/dashboard")
def dashboard():
    total_users = User.query.count()
    return render_template("dashboard.html", total_user=total_users)






#Adding roles to useres (NOTE:defulte role is 'user')


@admindash.route('/add_role_to_user', methods=['POST'])
def add_role_to_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role_id = request.form.get('role_id')

        user = User.query.get(user_id)
        role = Role.query.get(role_id)

        if not user:
            print(f"User with ID {user_id} not found!")
        if not role:
            print(f"Role with ID {role_id} not found!")

        if user and role:
            print(f"User: {user.first_name} {user.last_name}, Role: {role.name}")


            user.roles = []
            user.roles.append(role)
            db.session.commit()

            flash('Role assigned successfully!', 'success')
        else:
            print(f"Invalid user or role. User: {user}, Role: {role}")
            flash('Invalid user or role!', 'danger')

    return redirect(url_for('admindash.Users_dashboard'))




#deleting users
@admindash.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')

    return redirect(url_for('admindash.Users_dashboard'))






#editing the information of the users
@admindash.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):

    user = User.query.get_or_404(user_id)


    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role_ids = request.form.getlist('role_ids')


        if password:
            user.set_password(password)

        user.first_name = first_name
        user.last_name = last_name
        user.email = email


        image = request.files.get('image')
        if image:
            user.image = image.read()


        user.roles.clear()
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)


        db.session.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))


    all_roles = Role.query.all()

    return render_template('edit_user.html', user=user, all_roles=all_roles)





#adding a user
@admindash.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role_ids = request.form.getlist('role_ids')


        image = request.files['image']
        image_binary = None
        if image:
            image_binary = image.read()

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            image=image_binary
        )

        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                new_user.roles.append(role)

        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!', 'success')
        return redirect(url_for('admindash.Users_dashboard'))

    all_roles = Role.query.all()

    return render_template('add_user.html', all_roles=all_roles)




# Display Image in a Template html code => <img src="{{ url_for('admindash.view_user', user_id=user.id) }}" alt="User Image">


#showing user profiles
@admindash.route('/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    user = User.query.get_or_404(user_id)

    # Return the image as a response in a format that the browser can display
    if user.image:
        return Response(user.image, mimetype='image/jpeg')  # Or image/png, depending on your image format
    else:
        return "No image available", 404
















def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
