from flask import Blueprint , render_template , redirect ,url_for , Response , send_file
from flask_login import current_user, login_required
from flask_user import roles_required
from .models import User

views = Blueprint("views", __name__)



@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)



@views.route("/posts")
def posts():
    return render_template("posts.html" ,user=current_user)




@views.route('/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)  # Fetch user data by user_id
    if user:
        return render_template('user_profile.html', user=user)
    else:
        return "User not found", 404




# Route to serve user image from database
@views.route('/user_image/<int:user_id>')
def user_image(user_id):
    user = User.query.get(user_id)
    if user and user.image:
        return Response(user.image, mimetype='image/jpeg')
    return "Image not found", 404
