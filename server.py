from flask import Flask, redirect, request, render_template, session, flash, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import PostComment, Age, Income, Gender, SexOr, Race, User, Post, Picture, PostCategory, Category, Message, Following, connect_to_db, db 
import random
import datetime

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
                   "Best of luck in your search",
                   "You deserve to have everything you need"]

@app.route('/')
def show_form():
    """Welcome page and request login or sign up."""
    
    if "logged_in" in session:
        return redirect("/user_home")
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

    if "logged_in" in session:
        return redirect("/user_home")
    else:
        return render_template("new_user.html", incomes=incomes, ages=ages, genders=genders,
                                races=races, sex_ors=sex_ors)


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

    if "logged_in" in session:
        return redirect("/user_home")
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
        return redirect('/user_home')
    elif not user:
        flash("I'm sorry. That username does not exist. Please create an account!")
        return redirect("/new_user")
    else:
        flash("I'm sorry. That is an incorrect password. Please try again.")
        return redirect("/login_form")     

@app.route("/user_home")
def home_menu():
    """Displays user's homepage and menu of user options."""

    username = session.get('logged_in')
    user_obj = User.query.filter_by(username=session.get('logged_in')).first()
    user_post_objs = user_obj.posts
    num_gives = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == True])
    num_gets = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == False])
    user_score = calculate_user_score(num_gives, num_gets)

    if session.get("logged_in") != None:
        return render_template("homepage.html", user_score=user_score, num_gives=num_gives, num_gets=num_gets)
    else: 
        return redirect("/login_form")

@app.route("/user_interest")
def user_choice():
    """Takes in user's current interest in using app."""

    user_interest = request.args.get("user_interest")
    categories = Category.query.all()

    if user_interest == "give":
        give_compliment = random.choice(GIVE_COMPLIMENTS)
        return render_template("user_submit_post.html", user_interest=user_interest, give_compliment=give_compliment, categories=categories)
    elif user_interest == "get":
        get_compliment = random.choice(GET_COMPLIMENTS)
        return render_template("user_submit_post.html", user_interest=user_interest, get_compliment=get_compliment, categories=categories)

# @app.route("/save_categories")
# def save_categories():
#     """Takes in user selected categories and tags post."""

#     categories = []
#     sel_categories = request.args.getlist('category')
#     category_names = db.session.query(Category.category_name).filter(Category.category_id.in_(sel_categories)).all()
    
#     for category in category_names:
#         categories.append(category[0])
#     return jsonify({'results' : categories})

@app.route("/confirm_post", methods=["POST"])
def confirm_post():
    """Confirms a user's posting, saves their posting and 
    associated categories to the database."""
    # import pdb; pdb.set_trace()
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    sel_categories = request.form.getlist('category')
    category_objs = db.session.query(Category).filter(Category.category_id.in_(sel_categories)).all()
    
    post_type = request.form.get("post_type")
    post_title = request.form.get("post_title")
    description = request.form.get("post_message")
    give_or_get = is_give_or_get(post_type) # returns t or f
    post = Post(user_id=user_id, title=post_title, description=description, post_date=datetime.datetime.now(), is_give=give_or_get, is_active=True)
    db.session.add(post)
    db.session.commit()

    post_categories = [PostCategory(post_id=post.post_id, category_id=category.category_id) for category in category_objs]

    map(lambda x: db.session.add(x), post_categories) 
    #map(takes anonymous function lambda, iterates over post_categories)
    db.session.commit()
    return render_template("post_confirm.html", is_give=give_or_get, post_categories=post_categories)

