from flask import Blueprint , render_template
from flask_login import current_user, login_required
from flask_user import roles_required

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)



@views.route("/posts")
def posts():
    return render_template("posts.html" ,user=current_user)
