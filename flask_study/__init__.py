from flask import Flask, render_template, url_for, request, redirect, session
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime, base64
import sys, os, shutil
from urllib.parse import unquote

# 웹 서버 생성하기
app = Flask(__name__)

UPLOAD_DIR = "\static\profile_image"

app.config['SECRET_KEY'] = 'flask_study'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_DIR'] = UPLOAD_DIR
db = SQLAlchemy(app)

class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(100), default=os.path.join(UPLOAD_DIR, 'default.png'))

    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, email, password, profile_image, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        self.profile_image = profile_image

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email}')>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Post(db.Model):
    __table_name__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique = True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Post('{self.id}', '{self.title}')>"

@app.route("/")
def home():
    posts = Post.query.all()

    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    email = request.form['email']
    passw = request.form['password']
    login_success = False

    data = User.query.filter_by(email=email)
    for user in data:
        if user.check_password(passw) is True:
            login_success = True
            current_user = user

    if login_success is True : 
        session['logged_in'] = True
        session['user_email'] = email
        session['username'] = current_user.username
        return redirect(url_for('home'))
    else :
        return "<div>"+email+"</div>"+"<div>"+passw+"</div>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/edit_post', methods=['GET','POST'])
def edit_post():
    user_email = session['user_email']
    title = request.form['title']
    article = request.form['article']

    author = User.query.filter_by(email=user_email).first()
    
    new_post = Post(title=title, content=article, author=author)

    try: 
        db.session.add(new_post)
        db.session.commit()
    except:
        db.session().rollback()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else :
        name = request.form['username']
        email = request.form['email']
        passw = request.form['password']
        is_profile_set = request.form.get('is_profile_set')
        if is_profile_set is None :
            profile_image = "default.png"
            
        else :
            profile_image = name + ".png"

        path = os.path.join("static/profile_image/", profile_image)

        if is_profile_set is not None :
            shutil.copyfile(
            os.path.join("flask_study/static/profile_image/", "temp_profile.png"),  
            "flask_study/" + path)
        
        

        new_user = User(username=name, email=email, password=passw, profile_image=str(path))
        try: 
            db.session.add(new_user)
            db.session.commit()
        except:
            db.session().rollback()
        return redirect(url_for('home'))



@app.route('/temp_profile_image', methods=['POST'])
def save_temp_image():
    raw_data = unquote(request.get_data().decode("utf-8"))
    starter = raw_data.find(',')
    ender = raw_data.find("&enctype")
    image_data = raw_data[starter+1:ender]
    print("======================================")
    print(image_data)
    print("======================================")
    tmp_profile_image_path = os.path.join("flask_study/static/profile_image/", "temp_profile.png")
    with open(tmp_profile_image_path, "wb") as fh:
        fh.write(base64.decodebytes(image_data.encode("utf-8")))
    return str("success")