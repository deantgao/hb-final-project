from flask import Flask, redirect, request, render_template, session, flash, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import GiveOffer, GetRequest, PostComment, Age, Income, Gender, SexOr, Race, User, Post, Picture, PostCategory, Category, Message, Following, connect_to_db, db 
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

    if 'logged_in' in session:
        user_obj = User.query.filter_by(username=session.get("logged_in")).first()
        user_id = user_obj.user_id
        user_post_objs = Post.query.filter_by(user_id=user_id).all() 
        # all the posts made by logged in user
        # user_post_ids = [user_post_obj.post_id for user_post_obj in user_post_objs] 
        requests_on_each_post = [user_post_obj.get_requests for user_post_obj in user_post_objs]
        unseen_request_objs = []
        for requests_on_post in requests_on_each_post:
            for each_request in requests_on_post:
                if each_request.is_seen == False:
                    unseen_request_objs.append(each_request)
        offers_on_each_post = [user_post_obj.give_offers for user_post_obj in user_post_objs]
        unseen_offer_objs = []
        for offers_on_post in offers_on_each_post:
            for each_offer in offers_on_post:
                if each_offer.is_seen == False:
                    unseen_offer_objs.append(each_request)
        post_comment_objs_per_post = [user_post.comments for user_post in user_post_objs] 
        # this is a list of lists [[comment objs on each post]]
        unseen_post_comment_objs = [] # a single list of ALL unseen commments for a particular user
        for post_comments_on_obj in post_comment_objs_per_post:
            for comment in post_comments_on_obj:
                if comment.is_seen == False:
                    unseen_post_comment_objs.append(comment)
        num_notifications = len(unseen_offer_objs + unseen_post_comment_objs + unseen_request_objs)
        num_gives = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == True])
        num_gets = len([get_request_obj for get_request_obj in user_obj.get_requests if get_request_obj.request_approved == True])
        user_score = calculate_user_score(num_gives, num_gets)
        # post_ids_w_requests = [user_post_obj.post_id for user_post_obj in user_post_objs if len(user_post_obj.get_requests) > 0]
        return render_template("homepage.html", user_score=user_score, num_gives=num_gives, num_gets=num_gets,
                                num_notifications=num_notifications, unseen_requests=unseen_request_objs,
                                unseen_comments=unseen_post_comment_objs, unseen_offers=unseen_offer_objs)
    else: 
        return redirect("/login_form")

# @app.route("/render_notifications")
# def render_notifications():
#     """Renders the notifications to display on user homepage."""



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
    post = Post(user_id=user_id, title=post_title, description=description, post_date=datetime.datetime.now(), is_give=give_or_get)
    db.session.add(post)
    db.session.commit()

    post_categories = [PostCategory(post_id=post.post_id, category_id=category.category_id) for category in category_objs]

    map(lambda x: db.session.add(x), post_categories) 
    #map(takes anonymous function lambda, iterates over post_categories)
    db.session.commit()
    return render_template("post_confirm.html", is_give=give_or_get, post_categories=post_categories)

@app.route("/browse", methods=["GET", "POST"])
def browse_posts():
    """Displays page where user can browse postings and is given recommended posts."""

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

# @app.route("/browse_all")
# def browse_all():
#     """Allows users to browse all give posts."""

#     return render_template("browse.html", post_type=None, give_post_objs=Post.query.filter_by(is_give=True).all())

@app.route("/post/post_id/<int:post_id>")
def user_posting(post_id):
    """Displays each individual user posting that corresponds with the user's post ID."""
    
    user_posting_obj = Post.query.filter_by(post_id=post_id).first()
    requests_on_post_objs = GetRequest.query.filter_by(post_id=post_id).all()
    usernames_made_requests = [request.user_made_request.username for request in requests_on_post_objs]
    user_score = None
    if "logged_in" in session:
        user_post_obj = User.query.filter_by(username=session.get('logged_in')).first()
        user_post_objs = Post.query.filter_by(user_id=user_post_obj.user_id).all()
        requests_made_by_user_objs = GetRequest.query.filter_by(user_made_request=user_post_obj).all()
        # requests_on_each_post = [user_post_obj.get_requests for user_post_obj in user_post_objs]
        num_gives = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == True])
        num_gets = len([request_made_by_user for request_made_by_user in requests_made_by_user_objs if request_made_by_user.request_approved == True])
        user_score = calculate_user_score(num_gives, num_gets)
    
    return render_template("user_posting.html", user_posting=user_posting_obj, 
                            user_score=user_score, users_requested=usernames_made_requests)

@app.route("/save_comment", methods=["POST"])
def save_comment():
    """Saves a comment on a post to the database."""

    post_comment = request.form.get("comments")
    post_id = request.form.get("post_id")
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    comment = PostComment(post_id=post_id, user_id=user_id, time_posted=datetime.datetime.now(), comment_body=post_comment)
    db.session.add(comment)
    db.session.commit()

    com_post_time = datetime.datetime.strftime(comment.time_posted, "%Y-%m-%d")
    return jsonify({'results' : com_post_time})

@app.route("/make_get_request", methods=["POST"])
def make_get_request():
    """Saves a get request to the database."""

    message = request.form.get("message")
    post_id = request.form.get("post_id")
    post_obj = Post.query.filter_by(post_id=post_id).one()
    # post_user_obj = post_obj.post_give_user
    # requests_for_user_objs = post_obj.get_requests
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    message = GetRequest(post_id=post_id, user_id=user_id, time_requested=datetime.datetime.now(), 
                        request_message=message)
    db.session.add(message)
    db.session.commit()

    return jsonify({'results' : "Request Sent"})

@app.route("/make_give_offer", methods=["POST"])
def make_give_offer():
    """Saves a give offer to the database."""

    message = request.form.get("message")
    post_id = request.form.get("post_id")
    post_obj = Post.query.filter_by(post_id=post_id).one()
    # post_user_obj = post_obj.post_give_user
    # requests_for_user_objs = post_obj.get_requests
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    message = GiveOffer(post_id=post_id, user_id=user_id, time_offered=datetime.datetime.now(), 
                        offer_message=message)
    db.session.add(message)
    db.session.commit()

    return jsonify({'results' : "Offer Sent"})

# @app.route("/send_get_request", methods=["POST"])
# def send_get_request():
#     """Sends request and message to user of posting."""

#     request_message = request.form.get("request_message")
#     post_id = request.form.get("post_id")
#     post_obj = Post.query.filter_by(post_id=post_id).one()
#     post_user_obj = post_obj.user
#     requests_for_user_objs = post_obj.get_requests
#     user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id

#     return render_template("/user_home", )


@app.route("/user_profile/<username>")
def user_profile(username):
    """Displays individual user's profile page with their user activity."""

    profile_user_obj = User.query.filter_by(username=username).first()
    profile_user_post_objs = Post.query.filter_by(user_id=profile_user_obj.user_id).all()
    profile_user_comment_objs = PostComment.query.filter_by(user=profile_user_obj).all()
    all_user_activity_objs = profile_user_post_objs + profile_user_comment_objs
    all_user_activity_objs.sort(key=lambda obj: obj.post_date if type(obj) == Post else obj.time_posted)
    print "these should be chronologically ordered user activity: ", all_user_activity_objs

    return render_template("user_profile.html", profile_user=profile_user_obj, 
                            all_user_activity=all_user_activity_objs, profile_user_posts=profile_user_post_objs)

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
    score = 5
    if num_gives != 0:
        score += num_gives * 3 - num_gets
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