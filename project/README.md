Documentation for your project in the form of a Markdown file called README.md. This documentation is to be a user’s
manual for your project. Though the structure of your documentation is entirely up to you, it should be incredibly
clear to the staff how and where, if applicable, to compile, configure, and use your project. Your documentation should
be at least several paragraphs in length. It should not be necessary for us to contact you with questions regarding your
project after its submission. Hold our hand with this documentation; be sure to answer in your documentation any questions
that you think we might have while testing your work.



# SECRET SANTA
---------------------------------------------------------------------------------------------------
Secret Santa is a Christmas gift tradition where members of a group (whether it's friends or family) will randomly
draw names to be designated as someone's "Secret Santa". They are given a wishlist of potential gift ideas to give their
gift recipient. Afterwards, the recipient is supposed to guess who was their Secret Santa.

With that in mind, we created this website, Secret Santa, which simplifies this process through a website.

An interactive website that allows users to register accounts, log in, and confirm an email address in order to use.
Once registered and confirmed, users are able to create a 'party' for other users to join with a party code, and
the site will then randomly generate secret santa assignments for this group of people. This website was designed
to be run as a flask application within the CS50 IDE.

# Link to video:
https://youtu.be/ZKzs1KWSk1o

## Table of Contents
* [Technologies & Versions](#Technologies-&-Versions)
* [Flask Usage](#Flask-Usage)
* [Example Party](#Example-Party)
* [Site Usage](#Site-Usage)
* [Notes](#Notes)

### Technologies & Versions
This project is created with:
- Bootstrap 4
- HTML 5 1.1
- Python 3.7.9
- Flask 1.1.2
- Flask-Mail 0.9.1
- Flask-Session 0.3.2
- email-validator 1.1.2
- itsdangerous 1.1.0
- Werkzeug 1.0.1
- cs50 6.0.1
- Jinja2 2.11.2
- SQLAlchemy 1.3.20


### Flask Usage
To run this project, install it as such:
1. download the zip file from Gradescope :)
2. upload the zip files into the CS50 IDE
3. execute 'unzip project.zip' to uncompress the file
4. execute 'rm project.zip' followed by 'y' to delete the ZIP file
5. execute 'cd project' in order to change into that directory
6. execute the following commands into the terminal in order to load the application:
        export FLASK_APP=application
        flask run

### Example Party
We've gone ahead and created a sample party with 3 fake gmail accounts, one of which is the party-creator and the other
two being party-joiners! This way, when you log in, you can see the difference in access for these two types of accounts.
Feel free to click around the navigation bar, update their wishlists, submit hints, draw secret santas... the possibilities
are (almost) endless.

Here is the information for the example party:

Party:
    Name: CS50
    Code: CS50

Party-creator:

    Name: Sam Sung
    Username: samsung
    Email Address: secretsantasamsung@gmail.com
    Email Password: 123ABCabc
    Secret Santa Password: CS50tester

Party-joiners:

    Name: Saad Maan
    Username: saadmaan
    Email Address: secretsantasaadmaan@gmail.com
    Email Password: 123ABCabc
    Secret Santa Password: CS50tester

    Name: Chris P. Bacon
    Username: chrisbacon
    Email Address: secretsantachrispbacon@gmail.com
    Email Password: 123ABCabc
    Secret Santa Password: CS50tester

### Site Usage
##### Register an account + log in:
1. enter username, email, password, and retype your password (make sure it matches all qualifications!)
2. check your email to find the email confirmation link
3. click the link, it will confirm your email
4. navigate to the log in
5. enter username and password, and log in!

##### Forgot Password:
1. Click "Forgot Password" in log-in page
2. Enter username and email
3. Check email for a code
4. Enter username, code, and new password

##### Change Password:
1. Navigate to settings by clicking on your username in the navigation bar
2. Click on "Change Password"
3. Enter your old password and your new password

##### Starting a party:
1. Click "Create" in the navigation bar
2. Enter party name and a join code and click "Create"

##### Joining a party:
1. Click "Join" in the navigation bar
2. Enter a party code

##### Leaving a party:
1. Click "My Party" in the navigation bar
2. Click "Leave Party"

##### My Draw:
1. This page will display who you drew as your secret santa recipient and their wishlist
   (this was randomly generated)

##### Creating a Wishlist:
1. Click the button to add an item
2. Add the name, a description, and a link to the item!
3. If you want to change the order of the items, click the up/down buttons
4. If you want to edit an item, click the edit button next to it, and complete the form
5. If you want to delete an item, click the delete button next to it.

##### Reveal:
1. Enter a hint for your secret santa
2. Click save. If you want to update it at any time, feel free to update with the same portal.
3. When the time comes, click reveal to see the hint for who your secret santa is.

#### Admin Functions
##### Draw names:
1. If admin, navigate to "My Party"
2. Click "Draw" at the bottom of the page

##### Kick out members:
1. Navigate to the "My Party" page
2. Locate the user you wish to kick out of the party
3. Click on the "Kick" button next to their name

##### Send message to members:
1. Navigate to the "My Party" page
2. Locate the user you wish to send a message to
3. Click on "Send Email"
4. Type in message in the pop-up box
5. Hit "Send Email"

##### Secret Santa Reveal Date:
1. Navigate to the "My Party" page
2. Under "Date of Secret Santa Reveal" click "Edit Date"
3. Set a date

##### Change Join Code:
1. Navigate to "My Party"
2. Click on the "Join Code" button
3. Click on "Change Code"
4. Enter your user password and the new join code

### Notes
1. You cannot be in more than one party at a time!
2. If you're the party creator, you're able to send emails to everybody in your party
3. You can also kick people out of your party (we won't tell)
4. Be careful when picking username/email! You can't change it afterwards
