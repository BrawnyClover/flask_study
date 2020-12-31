from flask import Flask, render_template, url_for, request, redirect, session
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

# 웹 서버 생성하기
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else :
        if request.method == 'POST':
            username = getname(request.form['username'])
            return render_template('index.html', data=getfollowedby(username))
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else :
        name = request.form['username']
        passw = request.form['password']
        try:
            data = User.query.filter_by(username=name, apssword=passw).first()
            if data is not None : 
                session['logged_in'] = true
                return redirect(url_for('home'))
            else :
                return 'cannot login'
        except :
            return 'cannot login'