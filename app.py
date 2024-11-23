from flask import Flask, Blueprint, request, render_template, redirect, url_for, jsonify
from user import user_bp  # Import the user blueprint
from admin import admin_bp  # Import the admin blueprint
from bank import bank_bp 
from datetime import timedelta

app = Flask(__name__)

app.register_blueprint(user_bp, url_prefix='/user')  # 使用 '/user' 前綴註冊 user 藍圖
app.register_blueprint(admin_bp, url_prefix='/admin')  # Routes in admin will be prefixed with '/admin'
app.register_blueprint(bank_bp, url_prefix='/bank')  # 使用 '/user' 前綴註冊 user 藍圖

# Set the secret key and session configurations
app.secret_key = 'your_secret_key'  # Secret key for signing cookies
app.config.update(
        SESSION_COOKIE_NAME='session',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)



@app.route('/')
def home():
    return render_template('home.html')  # Home page with 4 buttons: Register, Login, Loans, Credit Card

if __name__ == '__main__':
    app.run(debug=True, port=6661)
