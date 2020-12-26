# IMPORTING ALL LIBRARIES & FUNCTIONS
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from datetime import datetime
import re
from cs50 import SQL

from helper import login_required, check_confirmed

import random, string

# configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure mail things, thanks to
# https://stackoverflow.com/questions/45540384/flask-mail-error-headers-self-sender-self-reply-to-self-recipients
# https://stackoverflow.com/questions/18881929/flask-mail-gmail-connection-refused
app.config['SECRET_KEY'] = 'my_precious'
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'cs50secretsanta@gmail.com',
    MAIL_PASSWORD = 'thisiscs50',
))

mail = Mail(app)


# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///secretsanta.db")


######## FUNCTIONS
# email confirmation creation, inspired by https://realpython.com/handling-email-confirmation-in-flask/#add-email-confirmation
def send_confirmation(email):

    # generate unique url
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    confirm_url = url_for('confirm_email', token=confirm_serializer.dumps(email), _external=True)

    # put that into email template
    html = render_template('activate.html', confirm_url=confirm_url)

    # make it a valid list type if it isn't already
    if type(email) is not list:
        recipients = email.split()

    # compile everything into a message
    msg = Message("Secret Santa Confirmation", body=html, sender=app.config['MAIL_USERNAME'], recipients=recipients)

    # send the email
    mail.send(msg)

    return "Sent"

# confirm token function
def confirm_token(token, expiration=43200000):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            max_age=expiration
        )
    except:
        return False
    return email

# Send email with code to change password
def emailcode(email, code, username):
    user = db.execute("SELECT name FROM users WHERE username = ?", username)

    # put that into email template
    html = render_template("emailcode.html", user = user[0]["name"], code = code)

    # make it a valid list type if it isn't already
    if type(email) is not list:
        recipients = email.split()

    # compile everything into a message
    msg = Message("Secret Santa Message", body=html, sender=app.config['MAIL_USERNAME'], recipients=recipients)

    # send the email
    mail.send(msg)

    return "Sent"

############### PAGES

####### ACCOUNT
# register an account
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user in"""

    # user submitted via POST
    if request.method == "POST":

        # variables
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        name = request.form.get("name")
        confirmed = False

        # ensure username and password and email submitted
        if not username or not password or not email or not name:
            flash('All fields must be filled out')
            return redirect('/register')

        # ensure username doesn't already exist
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if (len(rows) == 1):
            flash('Username is already taken')
            return redirect('/register')

        # ensure email hasn't already been registered
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if (len(rows) == 1):
            flash('Email has already been registered. Try logging in instead.')
            return redirect('/register')

        # determine if email is valid, (https://pypi.org/project/email-validator/)
        try:
            # validate email
            valid = validate_email(email)

            # update with normalized form
            email = valid.email

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            flash(str(e))
            return redirect('/register')

        # ensure password is valid (https://www.geeksforgeeks.org/python-program-check-validity-password/)
        flag = 0
        while True:
            if (len(password)<8):
                flag = -1
                break
            elif not re.search("[a-z]", password):
                flag = -1
                break
            elif not re.search("[A-Z]", password):
                flag = -1
                break
            elif not re.search("[0-9]", password):
                flag = -1
                break
            else:
                flag = 0
                break

        if flag == -1:
            flash("Invalid password, please try again")
            return redirect("/register")

        # ensure password & confirmation are the same
        if (request.form.get("password") != request.form.get("confirmation")):
            flash('Password and confirmation must be identical')
            return redirect('/register')

        # send confirmation email
        send_confirmation(email)

        # FINALLY store user information into database
        db.execute("INSERT INTO users (username, hash, email, name, confirmed) VALUES (?, ?, ?, ?, ?)", username, generate_password_hash(password), email, name, False)

        # redirect user to unconfirmed registered page
        return render_template("unconfirmed.html")

    # user reached route via GET
    else:
        return render_template("register.html")

# confirming the email address page (https://realpython.com/handling-email-confirmation-in-flask/#update-register-view-function-in-projectuserviewspy-again)
@app.route('/confirm/<token>')
def confirm_email(token):
    # if the confirmation link is wrong or expired
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.')

    # confirm the user
    confirm = db.execute("SELECT confirmed FROM users WHERE email=?", email)
    if confirm[0]['confirmed'] == 0:
        db.execute("UPDATE users SET confirmed = ? WHERE email = ?", True, email)
    return render_template('confirmed.html')

# login with account
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # if user reached route via post
    if request.method == "POST":

        # verify login is valid
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Invalid username or password')
            return redirect("/login")

        # store session information
        session["user_id"] = rows[0]["id"]
        session['USERNAME'] = rows[0]["username"]

        # redirect user to home page
        return redirect("/")

    # user reached route via GET
    else:
        return render_template("login.html")

# homepage baby
@app.route("/")
@login_required
@check_confirmed
def index():
    """Show user's existing information"""
    # define variables for user (taken from login)
    user_id = session["user_id"]
    username = session['USERNAME']

    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]

    return render_template("index.html", username=username, user=user)

