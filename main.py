# Section 1: Imports
from re import A
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import session, g

from flask_session import Session

from flask_paginate import Pagination

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, Integer
import csv
import os
import datetime
# End Section 1

## Section 2: Initalize
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test5.db'
app.config['SECRET_KEY'] = 'xxxxxxxxx'
app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(minutes=6)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
## End Section 2

### Section 3: Database Models
### # Subsection 1: User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    country = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=True)
    
    def __repr__(self):
        return self.name

    def as_dict(self):
        dict = {
            "id": self.id,
            "usernam": self.username,
            "country": self.country,
            "date": self.date, 
            "gender": self.gender,
            "email": self.email
        }

        return dict
### # End Subsection 1

### ## Subsection 2: Application Model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    size = db.Column(db.String(80), unique=False, nullable=False)
    currency = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.String(80), unique=False, nullable=False)
    rating_count_total = db.Column(db.String(80), unique=False, nullable=False)
    version = db.Column(db.String(80), unique=False, nullable=False)
    user_rating = db.Column(db.String(80), unique=False, nullable=False)
    genre = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return self.name

    def as_dict(self):
        dict = {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "currency": self.currency, 
            "price": self.price,
            "rating_count_total": self.rating_count_total,
            "version": self.version,
            "user_rating": self.user_rating,
            "genre": self.genre
        }

        return dict
### ## End Subsection 2
### End Section 3

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    text = db.Column(db.String(500), unique=False, nullable=False)
    app_id = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return self.username
    
    def as_dict(self):
        dict = {
            "id": self.id,
            "username": self.username,
            "text": self.text
        }

        return dict

#### Section 4: Create the Tables
db.create_all()
#### End Section 4

##### Section 5: Routes
##### # Subsection 1: Route for DB
@app.route("/db")
def database():
    with open('.data/store.csv', encoding='latin-1') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            first_line = True
            for row in data:
                if not first_line:
                    app_model = Application(name=row[2],
                                    size=str(round(int(row[3])/1000000,2)),
                                    currency=row[4],
                                    price=str(row[5]),
                                    rating_count_total=row[6],
                                    version=str(row[10]),
                                    user_rating=str(row[8]),
                                    genre=row[12])

                    db.session.add(app_model)
                    db.session.commit()
                    print("done")
                else:
                    first_line = False
    return "<h1>Done</h1>"
##### # End Subsection 1

##### ## Subsection 2: Route for home
@app.route("/")
def index():
    if "username" in session:
        g.username = session["username"]
        return render_template("index.html")

    return render_template("index.html")
##### ## End Subsection 2

##### ### Subsection 3: Route for SignUp
@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        username = None
        country = None
        birthday = None
        gender = request.form["gender"]

        if 'username' in request.form:
            username = request.form['username']
            print(request.form)
            if username == "":
                err = "Username field can not be empty!"
                return render_template("signup.html", err=err)
        if "country" in request.form:
            country = request.form["country"]
            if country is None:
                err = "Country field can not be empty!"
                return render_template("signup.html", err=err)
        if "birthday" in request.form:
            birthday= request.form["birthday"]
            year = int(birthday.split("-")[0])
            now = int((datetime.datetime.now()).strftime('%Y'))

            if year > now - 13:
                err = "Your age must be at least 14!"
                return render_template("signup.html", err=err)
            if birthday == "":
                err = "Birthday field can not be empty!"
                return render_template("signup.html", err=err)

        session["username"] = username
        g.username = username
        print("asd")
        session.permanent = True

        data_username = User.query.filter(User.username == username).first()
        if data_username:
            return redirect(url_for(".store", username=username))
        else:
            user_model = User(username=username, country=country, date=birthday, gender=gender)
            db.session.add(user_model)
            db.session.commit()
            return redirect(url_for(".store", username=username))
        
    return render_template("signup.html")
##### ### End Subsection 3

##### #### Subsection 4: Route for Store
@app.route("/store", methods=['GET', 'POST'])
def store():
    if "username" in session:
        username = session["username"]
        g.username = session["username"]

        if request.method == "POST":
            apps = None

            search_form = request.form["search"]
            sort_by = request.form["sort-by"]
            genre_sort = request.form["genre-sort"]

            if sort_by == "alphabetical":
                apps = Application.query.order_by(Application.name)
            elif sort_by == "price":
                apps = Application.query.order_by(cast(Application.price, Integer).desc())
            elif sort_by == "total-rates":
                apps = Application.query.order_by(cast(Application.rating_count_total, Integer).desc())
            elif sort_by == "user-rating":
                apps = Application.query.order_by(cast(Application.user_rating, Integer).desc())
            if genre_sort != "All":
                apps = apps.filter(Application.genre==genre_sort)   
            if search_form != "":
                apps = apps.filter(Application.name.contains(search_form))

            
            apps = apps.all()
            apps_list = [ app.as_dict() for app in apps ]
            pagination = Pagination(page=1, total=len(apps_list), search=False, record_name='apps_list')
            return render_template("store.html", apps_list=apps_list, username=username, pagination=pagination)

        apps = Application.query.all()
        apps_list = [ app.as_dict() for app in apps ]
        PER_PAGE=12
        search = False
        q = request.args.get('q')
        if q:
            search = True
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1
        i=(page-1)*PER_PAGE
        apps_list1 = apps_list[i:i+12]
        pagination = Pagination(page=page, total=len(apps_list), search=search, record_name='apps_list')

        return render_template("store.html", apps_list=apps_list1, username=username, pagination=pagination)
    else:
        return redirect(url_for(".sign_up"))
##### #### End Subsection 4

@app.route("/store/<id>", methods=['GET', 'POST'])
def app_page(id):
    if "username" in session:
        g.username = session["username"]
        single_app = Application.query.filter(Application.id==id).first()
        reviews = Reviews.query.filter(Reviews.app_id==id).all()
        reviews_list = [ review.as_dict() for review in reviews ]

        if request.method == "POST":
            if "review-txt" in request.form:
                if request.form["review-txt"] == "":
                    err = "Review text can not be empty!"
                username = g.username
                text = request.form["review-txt"]

                review_model = Reviews(username=username, text=text, app_id=id)
                db.session.add(review_model)
                db.session.commit()
                
                return redirect(url_for(".app_page", id=id))

        return render_template("app_page.html", single_app=single_app, reviews_list=reviews_list)

    else:
        return redirect(url_for(".sign_up"))

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if "username" in session:
        username = session["username"]
        g.username = username
        user = User.query.filter(User.username == username).first()
        year = int(user.date.split("-")[0])
        now = int((datetime.datetime.now()).strftime('%Y'))
        age = now - year

        if request.method == "POST":
            if "email" in request.form:
                user.email = request.form["email"]
            if "gender" in request.form:
                user.gender = request.form["gender"]

            db.session.commit()

            return render_template("index.html")

        return render_template("edit_info.html", user=user, age=age)
    else:
        return render_template("index.html")

@app.route("/logout")
def log_out():
    session["username"] = None
    g.username = None
    return redirect(url_for(".index"))

##### End Section 5