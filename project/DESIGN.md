A “design document” for your project in the form of a Markdown file called DESIGN.md that
discusses, technically, how you implemented your project and why you made the design decisions
you did. Your design document should be at least several paragraphs in length. Whereas your
documentation is meant to be a user’s manual, consider your design document your opportunity
to give the staff a technical tour of your project underneath its hood.


# IMPLEMENTATION
--------------------------------------------------------------------------------------------

## Web Development Things
* [Front End](#Front-End)
* [Back End](#Back-End)

## Website Table of Contents
* [Register](#Register)
* [Log In](#Log-In)
* [Index](#Index)
* [Join](#Join)
* [Create](#Create)
* [My Party](#My-Party)
* [My Draw](#My-Draw)
* [My Wishlist](#My-Wishlist)
* [Reveal](#Reveal)

### Front-End
The CSS and HTML for this site borrow heavily from Bootstrap 4, which provided a lot of very helpful
components that were integrated into this site. We decided to go with a red theme for pretty much
everything due to the Christmas theme of our project. We also wanted the pages to look good on mobile,
which Bootstrap was very helpful with. Finally, we wanted to make everything structured very clearly
on our site, so everything is organized via the navigation bar at the top of the site, and the pages
are relatively simple and straightforward. We created the icon/nav bar and set it up in an HTML template
called layout.html, and then we extended it for the rest of the HTML pages. However, for index, we did
not use this template because the home page did not fit into the container that we used for the rest of
the pages.

We also used Bootstrap to make the page adjust dynamically to the size of the screen being used, so the nav
bar collapse into a toggle if the browser is made much more narrow, and the rest of the site also adjusts to
the width of the browser. This allows for a more user-friendly experience!

### Back-End
The back end of the site is implemented via a Python library called flask, as well as SQL from cs50's library.
We stored all of our information in tables in a SQL database called secretsanta.db. Importantly, we use
session from flask in order to store the user's username and id, which allows us to index into the database
depending on the page the user is on and the function they are calling. In our database, we have 3 tables:
first is the user table, which stores the user's unique id, username, password hash, email, name, the
id of their randomly assigned secret santa, whether or not they are an admin (as a boolean), whether or not
the user is confirmed (also as a boolean), their corresponding hint, their party_id, and their potential
password-reset code. This table stores all the information that is pertinent to each individual person, and
the santa_id is correlated to another user in the same table. Additionally, there is a wishlist table that is
linked to this table by the user's id, which is unique. We did this because it allows each individual to input
as many things as they want into their wishlist, and it is still accessible via the user_id. Finally, there is
a table storing the parties, their join codes, the id of the creator, and the month&day of the end of the party.
This is helpful for displaying all the pertinent party information for each user after they log in, since the
id of the party is correlated with the "party_id" column for each user in the users table. This allows many individuals
in the users table to be correlated with one party, which is necessary. Overall, this method of storing information
allows all necessary data to be accessible by users for their web experience and it allows customization of
wishlist and party size for each user and party respectively.

#### Register
The first page of the site that the user will be sent to is the register page.
###### input + user feedback + storing things in the database
Here, they are asked to input their name, username, email, and then set a password (and confirm the password).
We wanted to implement password requirements, there is a dynamic pop-up box that includes the requirements for
the password. As the password fulfills the requirements, the text and icon in the box turns green like
some sort of positive feedback. We chose to use the "flash" function from flask in order to give the
user feedback if they attempt to submit information that either is not valid (such as the email) or
does not comply with the password requirements, which should improve user experience and redirect them
towards proper usage of the site. We also check to see if the user hasn't already tried to log in. The
information is stored in a table called "users" in the secret santa database. The password is hashed with
werkzeug security's hash and then stored for security.
###### email confirmation
We also implemented a form of email confirmation, which was implemented via an additional function (called
send_confirmation()) which generates a unique URL based off of the user's email address input and emails it to
them. This was created because we allow users to send and receive information based on their party via
their email, so users need to be able to access an email. This also confirms that the account belongs to
somebody, and prevents people from making a ton of accounts for no reason. In order to ensure that the user
is confirmed (via email), there is another column of the users table called "confirmed", which is just a boolean
value that determines whether or not the user actually clicked on the link in their email. There is a decorator
in the helper.py file that ensures the user is confirmed by checking the database. If the user did click on their
link, the database is updated and the "confirmed" value is switched to True, and they're allowed to log in and access
the rest of the site!! (done via the confirm_emailfunction). For all of the email confirmation, we used the
URLSafeTimedSerializer from itsdangerous, because we're sending a link to an unknown address of unknown safety.
We also used flask_mail in order to send the emails, and we had to do a lot of mail configuration in order to set it up
and send emails via an account that was created and called cs50secretsanta@gmail.com, which is the account used
to send emails for everything in this website. We decided to implement the confirmation in this way because it
was relatively user-friendly in that the user simply has to go to their email and click on a link, and it is relatively
safe because they have a unique link generated based on their email address. It also ensures the user has access
to an email that works. Using a decorator to safeguard the actual pages of the site ensures the user needs to confirm
their email prior to joining any parties, but it ensures that they know they have an account, they just need to
confirm their email, and they are notified of this in the updates sidebar on the home page.

#### Log In
After the user is registered, the log-in function is fairly simple. It simply takes the username/password submitted
from the log in page by the user and checks it against existing accounts in the database (using the
check_password_hash() function from werkzeug security). If the user logs in with the correct credentials, then they
are directed to the home page and their unique user_id is stored, as well as their username into the user's
session. This universalizes the user's username and id during their session in the site, and when they log out their
information is cleared. This allows the user to access different pages during their one session and personalizes
their experience. If their log in credentials are not valid, then they are flashed a message that says
'Invalid username or password' -- whether or not the vagueness is better for security is debatable, but it provides
some user feedback for if they fail to log in. Additionally, at the bottom of the log in page is a "Forgot Password"
link, which alllows users to reset their password if they need to.
###### password reset
If the user has forgotten their password, we redirect them to a page where they can submit a request to get a new password.
The user enters their email and username, and we confirm they relate to the same user and send them a randomized code via email.
This requires the user to check their email, which ensures that it is the same user (to a degree, at least). This code is created and then stored in
the users table in the database, and is entirely randomly generated, which makes it practically impossible to guess.
Once the user inputs this code via a form, it is checked against the information stored in the database. If it is correct,
then they are allowed to create their new password and confirm it. Then, they are redirected to the login page where they can log in
with these new credentials.

#### Index
This page is the landing page for users on the site. Once logged in, users are able to see a welcome message, along with an updates bar.
Bootstrap grid design was used to organize this page. In the updates bar, users will see updates based on the status of their account and party.
For example, if the user has not yet confirmed their email, they will see a message prompting them to do so. This information on the user is retrieved
from the users table using the session id.

#### Settings
##### Change Password
Within the settings page, users have the option of changing their password. When they click on the "Change Password" button, they will be redirected
to a form that asks them for their old password and new password. The program will check to ensure that the old password matched with the one
stored in the row corresponding to the user's id. Next, it will validate that the new password before updating it in the database.

#### Join
Similar to "Create," the program first checks if the user is already part of an existing party by pulling the party_id from their row.
If not, the user is then prompted to enter a join code. After checking to make sure that the code the user entered exists in the database,
the party_id of the user is updated to the id of that party.

#### Create
Each user is allowed to create their own own party and come up with a join code that others can use to join their party.
Since each person is only allowed to be in one party to prevent complications and overlaps, when the user first clicks on the "Create" button,
the program checks if they are already in a previous party by checking if their party_id is NULL or not. If this field is empty,
the "create" function proceeds and enters a new row into the "parties" table, logging the current user as the creator. It checks to make sure that
both the party name and code are unique and haven't been taken before so that there's no confusion when a user is trying to join a party.
Then, party_id is updated in the "users" table and because the user was the one to create the party, they are given admin status, a boolean value.

#### My Party
This page displays all the information about the user's party. If they are not in a party, they will be redirected to the join page and prompted
to enter a party join code. Once they have a party id, this page will display all the members of their party and their contact information.
We also show the date that the draw was made. Using the admin status and conditions in the html page, the creator of the party will see a different page.
If the user is the admin of the party, they receive special abilities including setting the date of the draw, kicking members out,
sending a message to any of the members, and making the draw.

##### reveal date
Only admin are able to edit the end date of the party. If an admin clicks on Edit Date (a button only visible to them), a Bootstrap modal form pops up.
In this form, admin can see drop-down menus for month and day. When this form is submitted, the date function is called. This function updates the month and day
in the parties table of the party whose id corresponds with the party_id of the user. After the form is submitted, the user is redirected to /party, and
a flash message appears notifying them that the date has been successfully updated.

##### edit join code
The admin can edit the join code of the party. When they click on the "Change Code" button, they are redirected to a page request form where they
can enter their password, which is used as extra security to validate their identity, and the new join code. We select their current
password from the database to ensure that it matches up then update the "parties" table to replace the old code with the new code
that the user entered.

##### kick members
Only admin have access to this ability. On the My Party page, Admin will see a button next to each user that says "Kick". If the admin clicks on this button,
a modal will pop up asking the admin if they are sure they would like to do this. When they click "Yes," the delete function is called. The function
first retrieves the id of the user that is to be deleted from the party, which is included as a hidden input field in the modal form that popped up earlier.
Then, the function updates the users database such that the party_id, santa_id, admin, and hint fields for the person to be kicked are set to NULL
(aka None in python). Then, the user is redirected to /party, and a flash message appears confirming that the person has been kicked from the party.

##### send email
Only admin have access to this ability. On the My Party page, admin will see a button next to each user that says "Send Email." If the admin clicks on this
button, a modal form will pop up with a text field that allows them to type in a message to the person they are sending the email to. When the admin clicks
"Send Email," the modal form is submitted. At this point, the sendemail function is called. This function first retrieves the email address of the user
being sent an email by accessing the users table and selecting for the user with the correct id. The id of the person being sent an email is known because
it is included as a hidden input field in the modal form that the admin submitted. Then, the function stores the message from the form in a variable. Finally,
it stores the names of both the sender and the sendee by identifying the user with the corresponding user id from the users table. After this is done, the
function renders an email template named email.html. This rendering swaps in the message and names of the sender and sendee into the correct places in the
template. Next, the list of recipients is checked to see if it is valid; if not, split is used to make it valid. After this is done, the email message
and all other components of the email (e.g. recipients) are compiled into a final email. This email is then sent using the cs50secretsanta@gmail.com email
address. A common email address is used to send all emails from this website to provide uniformity and professionalism -- and also to prevent users from
having to reveal/use their own personal information and email addresses. At this point, the admin is redirected to /party, and a flash message appears that
notifies them that the email has successfully been sent.

##### leave
If the individual wants to leave the party, then they need to click on the button at the bottom of the "my party" page. Then, a modal will pop open asking
them to confirm. This is to confirm that the user wants to leave the party. If so, then the button submits a post request that goes into the 'users' table
and clears the party id for that user, setting it to None, which then means they are no longer in a party. They are redirected to the home page, where they
are welcome to start their own party or join a different one (or rejoin the party they just left, if they so choose).

#### My Draw
##### draw function
After the admin clicks the "draw" button on the "My Party" page, the draw function will be called. The program selects all the people who have the same
party_id that the admin does (or everyone in their party). Using a function from the "random" library, the program randomly selects a name out
of the list. We have a condition to ensure that no one draws themselves. Next, there is a field in the users table called "santa_id" which denotes
the id of the person who is giving the user the gift. Thus, if person A draws person B, the santa_id in B's row will correspond to the user id of A.
Finally, the person drawn will be removed from the list of names and the program will repeat the random assignment until there is no one left.
##### draw page
Users will be able to navigate to the "My Draw" page where they can see the name of the person that they drew as well as the person's wishlist.
The wishlist of the person that they drew is retrieved by identifying the user id of whichever person that has a santa_id that matches the user's id.
This person's wishlist is then identified by retrieving all items from the wishlist table that have a user_id equivalent to this person's id.
This list of items is then used to render the my draw page.

#### My Wishlist
When the user is directed to /mywishlist, the mywishlist function is called. This function uses the session's user_id to generate a list of item from the
wishlist table that have a user id corresponding to that id. Moreover, the function orders this list by ranking, such that the highest rank (1) is at the top.
This wishlist is then used to render mywishlist.html, which displays each item in a table. For each item, this page includes the ranking, name, description,
and link to the item. Buttons to edit, delete, or move each item are included. Finally, an add item button is included at the bottom of the page.

##### Move Item
Next to each item in the wishlist is an up arrow and a down arrow. Both of these arrows are included in the same form. When either button is pressed,
the form is submitted. At this point, the moveitem function is called. This function checks to see which button was pressed based on its value.
Then, it gets the ranking of the item from the wishlist table. After this, it finds the item id of the item whose ranking it will swap with (either the item
with ranking of one higher or one lower, depending on whether the move up or move down button was pressed). Using a temp variable, these two rankings are then
swapped. Thus, the two items are switched in the wishlist order.

##### Edit Item
The edit button is present next to each item in the wishlist. When pressed, it opens up a modal form with fields for name, description, and link of the item.
Placeholder values for each of those fields are already included. If the user does not wish to update those fields, then the user simply doesn't need to type
anything in them. When the user submits this form, the edititem function is called. This function stores the submitted values for each of these three fields
in variables.It then checks to see if any of them are empty; if they are, then it is assumed that the user does not want to change that field, so the value
of the variable is switched to the existing value of that field in the wishlist table. Then, the wishlist table is updated so that the fields of the item
with the corresponding id is updated to the new values of item (aka name), description, and link.

##### Add Item
The add button works similarly to the edit button. A modal form is provided. Once submitted, the values of the fields from that form are used to update the
item with the corresponding id in the wishlist table.

##### Delete Item
The delete button submits a form that has a hidden input field containing the item's id. Then, the deleteitem function is called. When this function is called,
the id of the item, retrieved from the form, is used to delete the corresponding row of the item in the wishlist table. At this point, the user is redirected
to the /wishlist page.

#### Reveal
Part of secret santa is guessing who each person's secret santa was at the very end of the game. The Reveal page of the site
anonymously trades hints for each person's secret santa's identity. This is done with yet another column of the users table
which includes a "hint" that is inputted via a form from this page (and again, flash is used for user feedback). Using Jinja
templates, we swap hints for individuals by indexing into the users table, first by finding the santa_id, and then the hint
based on the id of that individual, and then displays that in a pop-up modal on that page. This allows party members to more
easily swap hints and guess who their secret santa was at the end of the party. It is created this way, by trading information
from the user table, in order to keep the secret santa themself anonymous, but portray the hint that they entered.