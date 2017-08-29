from flask import Flask, redirect, request, render_template, session, flash, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import GiveOffer, GetRequest, PostComment, Age, Income, Gender, SexOr, Race, User, Post, Picture, PostCategory, Category, Message, Following, connect_to_db, db 
from sqlalchemy import distinct
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

# @app.route("/notifications/all.json")
# def get_all_notification_data():

#     notification_data = {"foo":"bar"}
#     return jsonify(notification_data)


@app.route("/user_home")
def home_menu():
    """Displays user's homepage and menu of user options."""

    if 'logged_in' in session:
        user_obj = User.query.filter_by(username=session.get("logged_in")).first()
        user_post_objs = Post.query.filter_by(user_id=user_obj.user_id).all() 
        # all the posts made by logged in user
        requests_per_post = {}
        for user_post_obj in user_post_objs:
            requests_per_post[user_post_obj] = user_post_obj.get_requests
        requests_on_each_post = [user_post_obj.get_requests for user_post_obj in user_post_objs]
        unseen_request_objs, all_requests = get_notifications(requests_on_each_post)
        # all_requests.sort(key=lambda obj: obj.post_id)
        offers_on_each_post = [user_post_obj.give_offers for user_post_obj in user_post_objs]
        unseen_offer_objs, all_offers = get_notifications(offers_on_each_post)
        all_offers.sort(key=lambda obj: obj.post_id)
        post_comment_objs_per_post = [user_post.comments for user_post in user_post_objs] 
        unseen_post_comment_objs, all_comments = get_notifications(post_comment_objs_per_post) # a single list of ALL unseen commments for a particular user
        all_comments.sort(key=lambda obj: obj.post_id)
        num_notifications = len(unseen_offer_objs + unseen_post_comment_objs + unseen_request_objs)
        num_gives = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == True])
        num_gets = len([get_request_obj.post_id for get_request_obj in user_obj.get_requests if get_request_obj.post.recipient_user_id == user_obj.user_id])
        user_score = calculate_user_score(num_gives, num_gets)
        return render_template("homepage.html", user_score=user_score, num_gives=num_gives, num_gets=num_gets,
                                num_notifications=num_notifications, requests_per_post=requests_per_post,
                                all_requests=all_requests, all_offers=all_offers, all_comments=all_comments) 
    else: 
        return redirect("/login_form")

@app.route("/mark_notification_seen", methods=["POST"])
def mark_notification_seen():
    # will need notifification type and id to get from ajax

    notification_type = request.form.get("notification_type")
    notification_id = request.form.get("notification_id")

    if notification_type == "comment":
        query = PostComment.query.filter_by(comment_id=notification_id).first()
    elif notification_type == "offer":
        query = GiveOffer.query.filter_by(offer_id=notification_id).first()
    elif notification_type == "request":   
        query = GetRequest.query.filter_by(request_id=notification_id).first()

    query.is_seen = True
    db.session.commit()

    return "success"

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
    print "what do THESE selected categories look like...? : ", sel_categories
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

    categories = Category.query.all()
    post_type = request.form.get("post_type")
    get_category_objs = request.form.getlist("post_category")
    get_category_ids = [int(get_category_obj) for get_category_obj in get_category_objs] 
    active_give_post_objs = Post.query.filter_by(is_give=True, recipient_user_id=None).all()
    active_get_post_objs = Post.query.filter_by(is_give=False, recipient_user_id=None).all()
    give_category_ids = [(give_post_obj.post_id, [post_category.category_id for 
                          post_category in give_post_obj.post_categories]) for 
                          give_post_obj in active_give_post_objs]
    # give_category_ids returns eg: [(2, [5, 6]), (3, [3]), (4, [1, 2, 3])] 
    # -> list of tuples: [(post id, [list of category ids for that post]), (,[])]
    gives_match_gets = filter(filter_post_by_category, give_category_ids) 
    # a list of tuples (post_id number, [post_category ids where get matches give])
    # filter(takes in a function that passes in each item in the proceeding list and discards any "false-y" comparisons 
    # (ie where the set(is empty), 
    # iterates over a list and passes in each item to the preceding function as "post")
    # in this case, takes in a list of post ids
    give_post_ids = []
    for give_match_get in gives_match_gets:
        give_post_id, match_category_ids = give_match_get
        give_post_ids.append(give_post_id)
    match_give_objs = [Post.query.filter_by(post_id=give_post_id).first() for give_post_id in give_post_ids]

    return render_template("browse.html", categories=categories, post_type=post_type, get_post_objs=active_get_post_objs, 
                            give_post_objs=active_give_post_objs, match_give_objs=match_give_objs)


