from flask import Flask
from flask import render_template, redirect

app = Flask(__name__)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/home')
def home():
    return redirect("/home/active")


@app.route('/home/active')
def home_active():
    return render_template('home.html', type="active")


@app.route('/home/completed')
def home_completed():
    return render_template('home.html', type="completed")
