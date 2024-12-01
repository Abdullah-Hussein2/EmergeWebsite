from flask import Blueprint , render_template , redirect , url_for , request , flash
from . import db
from .models import User , Role
from flask_login import login_user , logout_user , login_required , current_user
from werkzeug.security import generate_password_hash, check_password_hash



auth = Blueprint("auth", __name__)

@auth.route("/login" , methods=['GET' , 'POST'])
def login():

    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('Password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!' , category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('pass is incorrect.' , category='error')
        else:
            flash('Email is incorrect or dose\'t exist.' , category='error')

    return render_template("login.html" , user=current_user)










@auth.route("/signup" , methods=['GET' , 'POST'])
def sign_up():
    if request.method == 'POST':

        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters long.', category='error')
        else:
            default_role = Role.query.filter_by(name='User').first()
            if not default_role:
                default_role = Role(name='User', label='Regular User')
                db.session.add(default_role)
                db.session.commit()


            new_user = User(email=email,
                            first_name=first_name,
                            last_name=last_name,
                            is_active=True ,
                            password=generate_password_hash(password1))



            new_user.roles.append(default_role)
            db.session.add(new_user)
            db.session.commit()


            login_user(new_user, remember=True)
            flash('User created' , category='success')
            return redirect(url_for('views.home'))
    return render_template("signup.html" , user=current_user)









@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