# settings
@app.route('/settings')
def settings():
    # select the user from database
    profile = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    return render_template("settings.html", profile=profile, username=session['USERNAME'])

# log out
@app.route("/logout")
def logout():
    """Log user out"""

    # forget user_id
    session.clear()

    #redirect user to login form
    return redirect("/")


######### WISHLIST
# gets the draw's wishlist
@app.route("/mydraw")
@login_required
@check_confirmed
def mydraw():
    # find id of draw
    mydrawid = db.execute("SELECT id FROM users WHERE santa_id = ?", session["user_id"])

    # if no draw, return error
    if (len(mydrawid) == 0):
        flash("You have not drawn a recipient yet. Check again later")
        return redirect("/")

    # if there is a draw
    mydraw = db.execute("SELECT name FROM users WHERE id = ?", mydrawid[0]["id"])
    theirwishlist = db.execute("SELECT * FROM wishlist WHERE userid = ? ORDER BY ranking ASC", mydrawid[0]["id"])

    return render_template("mydraw.html", mydraw=mydraw[0]["name"], theirwishlist=theirwishlist, username=session['USERNAME'])

# gets user's wishlist
@app.route("/mywishlist")
@login_required
@check_confirmed
def mywishlist():
    # select wishlist items
    mywishlist = db.execute("SELECT * FROM wishlist WHERE userid = ? ORDER BY ranking ASC", session["user_id"])
    return render_template("mywishlist.html", mywishlist=mywishlist, username=session['USERNAME'])

# adds item to wishlist
@app.route("/additem", methods=["GET", "POST"])
@login_required
@check_confirmed
def additem():

    # if post
    if request.method == "POST":
        if request.form["submit"] == "add":

            # configure variables
            item = request.form.get("name")
            description = request.form.get("description")
            link = request.form.get("link")

            # establish ranking
            ranking = 1 + db.execute("SELECT COUNT(item) FROM wishlist WHERE userid = ?", session["user_id"])[0]["COUNT(item)"]

            # error if they don't add anything
            if not item:
                flash("must enter name of item")
                return redirect("/mywishlist")

            # save it into database
            db.execute("INSERT INTO wishlist (userid, item, description, link, ranking) VALUES (?,?,?,?,?)", session["user_id"], item, description, link, ranking)
            return redirect("/mywishlist")
    else:
        return redirect("/mywishlist")

