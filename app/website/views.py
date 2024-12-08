from flask import Blueprint , render_template , redirect ,url_for , Response , request , abort , flash
from flask_login import current_user, login_required
from flask_user import roles_required
from .models import User , Doctor



views = Blueprint("views", __name__)



@views.route("/")
@views.route("/home")
def home():
    return render_template("Core/home.html", user=current_user)



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
@roles_required('Admin')
def view_doctors():
    doctors = Doctor.query.all()
    return render_template('Adminstartion/view_doctors.html', doctors=doctors)





@views.route('/services')
def services():
    if not current_user.is_authenticated or not current_user.has_roles('Admin'):
        abort(403)
    return render_template('Core/services.html')
