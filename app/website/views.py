from flask import Blueprint , render_template , redirect ,url_for , Response , request , abort , flash
from flask_login import current_user, login_required
from flask_user import roles_required
from .models import User , Doctor , Appointment , Role
from . import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

views = Blueprint("views", __name__)



@views.route("/")
@views.route("/home")
def home():
    return render_template("Core/home.html", user=current_user)



@views.route("/posts")
@login_required
def posts():
    return render_template("posts.html" ,user=current_user)




@views.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    # Check if the current user is either the profile owner, an Admin, or has an appointment as a doctor with this user.
    if current_user.is_anonymous or (
            current_user.id != user_id
            and not current_user.has_roles('Admin')
            and not Appointment.query.filter_by(doctor_id=current_user.id, user_id=user_id).first()
    ):
        abort(403, description="Not authorized to view this profile")

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.phone_number = request.form.get('phone')
        user.description = request.form.get('description')
        image = request.files['image']
        if image:
            user.image = image.read()

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while updating the profile.', 'danger')

    return render_template('user_profile.html', user=user)

# Route to serve user image from database
@views.route('/user_image/<int:user_id>')
@login_required
@roles_required('Admin')
def user_image(user_id):
    user = User.query.get(user_id)
    if user and user.image:
        return Response(user.image, mimetype='image/jpeg')
    return "Image not found", 404
@views.errorhandler(403)
def forbidden_error(error):
    return render_template('Error/403.html'), 403


@views.route('/services')
def services():
    if not current_user.is_authenticated or not current_user.has_roles('Admin'):
        abort(403)
    return render_template('Core/services.html')


@views.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    # Fetch all doctors from the database
    doctors = Doctor.query.all()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        try:
            # Convert strings to date and time objects
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()  # Convert to date object
            time_obj = datetime.strptime(time_str, '%H:%M').time()  # Convert to time object
        except ValueError as e:
            flash('Invalid date or time format.', 'danger')
            return render_template('book_appointment.html', doctors=doctors)

        if doctor_id and date_obj and time_obj:
            try:
                new_appointment = Appointment(
                    user_id=current_user.id,
                    doctor_id=doctor_id,
                    date=date_obj,
                    time=time_obj
                )
                db.session.add(new_appointment)
                db.session.commit()
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('views.home'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('An error occurred while booking the appointment: {}'.format(e), 'danger')

    return render_template('book_appointment.html', doctors=doctors)

@views.route('/doctors')
@login_required
@roles_required('Admin')  # Or whichever roles should have access to this info
def view_doctors():
    doctors = User.query.join(User.roles).filter(Role.name == 'Doctor').all()
    return render_template('view_doctors.html', doctors=doctors)


@views.route('appointment')
def appointment():
    return render_template('appointments.html')