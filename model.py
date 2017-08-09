from flask_sqlalchemy import SQLAlchemy

# Here's where we create the idea of our database. We're getting this through
# the Flask-SQLAlchemy library. On db, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Part 1: Compose ORM

class User(db.Model):
    """Individual app user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    loc_by_reg = db.Column(db.String(50), nullable=True)
    income_id = db.Column(db.Integer, db.ForeignKey('user_incomes.income_id'), nullable=True)
    age_id = db.Column(db.Integer, db.ForeignKey('user_ages.age_id'), nullable=True)
    gender_id = db.Column(db.Integer, db.ForeignKey('user_genders.gender_id'), nullable=True)
    race_id = db.Column(db.Integer, db.ForeignKey('user_races.race_id'), nullable=True)
    sex_or_id = db.Column(db.Integer, db.ForeignKey('user_sex_ors.sex_or_id'), nullable=True)
    # comments_made = db.Column(nullable=True)
    # comments_tagged = db.Column(nullable=True)
    # followers = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # followees = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # pic_url = db.Column(db.String(400), nullable=True) #advanced V2 feature

    income = db.relationship('Income', backref="users")
    age = db.relationship('Age', backref="users")
    gender = db.relationship('Gender', backref="users")
    race = db.relationship('Race', backref="users")
    sex_or = db.relationship('SexOr', backref="users")

    followers = db.relationship('User', secondary="followings", 
                                        primaryjoin="User.user_id==Following.user_followed",
                                        secondaryjoin="User.user_id==Following.user_following")
    followees = db.relationship('User', secondary="followings", 
                                        primaryjoin="User.user_id==Following.user_following",
                                        secondaryjoin="User.user_id==Following.user_followed")

class Income(db.Model):
    """Each user income category."""

    __tablename__ = "user_incomes"

    income_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=True)

class Age(db.Model):
    """Each user age category."""

    __tablename__ = "user_ages"

    age_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=True)

class Gender(db.Model):
    """Each user income category."""

    __tablename__ = "user_genders"

    gender_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=True)

class Race(db.Model):
    """Each user income category."""

    __tablename__ = "user_races"

    race_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=True)

class SexOr(db.Model):
    """Each user income category."""

    __tablename__ = "user_sex_ors"

    sex_or_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=True)

class Post(db.Model):
    """Each individual posting."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    latitude = db.Column(db.String(100), nullable=True) #should these be strings?
    longitude = db.Column(db.String(100), nullable=True)
    post_date = db.Column(db.DateTime, nullable=False) # is there anything else needed here?
    is_need = db.Column(db.Boolean(), nullable=False) # is this correct syntax for boolean?
    is_active = db.Column(db.Boolean(), nullable=False, default=True) # is this correct syntax for boolean?
    featured_img = db.Column(db.String(400), nullable=True)

    user = db.relationship('User', backref="posts") # is this correct relationship to refer back to two FKs?

class Picture(db.Model):
    """Each picture associated with a post."""

    __tablename__ = "pictures"

    pic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    pic_url = db.Column(db.String(400), nullable=True)

    post = db.relationship('Post', backref='pictures')

class PostCategory(db.Model):
    """Association for a post and the category(ies) it belongs to."""

    __tablename__ = "post-categories"

    post_cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)

    post = db.relationship('Post', backref="post-categories")
    category = db.relationship('Category', backref="post-categories")

class Category(db.Model):
    """Category type for a post."""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), nullable=False)

class Message(db.Model):
    """A message sent between users."""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_sent = db.Column(db.DateTime, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message_body = db.Column(db.String(1000), nullable=False)

    user_receive = db.relationship('User', primaryjoin="Message.recipient_id==User.user_id")
    user_sent = db.relationship('User', primaryjoin="Message.sender_id==User.user_id")

class Following(db.Model):
    """Each follow between users."""

    __tablename__ = "followings"

    following_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_followed = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_following = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # user_follo = db.relationship('User', primaryjoin="Following.")
    # user = db.relationship('User', backref="followers")

class PostComment(db.Model):
    """Each comment on a post."""

    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False)
    comment_body = db.Column(db.String(400), nullable=False)
    # tagged = db.Column(db.Array) # how would i store tags in this field? using an array/list?

# how to create a table/field for tagging people in comments?


##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///resourceshare'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