@app.route("/filter_search")
def filter_search():
    """Filters a user search by some combination of keyword, location, and/or selected category(ies)."""

    keyword = request.args.get("keyword")
    post_type = request.args.get("post_type")
    address = request.args.get("address") 
    category_ids = request.args.getlist("categories[]")[1:]

    results = Post.query
    if post_type == "give":    
        results = results.filter(Post.is_give==True) 
    elif post_type == "get":
        results = results.filter(Post.is_give==False)
    if keyword:    
        results = results.filter(Post.description.ilike("%" + keyword + "%")) 
    results = results.all()
    print "these should be all post objs: ", results
    if category_ids:
        category_ids = set(int(cat_id) for cat_id in category_ids)
        results = [result for result in results if set(category_ids) 
                   & set([post_category.category_id for post_category in result.post_categories])]
    results = [result.serialize for result in results]
    print "what the f are these????", results

    return jsonify({'results' : results})
    #     gives_match_gets = filter(filter_post_by_category, give_category_ids) 
    #     # a list of tuples (post_id number, [post_category ids where get matches give])
    #     # filter(takes in a function that passes in each item in the proceeding list and discards any "false-y" comparisons (ie where
    #     #the set(is empty), 
    #     # iterates over a list and passes in each item to the preceding function as "post")
    #     return posts_for_sel_categories

@app.route("/post/post_id/<int:post_id>")
def user_posting(post_id):
    """Displays each individual user posting that corresponds with the user's post ID."""

    #write logic to check if the post has a recipient
    #if post.recipient_user_id and post.author_id != current user and session['logged_in'] != :
        # flash "no longer active"
        # redirect browse
    
    user_posting_obj = Post.query.filter_by(post_id=post_id).first()
    requests_on_post_objs = GetRequest.query.filter_by(post_id=post_id).all()
    usernames_made_requests = [requests_on_post.user_made_request.username for requests_on_post 
                               in requests_on_post_objs]
    requests_on_post_objs = GetRequest.query.filter_by(post_id=post_id).all()
    user_score = None

    if "logged_in" not in session:
        flash("This posting is no longer active.")
        return redirect("/browse")
    elif "logged_in" in session:
        user_post_obj = User.query.filter_by(username=session.get('logged_in')).first()
        user_post_objs = Post.query.filter_by(user_id=user_post_obj.user_id).all()
        # requests_made_by_user_objs = GetRequest.query.filter_by(user_made_request=user_post_obj).all()
        if user_posting_obj.recipient_user_id and user_posting_obj.author.username != session["logged_in"] and session["logged_in"] != user_posting_obj.recipient.username:
            flash("This posting is no longer active.")
            return redirect("/browse")
        elif user_posting_obj.recipient_user_id and user_posting_obj.author.username == session["logged_in"]:
            flash("You have approved someone to claim this item. Here is the original posting.")
        elif user_posting_obj.recipient_user_id and session["logged_in"] == user_posting_obj.recipient.username:
            flash("You have been approved to get this item! Here is the original posting.")
        else:
            num_gives = len([user_post_obj.is_give for user_post_obj in user_post_objs if user_post_obj.is_give == True])
            num_gets = len([request_made_by_user for request_made_by_user in user_post_obj.get_requests if request_made_by_user.post.recipient_user_id != None])
            # num_gets = len([request_made_by_user for request_made_by_user in requests_made_by_user_objs if request_made_by_user.request_approved == True])
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
    # post_user_obj = post_obj.author
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
    # post_user_obj = post_obj.author
    # requests_for_user_objs = post_obj.get_requests
    user_id = User.query.filter_by(username=session.get('logged_in')).first().user_id
    message = GiveOffer(post_id=post_id, user_id=user_id, time_offered=datetime.datetime.now(), 
                        offer_message=message)
    db.session.add(message)
    db.session.commit()

    return jsonify({'results' : "Offer Sent"})

@app.route("/approve_request", methods=["POST"])
def approve_request():
    """After a user approves one request on their post, marks the post as 
    no longer active and removes the posting."""

    request_id = request.form.get("request_id")
    approved_request = GetRequest.query.filter_by(request_id=request_id).first()
    approved_post = approved_request.post
    approved_post.recipient_user_id = approved_request.user_id
    db.session.commit()

    return jsonify({'results' : request_id})

@app.route("/undo_approve_request", methods=["POST"])
def undo_approve():
    """Removes recipient ID on a post where the get approval has been undone."""

    post_id = request.form.get("post_id")
    undone_approve_post = Post.query.filter_by(post_id=post_id).first()
    undone_approve_post.recipient_user_id = None
    db.session.commit()

    return jsonify({'results' : "post is now active"})

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

def filter_by_keyword(keyword=None, post_type=None):
    """Returns all active posts that match   a keyword search."""

    if post_type is None:
        active_posts = Post.query.filter_by(recipient_user_id=None)
    else:
        active_posts = Post.query.filter_by(is_give=post_type, recipient_user_id=None)
    if keyword:
        posts_match_keyword = [post for post in active_posts if keyword in post.description]
    else:
        posts_match_keyword = active_posts

    return posts_match_keyword

def get_notifications(notifications_on_each_post):
    """Calculates all the notifications for a single user."""

    unseen_notifications_of_type = []
    all_notifications_of_type = []
    for notifications in notifications_on_each_post:
        for notification in notifications:
            if notification.is_seen == False:
                unseen_notifications_of_type.append(notification)
            all_notifications_of_type.append(notification)
    return (unseen_notifications_of_type, all_notifications_of_type)

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