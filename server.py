from flask import Flask, redirect, request, render_template, session, flash
# from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import Age, Income, Gender, SexOr, Race, User, Post, Picture, PostCategory, Category, Message, Following, connect_to_db, db 
import random

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True

# Required to use Flask sessions and the debug toolbar
app.secret_key = "1a2b3c"

GIVE_COMPLIMENTS = ["Glad you are feeling like such a generous spirit today",
                    "How kind you are",
                    "It's someone's lucky day",
                    "You're giving someone something they need",
                    "You inspire"]
GET_COMPLIMENTS = ["Hope you find what you are looking for",
                   "Good for you for seeking what you need",
                   "Best of luck in your search"]

@app.route('/')
def show_form():
    """Welcome page and request login or sign up."""
    if session.get("user") != None:
        return redirect("/home")
    else:
        return render_template("welcomepage.html")

@app.route("/new_user")
def new_user():
    """Display page for user to create new account."""
    incomes = Income.query.all()
    ages = Age.query.all()
    genders = Gender.query.all()
    races = Race.query.all()
    sex_ors = SexOr.query.all()

    if session.get("user") != None:
        return redirect("/home")
    else:
        return render_template("new_user.html", incomes=incomes, ages=ages, genders=genders,
                                races=races, sex_ors=sex_ors)

    # user = request.args.get("person")
    # session["user_name"] = user 
    # return redirect("/top-melons")

@app.route("/create_account", methods=["POST"])
def create_account():
    """Store new user in database."""

    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    loc_by_reg = request.form.get("location")
    income_lev = convert_to_none(request.form.get("income_lev"))
    age = convert_to_none(request.form.get("age"))
    gender = convert_to_none(request.form.get("gender"))
    race = convert_to_none(request.form.get("race"))
    sex_or = convert_to_none(request.form.get("sex_or"))
    pic_url = request.form.get("")

    new_user = User(username=username, password=password, email=email, loc_by_reg=loc_by_reg,
                    income_id=income_lev, age_id=age, gender_id=gender, race_id=race, sex_or_id=sex_or)
    if not User.query.filter_by(email=email).first(): # and User.query.filter_by(username=username).first():
        db.session.add(new_user)
        db.session.commit()
        flash("Thanks for signing up! Hope you GWUG!")
    elif User.query.filter_by(email=email).first():
        flash("This email is already associated with an account. Please log in!")
    elif User.query.filter_by(username=username).first():
        flash("This username is already in use. Please choose another.")
        return redirect("/new_user")
    return redirect("/login_form")

@app.route("/login_form")
def log_in():
    """Display login page."""

    if session.get("user") != None:
        return redirect("/home")
    else:
        return render_template("login_form.html")

@app.route("/verify_user", methods=["POST"])
def verify_user():
    """Verify the user login exists in database."""

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.password == password: 
        session['logged_in'] = username
        flash("Logged in as {}".format(username))
        return redirect('/home')
    else:
        flash("I'm sorry. That is an incorrect password. Please try again.")
        return redirect("/login_form")     

@app.route("/home")
def home_menu():
    """Displays user's homepage and menu of user options."""

    username = session.get('logged_in')

    if session.get("logged_in") != None:
        user_obj = User.query.filter_by(username=session.get('logged_in')).first()
        user_gives = user_obj.num_gives
        user_gets = user_obj.num_gets
        gets_left = 10 - user_gets
        return render_template("homepage.html", gives=user_gives, gets=user_gets,
                                gets_left=gets_left)
    else: 
        return redirect("/login_form")

@app.route("/user_interest")
def user_choice():
    """Takes in user's current interest in using app."""

    user_interest = request.args.get("user_interest")
    
    if user_interest == "give":
        categories = Category.query.all()
        give_compliment = random.choice(GIVE_COMPLIMENTS)
        return render_template("give_post.html", compliment=give_compliment, categories=categories)
    elif user_interest == "need":
        get_compliment = random.choice(GET_COMPLIMENTS)
        return render_template("get_post.html", compliment=get_compliment)
    elif user_interest == "browse":
        return render_template("user_browse.html")

@app.route("/process_categories")
def process_categories():
    """Takes in user selected categories."""

    user_categories = request.args.get("category")


@app.route("/log_out")
def log_out():
    """Logs user out."""

    del session['logged_in']
    flash("You are now logged out. See you next time!")
    return redirect("/")

###############################################################
# Helper functions    

def convert_to_none(string):
    """Converts empty strings to None."""
    if string == "":
        return None
    return string

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)
    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")