# moves item in ranking
@app.route("/moveitem", methods=["GET", "POST"])
@login_required
@check_confirmed
def moveitem():
    # if request method is post
    if request.method == "POST":
        # to move an item up
        if request.form["action"] == "moveup":

            # retrieve information for variables
            itemid = request.form.get("itemid")
            itemranking = db.execute("SELECT ranking FROM wishlist WHERE id=?", itemid)[0]["ranking"]

            # if it's already at the top of the list
            if itemranking == 1:
                return redirect("/mywishlist")

            # move item up relative to other items in wishlist
            temp = itemranking - 1
            otheritemid = db.execute("SELECT id FROM wishlist WHERE userid = ? AND ranking = ?", session["user_id"], temp)[0]["id"]

            db.execute("UPDATE wishlist SET ranking = ? WHERE id = ?", temp, itemid)
            db.execute("UPDATE wishlist SET ranking = ? WHERE id = ?", itemranking, otheritemid)

            return redirect("/mywishlist")
        # to move an item down
        elif request.form["action"] == "movedown":
            # find info for item
            itemid = request.form.get("itemid")
            itemranking = db.execute("SELECT ranking FROM wishlist WHERE id=?", itemid)[0]["ranking"]

            # move item down relative to other items
            temp = itemranking + 1
            otheritem = db.execute("SELECT id FROM wishlist WHERE userid = ? AND ranking = ?", session["user_id"], temp)

            if (len(otheritem) == 0):
                return redirect("/mywishlist")

            otheritemid = otheritem[0]["id"]

            db.execute("UPDATE wishlist SET ranking = ? WHERE id = ?", temp, itemid)
            db.execute("UPDATE wishlist SET ranking = ? WHERE id = ?", itemranking, otheritemid)
            return redirect("/mywishlist")
    else:
        return redirect("/mywishlist")

# edits item in wishlist
@app.route("/edititem", methods=["GET", "POST"])
@login_required
@check_confirmed
def edititem():
    # if request method is post
    if request.method == "POST":
        # to save the new information
        if request.form["submit"] == "save":
            id = request.form.get("itemid")
            item = request.form.get("edititem")
            description = request.form.get("editdescription")
            link = request.form.get("editlink")

            if not item:
                item = db.execute("SELECT item FROM wishlist WHERE id=? AND userid=?", id, session["user_id"])[0]["item"]
            if not description:
                description = db.execute("SELECT description FROM wishlist WHERE id=? AND userid=?", id, session["user_id"])[0]["description"]
            if not link:
                link = db.execute("SELECT link FROM wishlist WHERE id=? AND userid=?", id, session["user_id"])[0]["link"]

            db.execute("UPDATE wishlist SET item = ?, description=?, link=? WHERE id=? AND userid=?", item, description, link, id, session["user_id"])
            return redirect("/mywishlist")
    else:
        return redirect("/mywishlist")

# deletes item in wishlist
@app.route("/deleteitem", methods=["POST"])
@login_required
@check_confirmed
def deleteitem():
    # get id of item
    itemid = request.form.get("itemid")

    # deletes item from wishlist table
    db.execute("DELETE FROM wishlist WHERE id = ?", itemid)

    # redirects user
    flash("Item deleted.")
    return redirect("/mywishlist")

###### PARTY
# Create a party
@app.route("/create", methods=["GET", "POST"])
@login_required
@check_confirmed
def create():
    if request.method == 'POST':
        name = request.form.get("name")
        code = request.form.get("code")
        creator = session["user_id"]

        # Check validity
        if not name:
            return redirect("/create")
        elif not code:
            return redirect("/create")

        # Check unique name
        rows = db.execute("SELECT * FROM parties WHERE name = ?", name)
        if (len(rows) == 1):
            flash('Party name is already taken')
            return redirect('/create')

        # Check unique code
        codes = db.execute("SELECT * FROM parties WHERE code = ?", code)
        if (len(codes) == 1):
            flash('Party code is already taken')
            return redirect('/create')

        # Add to table
        db.execute("INSERT INTO parties (name, code, creator_id) VALUES (?, ?, ?)", name, code, creator)

        # Add creator to party
        partyid = db.execute("SELECT id FROM parties WHERE code = ?", code)
        db.execute("UPDATE users SET party_id = ?, admin = 1 WHERE id = ?", partyid[0]["id"], session["user_id"])

        return redirect("/")
    else:
        # Check is user is already in party
        existing = db.execute("SELECT party_id FROM users WHERE id = ?", session["user_id"])
        if existing[0]["party_id"] != None:
            flash('You cannot be in multiple parties at a time')
            return redirect("/")

        return render_template("create.html")


