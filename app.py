import sqlite3
from flask import Flask, render_template, request, flash, redirect, session
from cryptography.fernet import Fernet
db = sqlite3.connect("database.db", check_same_thread = False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS USERS (USERID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME VARCHAR(20) UNIQUE NOT NULL, PASSWORD VARCHAR(255) NOT NULL)")
db.commit()
app = Flask(__name__)
app.secret_key = "This is an unguessable secret key"
key = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY='
fernet = Fernet(key)

# FLASH MESSAGE CSS
alert_error = "p-3 px-3 bg-red-600 text-white"
warning_error = "p-3 px-3 bg-yellow-400"
success = "p-3 px-3 bg-green-500 text-white"

def isLogged():
	if "isLogged" in session:
		return True
	else:
		return False

# Routes
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/register", methods = ["GET", "POST"])
def register():
	if request.method == "POST":
		username = request.form["username"]
		plain_password = request.form["password"]
		plain_password_confirm = request.form["confirm_password"]
		if plain_password != plain_password_confirm:
			flash("Passwords don't match", warning_error)
			return redirect("/register")
		b = bytes(plain_password, "utf-8")
		password = fernet.encrypt(b)
		cursor.execute("INSERT INTO USERS VALUES (NULL, ?, ?)", (username, password))
		db.commit()
		session["is_Logged"] = True
		session["username"] = username
		flash("Registered successfully!", success)
		return redirect("/")
	else:
		logged = isLogged()
		if logged == True:
			flash("You are already logged in", alert_error)
			return redirect("/")
		return render_template("register.html")
@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		cursor.execute("SELECT PASSWORD FROM USERS WHERE USERNAME = (?)", (username,))
		try:
			encrypted = cursor.fetchall()[0][0]
		except IndexError:
			flash("Username or password are incorrect!", alert_error)
			return redirect("/login")
		if fernet.decrypt(encrypted) == bytes(password, "utf-8"):
			session["isLogged"] = True
			session["username"] = username
			flash("Successfully logged in!", success)
			return redirect("/")
		else:
			flash("Username or password are incorrect!", alert_error)
			return redirect("/login")
		
		return "POST REQUEST"
	return render_template("login.html")
@app.route("/logout")
def logout():
	if "isLogged" in session:
		session.pop("isLogged", None)
		session.pop("username", None)
		flash("Successfully logged out!", success)
		return redirect("/")
	else:
		flash("You are not logged in!", warning_error)
		return redirect("/login")


# Run the app
if __name__ == '__main__':
	app.run(debug = True)