@app.route("/browse", methods=["GET", "POST"])
def browse_posts():
    """Displays page where user can browse postings and are given recommended posts."""

    def filter_post_by_category(post):
        """Determines all the instances where a get post categories match give posts categories."""
        # post is a tuple with (post_id, [category ids for post])
        return set(post[1]) & set(get_category_ids)

    post_type = request.form.get("post_type")
    get_category_objs = request.form.getlist("post_category")
    get_category_ids = [int(get_category_obj) for get_category_obj in get_category_objs] # 
    give_post_objs = Post.query.filter_by(is_give=True).all()
    get_post_objs = Post.query.filter_by(is_give=False).all()
    give_category_ids = [(give_post_obj.post_id, [post_category.category_id for post_category in give_post_obj.post_categories]) for give_post_obj in give_post_objs]
    gives_match_gets = filter(filter_post_by_category, give_category_ids) # a list of tuples (post_id number, [post_category ids where get matches give])
    give_post_ids = []
    for give_match_get in gives_match_gets:
        give_post_id, match_category_ids = give_match_get
        give_post_ids.append(give_post_id)
    # filter(takes in a function that passes in each item in the proceeding list and discards any "false-y" comparisons (ie where
    #the set(is empty), 
    # iterates over a list and passes in each item to the preceding function as "post")
    match_give_objs = [Post.query.filter_by(post_id=give_post_id).first() for give_post_id in give_post_ids]

    return render_template("browse.html", post_type=post_type, get_post_objs=get_post_objs, give_post_objs=give_post_objs, match_give_objs=match_give_objs)

@app.route("/browse_all")
def browse_all():
    """Allows users to browse all give posts."""

    return render_template("browse.html", post_type=None, give_post_objs=Post.query.filter_by(is_give=True).all())

@app.route("/post/post_id/<int:post_id>")
def user_posting(post_id):
    """Displays each individual page for a user's post."""

    user_posting = Post.query.filter_by(post_id=post_id).one() 
    #this should be the user posting that corresponds with the url post_id <from browse.html
    post_comments = PostComment.query.filter_by(post_id=post_id).all()
    user_posts = User.query.filter_by(username=session.get("logged_in")).one().posts
    num_gives = len([user_post.is_give for user_post in user_posts if user_post.is_give == True])
    
    return render_template("user_posting.html", user_posting=user_posting, post_comments=post_comments, 
                            num_gives=num_gives)

@app.route("/save_comment", methods=["POST"])
def save_comment():
    """Saves a comment on a post to the database."""

    post_comment = request.form.get("comments")
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    post_id = request.form.get("post_id")
    print post_id
    comment = PostComment(post_id=post_id, user_id=user_id, time_posted=datetime.datetime.now(), comment_body=post_comment)
    db.session.add(comment)
    db.session.commit()

    com_post_time = datetime.datetime.strftime(comment.time_posted, "%Y-%m-%d")
    return jsonify({'results' : com_post_time})

@app.route("/user_profile/<username>")
def user_profile(username):
    """Displays individual user's profile page with their user activity."""

    profile_user_obj = User.query.filter_by(username=username).one()
    profile_user_obj_posts = User.query.filter_by(username=username).one().posts
    user_comment_objs = PostComment.query.filter_by(user=profile_user_obj).all()
    all_user_activity_objs = profile_user_obj_posts + user_comment_objs
    all_user_activity_objs.sort(key=lambda obj: obj.post_date if type(obj) == Post else obj.time_posted)

    return render_template("user_profile.html", profile_user=profile_user_obj)

@app.route("/log_out")
def log_out():
    """Logs user out."""

    del session['logged_in']
    flash("You are now logged out. See you next time!")
    return redirect("/")

###############################################################
# Helper functions 

# create a function to calculate users' getting and giving scores   
def calculate_user_score(num_gives, num_gets):
    """Calculates user score for getting and giving."""
    score = 10
    if num_gives != 0:
        score += num_gives * 5 - num_gets
    elif num_gives == 0 and num_gets != 0:
        score -= num_gets
    return score

def is_give_or_get(post_type):
        """Returns true if a user post is giving, returns false if a user post is getting."""
        
        if post_type == "give":
            return True
        elif post_type == "get":
            return False

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