# Change join code
@app.route("/change_code", methods=["POST"])
@login_required
@check_confirmed
def change_code():
    return render_template("code.html")

# create a new code for the party
@app.route("/new_code", methods=["POST"])
@login_required
@check_confirmed
def new_code():
    # Declare variables
    password = request.form.get("password")
    code = request.form.get("code")

    # Confirm user identity through password
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if not check_password_hash(rows[0]["hash"], password) or len(rows) != 1:
        flash('Invalid password', 'error')
        return redirect("/")

    # Check unique code
    codes = db.execute("SELECT * FROM parties WHERE code = ?", code)
    if (len(codes) == 1):
        flash('Party code is already taken')
        return redirect('/')

    # Update party code
    db.execute("UPDATE parties SET code = ? WHERE creator_id = ?", code, session["user_id"])

    return redirect("/party")


# Join a party
@app.route("/join", methods=["GET", "POST"])
@login_required
@check_confirmed
def join():
    if request.method == "POST":

        code = request.form.get("code")

        # Check that code exists
        rows = db.execute("SELECT * FROM parties WHERE code = ?", code)
        if (len(rows) == 0):
            flash('Code does not exist')
            return redirect('/join')

        # Update database
        partyid = db.execute("SELECT id FROM parties WHERE code = ?", code)
        db.execute("UPDATE users SET party_id = ? WHERE id = ?", partyid[0]["id"], session["user_id"])
        return redirect("/")

    else:
        # Check is user is already in party
        existing = db.execute("SELECT party_id FROM users WHERE id = ?", session["user_id"])
        if existing[0]["party_id"] != None:
            print(existing)
            flash('You have already joined a party')
            return redirect("/")

        return render_template("join.html", username=session['USERNAME'])

# Show party info
@app.route("/party", methods=["GET", "POST"])
@login_required
@check_confirmed
def party():
    partyid = db.execute("SELECT party_id FROM users WHERE id = ?", session["user_id"])

    # Check that member is in a party
    if not (partyid[0]["party_id"]):
        flash('Join a party to continue')
        return render_template("join.html")

    party = db.execute("SELECT name FROM parties WHERE id = ?", partyid[0]["party_id"])
    code = db.execute("SELECT code FROM parties WHERE id = ?", partyid[0]["party_id"])
    members = db.execute("SELECT * FROM users WHERE party_id = ?", partyid[0]["party_id"])
    creator = db.execute("SELECT creator_id FROM parties WHERE id = ?", partyid[0]["party_id"])
    month = db.execute("SELECT month FROM parties WHERE id = ?", partyid[0]["party_id"])
    day = db.execute("SELECT day FROM parties WHERE id = ?", partyid[0]["party_id"])

    if (len(month) == 0):
        month = None
    elif (len(day) == 0):
        day = None
    else:
        month = month[0]["month"]
        day = day[0]["day"]

    admin = db.execute("SELECT admin FROM users WHERE id = ?", session["user_id"])

    if admin[0]["admin"] == 0:
        return render_template("party.html", party = party[0]["name"], members = members, month = month, day = day, username=session['USERNAME'])
    else:
        return render_template("party.html", party = party[0]["name"], members = members, admin = admin[0]["admin"], month = month, day = day, username=session['USERNAME'], code=code[0]['code'])


# leaving the party button
@app.route('/leave', methods=["POST"])
@login_required
@check_confirmed
def leave():
    # clear the party information from the users table
    db.execute("UPDATE users SET party_id = ? WHERE id = ?", None, session['user_id'])

    return redirect('/')

