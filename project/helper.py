import os
import requests
import urllib.parse

from flask import Flask, flash, redirect, render_template, request, session, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///secretsanta.db")



#### FUNCTIONS

# requires login
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function

# checks to see if the user has confirmed their email
def check_confirmed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        status = db.execute("SELECT confirmed FROM users WHERE id=?", user_id)
        if status[0]['confirmed'] == 0:
            return render_template('unconfirmed.html')
        return f(*args, **kwargs)
    return decorated_function