from flask import Blueprint , render_template , redirect ,url_for , Response , request , abort , flash
from flask_login import current_user, login_required
from flask_user import roles_required
from .models import User , Doctor
from flask import session

views = Blueprint("views", __name__)



@views.route("/")
@views.route("/home")
def home():
    internal_doctors = Doctor.query.filter_by(specialization='Internal').limit(5).all()
    ophthalmologists = Doctor.query.filter_by(specialization='Ophthalmologist').limit(5).all()
    return render_template("Core/home.html", 
                           internal_doctors=internal_doctors, 
                           ophthalmologists=ophthalmologists)


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
@login_required
def view_doctors():
    doctors = Doctor.query.all()
    return render_template('Adminstartion/view_doctors.html', doctors=doctors)





@views.route('/services')
def services():
    if not current_user.is_authenticated or not current_user.has_roles('Admin'):
        abort(403)
    return render_template('Core/services.html')