# Draw santas
@app.route("/draw", methods=["GET", "POST"])
@login_required
@check_confirmed
def draw():
    # Get list of everyone in the party
    partyid = db.execute("SELECT party_id FROM users WHERE id = ?", session["user_id"])
    people = db.execute("SELECT id FROM users WHERE party_id = ?", partyid[0]["party_id"])

    copy = []

    # Convert dictionary values to list
    for person in people:
        copy.append(person.get('id'))

    person = copy[0]
    while len(copy) != 0:

        # person chooses someone
        while(True):
            secretSanta = random.choice(copy)
            # Make sure they don't draw their own name
            if secretSanta != person and (len(copy) == 1 or secretSanta != copy[0]):
                break

        # Update database
        db.execute("UPDATE users SET santa_id = ? WHERE id = ?", secretSanta, person)

        # Remove person
        copy.remove(secretSanta)

        # Next loop the selected person chooses their person
        person = secretSanta

    flash("Draw done successfully.")
    return redirect("/party")


##### ADMIN FUNCTIONS
# Delete users
@app.route("/delete", methods=["GET", "POST"])
@login_required
@check_confirmed
def delete():
    if request.method == "POST":
        recipientid = int(request.form["recipientid"])
        # delete that person... tea
        db.execute("UPDATE users SET admin = 0, santa_id = ?, hint = ?, party_id = ? WHERE id = ?", None, None, None, recipientid)
        flash("User kicked from your party.")
        return redirect("/party")
    else:
        return redirect("/party")

# Adds date
@app.route("/date", methods=["GET", "POST"])
@login_required
@check_confirmed
def date():
    if request.method == "POST":

        # get month and day from the form
        month = request.form["month"]
        day = int(request.form["day"])

        # save that into the database for that party
        db.execute("UPDATE parties SET month = ?, day = ? WHERE creator_id = ?", month, day, session["user_id"])
        flash("Secret santa reveal date successfully updated.")

        return redirect("/party")
    else:
        return redirect("/party")

# Sends email
@app.route("/sendemail", methods=["GET", "POST"])
@login_required
@check_confirmed
def sendemail():
    if request.method == "POST":

        # establish variables
        email = db.execute("SELECT email FROM users WHERE id = ?", int(request.form["recipientid"]))[0]["email"]
        message = request.form["message"]
        origin = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])[0]["name"]
        recipient = db.execute("SELECT name FROM users WHERE id = ?", int(request.form["recipientid"]))[0]["name"]

        # put that into email template
        html = render_template('email.html', message=message, origin=origin, recipient=recipient)

        # make it a valid list type if it isn't already
        if type(email) is not list:
            recipients = email.split()

        # compile everything into a message
        msg = Message("Secret Santa Message", body=html, sender=app.config['MAIL_USERNAME'], recipients=recipients)

        # send the email
        mail.send(msg)

        flash("Email sent.")
        return redirect("/party")

####### SANTA REVEAL
@app.route("/reveal", methods=["GET", "POST"])
@login_required
@check_confirmed
def reveal():
    # user got there via post
    if request.method == "POST":

        # store hint into database
        db.execute("UPDATE users SET hint = ? WHERE id = ?", request.form.get("hint"), session["user_id"])

        # flash successful message
        flash('Successfully updated hint!')
        return redirect("/reveal")

    else:
        # retrieve secret santa hint
        santa_id = db.execute("SELECT santa_id FROM users WHERE id = ?", session ['user_id'])
        hint_db = db.execute("SELECT hint FROM users WHERE id = ?", santa_id[0]['santa_id'])
        if not hint_db:
            hint = None
        else:
            hint = hint_db[0]['hint']
        # render template
        return render_template("reveal.html", username=session['USERNAME'], hint=hint)

