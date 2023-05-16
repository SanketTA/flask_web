from flask import Flask, redirect, url_for, render_template, request, session, g
from datetime import timedelta
import datetime
from datetime import datetime as dt
import sys
import platform
import time
import sqlite3

redirecting = "127.0.0.1"
websites = []
if platform.system() == 'Windows':
    hostpath = "C:\Windows\System32\drivers\etc\hosts"
elif platform.system() == "Linux" or platform.system() == "darwin":
    hostpath = "/etc/hosts"

app = Flask(__name__)
app.secret_key = "sanket@8788"
app.permanent_session_lifetime = timedelta(minutes=1440)
DATABASE = 'websiteblock.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS blocked (id INTEGER PRIMARY KEY AUTOINCREMENT, site_name TEXT UNIQUE, block_time TEXT, block_date TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS unblocked (id INTEGER PRIMARY KEY AUTOINCREMENT, site_name TEXT UNIQUE, unblock_time TEXT, unblock_date TEXT)")
        db.commit()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/About")
def aboutus():
    return render_template("About.html")
  
@app.route("/Contact")
def contactus():
    return render_template("contact.html")

@app.route("/Options")
def options():
    return render_template("options.html")

@app.route("/Login", methods=["POST","GET"])
def Login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            session["user"] = user[0]
            return redirect(url_for("Profile"))
        else:
            return render_template("Login.html", error="Invalid credentials")
    else:
        if "user" in session:
            return redirect(url_for("Profile"))
        return render_template("Login.html")


@app.route("/Profile")
def Profile():
    if "user" in session:
        user = session["user"]
        return render_template("Profile.html", name=user)
    else: 
        return redirect(url_for("Login"))


@app.route("/Logout")
def Logout():
    session.pop("user", None)
    return redirect(url_for("Login"))


@app.route("/Register", methods=["POST", "GET"])
def Registerus():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        
        session["user"] = username
        return redirect(url_for("Profile"))
    else:
        if "user" in session:
            return redirect(url_for("Profile"))
        return render_template("register.html")


@app.route("/Block", methods=["POST","GET"])
def BlockSite():
    if request.method == "POST":
        blocked = request.form["blocked"]

        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%H:%M")
        today = datetime.date.today()
        current_date = today.strftime("%Y-%m-%d")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO blocked (site_name, block_time, block_date) VALUES (?, ?, ?)", (blocked, formatted_time, current_date))
        db.commit()

        if blocked not in websites:
            name = blocked[4:]
            websites.append(blocked)
            websites.append(name)
            websites.append("m."+name)
        god()
    return render_template("block.html")

@app.route("/Timeblock", methods=["POST","GET"])
def Timeblock():
    start = 0
    end = 0
    if request.method == "POST":
        start = int(request.form["start"])
        end = int(request.form["end"])
        session["start"] = start
        session["end"] = end
        timegod(start, end)
        if (start != 0 and end !=0):
            return render_template("Profile.html",start = start, end = end)
    return render_template("Timeblock.html")

@app.route("/Unblock", methods=["POST","GET"])
def UnblockSite():
    if request.method == "POST":
        unblocked = request.form["unblocked"]

        current_time = datetime.datetime.now()
        today = datetime.date.today()
        current_date = today.strftime("%Y-%m-%d")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO unblocked (site_name, unblock_time, unblock_date) VALUES (?, ?, ?)", (unblocked, current_time, current_date))
        db.commit()


        if unblocked in websites:
            name = unblocked[4:]
            websites.remove(unblocked)
            websites.remove(name)
            websites.remove("m."+name)
        god()
    return render_template("unblock.html")

def timegod(start,end):
    if dt(dt.now().year, dt.now().month, dt.now().day,start) < dt.now() < dt(dt.now().year, dt.now().month, dt.now().day,end):
        with open(hostpath, 'r+') as fileptr:
            content = fileptr.read()
            fileptr.seek(0)
            fileptr.truncate()
            for website in websites:
                fileptr.write(redirecting+" "+website+"\n")
    else:
        with open(hostpath, 'r+') as fileptr:
            content = fileptr.read()
            fileptr.seek(0)
            fileptr.truncate()
            for website in websites:
                fileptr.write(redirecting+" "+website+"\n")


def god():
    with open(hostpath, 'r+') as fileptr:
        content = fileptr.read()
        fileptr.seek(0)
        fileptr.truncate()
        for website in websites:
            fileptr.write(redirecting+" "+website+"\n")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
