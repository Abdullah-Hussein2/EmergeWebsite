from flask import Blueprint , render_template , redirect ,url_for , Response , request , abort , flash
from flask_login import current_user, login_required
from flask_user import roles_required
from .models import User , Doctor
from flask import session

views = Blueprint("views", __name__)



@views.route("/")
@views.route("/home")
def home():
    # Featured doctors only
    internal_doctors = Doctor.query.filter_by(specialization='Internal', featured=True).limit(5).all()
    Dermatologist = Doctor.query.filter_by(specialization='Dermatologist', featured=True).limit(5).all()
    Endocrinologist = Doctor.query.filter_by(specialization='Endocrinologist', featured=True).limit(5).all()
    Orthopedic = Doctor.query.filter_by(specialization='Orthopedic', featured=True).limit(5).all()
    Cardiologist = Doctor.query.filter_by(specialization='Cardiologist', featured=True).limit(5).all()
    ophthalmologists = Doctor.query.filter_by(specialization='Ophthalmologist', featured=True).limit(5).all()

    return render_template(
        "Core/home.html",
        internal_doctors=internal_doctors,
        Dermatologist=Dermatologist,
        Endocrinologist=Endocrinologist,
        Orthopedic=Orthopedic,
        Cardiologist=Cardiologist,
        ophthalmologists=ophthalmologists
    )






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





@views.route('/doctors')
def view_doctors():
    doctors = Doctor.query.all()
    return render_template('Adminstartion/view_doctors.html', doctors=doctors)






@views.route('/doctor_image/<int:doctor_id>')
def doctor_image(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.image:
        return Response(doctor.image, mimetype='image/jpeg')
    return "Image not found", 404