# Redirects user to password change page
@app.route("/change_request", methods=["GET", "POST"])
@login_required
@check_confirmed
def change_request():
    if request.method == "POST":
        return render_template("change.html")
    else:
        return render_template("settings.html")

# Form to change password when already logged in
@app.route("/p_change", methods=["GET", "POST"])
@login_required
@check_confirmed
def p_change():
    if request.method == "POST":
        # Declare variables
        old = request.form.get("old")
        new = request.form.get("password")
        confirm = request.form.get("confirm")

        # Check old password is correct
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(rows[0]["hash"], old) or len(rows) != 1:
            flash('Invalid password', 'error')
            return redirect("/settings")

        # Ensure password is valid (https://www.geeksforgeeks.org/python-program-check-validity-password/)
        flag = 0
        while True:
            if (len(new)<8):
                flag = -1
                break
            elif not re.search("[a-z]", new):
                flag = -1
                break
            elif not re.search("[A-Z]", new):
                flag = -1
                break
            elif not re.search("[0-9]", new):
                flag = -1
                break
            else:
                flag = 0
                break

        if flag == -1:
            flash("Invalid password, please try again")
            return redirect("/reset")

        # Check passwords match
        if new != confirm:
            flash('Passwords must match')
            return render_template("p_change.html")

        # Update password
        hashed = generate_password_hash(new)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed, session["user_id"])

        return redirect("/")
    else:
        return render_template("change.html")

# Redirects user to password reset page request
@app.route("/forgot_p", methods=["GET", "POST"])
def forgot_p():
    if request.method == "POST":
        return render_template("resetrequest.html")
    else:
        return render_template("login.html")

# Change password request
@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    # user submitted via POST
    if request.method == "POST":

        # Declare variables
        username = request.form.get("username")
        x = db.execute("SELECT * FROM users WHERE username = ?", (username))
        email = request.form.get("email")

        # Enter password twice
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not request.form.get("username"):
            print("Must provide username.")
            return

        # Check if username already exists
        elif len(x) == 0:
            print("Username does not exist.")
            return

        # Check if username and email match up
        elif db.execute("SELECT id FROM users WHERE username = ?", username) != db.execute("SELECT id FROM users WHERE email = ?", email):
            print("Username or email invalid.")
            return

        # Generate random code
        N = 7
        code = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k = N))

        # Store code in user's database
        db.execute("UPDATE users SET password_code = ? WHERE username = ?", code, username)

        # Send email
        emailcode(email, code, username)

        return render_template("reset.html")

    else:
        return render_template("login.html")

# Confirm code and reset password
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        # Declare variables
        username = request.form.get("username")
        code = request.form.get("code")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Confirm field input
        if not username or not code or not password or not confirm:
            flash('Enter enter all fields')
            return render_template("reset.html")

        # Confirm user
        user = db.execute("SELECT * FROM users WHERE username = ?", (username))
        if len(user) == 0:
            flash('User does not exist')
            return render_template("reset.html")

        # Check code
        checkCode = db.execute("SELECT password_code FROM users WHERE username = ?", username)
        if code != checkCode[0]["password_code"]:
            flash('Invalid code')
            return render_template("login.html")

        # Ensure password is valid (https://www.geeksforgeeks.org/python-program-check-validity-password/)
        flag = 0
        while True:
            if (len(password)<8):
                flag = -1
                break
            elif not re.search("[a-z]", password):
                flag = -1
                break
            elif not re.search("[A-Z]", password):
                flag = -1
                break
            elif not re.search("[0-9]", password):
                flag = -1
                break
            else:
                flag = 0
                break

        if flag == -1:
            flash("Invalid password, please try again")
            return redirect("/reset")

        # Check passwords match
        if password != confirm:
            flash('Passwords must match')
            return render_template("reset.html")

        # Update password
        hashed = generate_password_hash(password)
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hashed, username)

        return render_template("login.html")

    else:
        return render_template("reset.html")