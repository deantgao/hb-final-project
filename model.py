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
    # comments_tagged = db.Column(nullable=True)
    # followers = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # followees = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pic_url = db.Column(db.String(400), nullable=True) #advanced V2 feature

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
                                        secondaryjoin="User.user_id==Following.user_followed") # these could be separate tables(?)

    @property
    def serialize(self):
        """Returns dictionary of data for user object."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
        }

class Income(db.Model):
    """Each user income type."""

    __tablename__ = "user_incomes"

    income_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_of = db.Column(db.String(100), nullable=True)

class Age(db.Model):
    """Each user age type."""

    __tablename__ = "user_ages"

    age_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_of = db.Column(db.String(50), nullable=True)

class Gender(db.Model):
    """Each user gender ID."""

    __tablename__ = "user_genders"

    gender_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_of = db.Column(db.String(100), nullable=True)

class Race(db.Model):
    """Each user racial background."""

    __tablename__ = "user_races"

    race_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_of = db.Column(db.String(100), nullable=True)

class SexOr(db.Model):
    """Each user sexual orientation."""

    __tablename__ = "user_sex_ors"

    sex_or_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_of = db.Column(db.String(100), nullable=True)

class Post(db.Model):
    """Each individual posting."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unique_id = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True, default=None)
    title = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(1000), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False)
    is_give = db.Column(db.Boolean(), nullable=False, default=None) # is this correct syntax for boolean?
    # is_active = db.Column(db.Boolean(), nullable=False, default=True) # is this correct syntax for boolean?
    featured_img = db.Column(db.String(400), nullable=True)

    author = db.relationship('User', primaryjoin="Post.user_id==User.user_id", backref="posts")
    # this is the user obj who authored the posting
    recipient = db.relationship('User', primaryjoin="Post.recipient_user_id==User.user_id", backref="gets") 
    # this is the user obj who is approved to get the item posted

    @property
    def serialize(self):
        """Returns dictionary of data for post object."""
        return {
            "post_id": self.post_id,
            "unique_id": self.unique_id,
            "user_id": self.user_id,
            "recipient_user_id": self.recipient_user_id,
            "title": self.title,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "post_date": self.post_date.strftime("%Y-%m-%d"),
            "author": self.author.serialize
        }

class GetRequest(db.Model):
    """Each individual get request on a user's give posting."""

    __tablename__ = "get_requests"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # user_received_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=Fal)
    time_requested = db.Column(db.DateTime, nullable=False)
    request_message = db.Column(db.String(1000), nullable=True)
    is_seen = db.Column(db.Boolean(), nullable=False, default=False)

    post = db.relationship('Post', backref="get_requests")
    user_made_request = db.relationship('User', foreign_keys=[user_id], backref="get_requests") #backref=db.backref("get_requests"), primaryjoin="get_requests.user_id==users.user_id")

    @property
    def user_received_request(self):
        post_w_request = Post.query.filter_by(post_id=self.post_id).first()
        user_id_on_post = post_w_request.user_id
        return User.query.filter_by(user_id=user_id_on_post).first()

class GiveOffer(db.Model):
    """Each individual give offer on a user's get posting."""

    __tablename__ = "give_offers"

    offer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_made_offer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    time_offered = db.Column(db.DateTime, nullable=False)
    offer_message = db.Column(db.String(1000), nullable=True)
    is_seen = db.Column(db.Boolean(), nullable=False, default=False)
    # offer_approved = db.Column(db.Boolean(), nullable=False, default=False)  
    post = db.relationship('Post', backref="give_offers")
    user_made_offer = db.relationship('User', primaryjoin="GiveOffer.user_made_offer_id==User.user_id")

    @property
    def user_received_offer(self):
        post_w_offer = Post.query.filter_by(post_id=self.post_id).first()
        user_id_on_post = post_w_offer.user_id
        return User.query.filter_by(user_id=user_id_on_post).first()

    # def user_received_offer


class Picture(db.Model):
    """Each picture associated with a post."""

    __tablename__ = "pictures"

    pic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    pic_url = db.Column(db.String(400), nullable=True)

    post = db.relationship('Post', backref='pictures')

class PostCategory(db.Model):
    """Association for a post and the category it belongs to."""

    __tablename__ = "post_categories"

    post_cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)

    post = db.relationship('Post', backref="post_categories")
    category = db.relationship('Category', backref="post_categories")

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
    unique_id = db.Column(db.Integer, nullable=False, default=1)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False)
    comment_body = db.Column(db.String(400), nullable=False)
    is_seen = db.Column(db.Boolean(), nullable=False, default=False)

    user = db.relationship('User', backref="comments") # this refers to the user who MADE a comment
    post = db.relationship('Post', backref="comments")

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

def create_categories(categories):
    for category_name in categories:
        category = Category(category_name=category_name)
        db.session.add(category)
    db.session.commit()

def create_incomes(income_levs):
    for income_lev in income_levs:
        income = Income(type_of=income_lev)
        db.session.add(income)
    db.session.commit()

def create_ages(ages):
    for age in ages:
        age_type = Age(type_of=age)
        db.session.add(age_type)
    db.session.commit()

def create_genders(genders):
    for gender in genders:
        gender_type = Gender(type_of=gender)
        db.session.add(gender_type)
    db.session.commit()

def create_races(races):
    for race in races:
        race_type = Race(type_of=race)
        db.session.add(race_type)
    db.session.commit()

def create_sex_ors(sex_ors):
    for sex_or in sex_ors:
        sex_or_type = SexOr(type_of=sex_or)
        db.session.add(sex_or_type)
    db.session.commit()

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    db.drop_all()
    db.create_all()
    print "Connected to DB."

    categories = ["Clothing", "Services", "Food", "Furniture", "Books", "Toys", "Electronics", "Vehicles", "Miscellaneous"]
    create_categories(categories)

    income_levs = ["", "Un/underemployed", "Under $30,000", "$30,000-$70,000", "$70,000-$100,000", "Over $100,000"]
    create_incomes(income_levs)

    ages = ["", "18 or Under", "19-25", "25-35", "35-50", "50-65", "65 or Older"]
    create_ages(ages)

    genders = ["", "Transmasculine", "Transfeminine", "Woman", "Man", "Genderqueer", "Agender", "Two-Spirit"]
    create_genders(genders)

    races = ["", "Black/African American", "Latino/a/x", "Pacific Islander", "Southeast Asian", 
             "South Asian", "East Asian", "Native American", "White", "Mixed Race"]
    create_races(races)

    sex_ors = ["", "Queer", "Lesbian", "Gay", "Bisexual", "Pansexual", "Straight", "Asexual"]
    create_sex_ors(sex_ors)


