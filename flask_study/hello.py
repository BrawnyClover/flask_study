from flask import Flask, render_template
from urllib import request
from bs4 import BeautifulSoup

# 웹 서버 생성하기
app = Flask(__name__)
@app.route("/")

def hello():
    return render_template('mapShow.html')