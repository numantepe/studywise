from flask import Flask, request, render_template, jsonify, redirect, url_for
import sqlite3
import datetime
import random

DATABASE = "app.db"

#conn = sqlite3.connect("lessons.db")
#
#c = conn.cursor()
#
#c.execute("""CREATE TABLE lessons (
#             course text,
#             topic text,
#             next_recap_date_year integer, 
#             next_recap_date_month integer, 
#             next_recap_date_day integer, 
#             days integer
#          ) """) 
#
#conn.commit()
#conn.close()

# with conn:

##### Auth #####

def create_new_auth_key() -> str:
    all_characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    new_auth_key = ""

    for i in range(random.randint(200, 300)):
        new_auth_key += random.choice(all_characters)
    
    return new_auth_key

def get_username_from_auth_key(db : str, auth : str) -> str:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE auth=:auth", {"auth": auth})

    user = c.fetchone()

    conn.commit()
    conn.close()

    username = user[0]
    
    return username

def is_auth_key_valid(db : str, auth : str) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE auth=:auth", {"auth": auth})
    
    user = c.fetchone()

    conn.commit()
    conn.close()

    if user != None:
        return True
    else:
        return False

##### Lessons #####

def insert_lesson(db : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()
    days = 0

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("INSERT INTO lessons VALUES (:username, :course, :topic, :next_recap_date_year, \
    :next_recap_date_month, :next_recap_date_day, :days)",
    {"username" : username,
    "course" : course, 
    "topic": topic, 
    "next_recap_date_year": today.year, 
    "next_recap_date_month": today.month, 
    "next_recap_date_day": today.day,
    "days": days})

    conn.commit()
    conn.close()

#insert_lesson(DATABASE, "Physics", "Quantum Mechanics")
#insert_lesson(DATABASE, "Biology", "Digestive System")
#insert_lesson(DATABASE, "Geography", "Provinces of Canada")

def update_lesson_finish(db : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE username=:username AND course=:course AND topic=:topic",
    {"username" : username,
    "course": course, 
    "topic": topic})
    lesson = c.fetchone()
    updated_lesson_new_days = lesson[6] + 1
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=updated_lesson_new_days)
    c.execute("UPDATE lessons SET next_recap_date_year=:next_recap_date_year, \
    next_recap_date_month=:next_recap_date_month, \
    next_recap_date_day=:next_recap_date_day, \
    days=:days WHERE course=:course AND topic=:topic",
                {"next_recap_date_year": updated_lesson_new_next_recap_date.year,
                 "next_recap_date_month": updated_lesson_new_next_recap_date.month,
                 "next_recap_date_day": updated_lesson_new_next_recap_date.day,
                 "days": updated_lesson_new_days,
                 "course": course,
                 "topic": topic})

    conn.commit()
    conn.close()

def update_lesson_delay(db : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE username=:username AND course=:course AND topic=:topic",
    {"username" : username,
    "course": course, 
    "topic": topic})
    lesson = c.fetchone()
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=1)
    c.execute("UPDATE lessons SET next_recap_date_year=:next_recap_date_year, \
    next_recap_date_month=:next_recap_date_month, \
    next_recap_date_day=:next_recap_date_day WHERE course=:course AND topic=:topic",
                {"next_recap_date_year": updated_lesson_new_next_recap_date.year,
                 "next_recap_date_month": updated_lesson_new_next_recap_date.month,
                 "next_recap_date_day": updated_lesson_new_next_recap_date.day,
                 "course": course,
                 "topic": topic})

    conn.commit()
    conn.close()

def get_lesson_list_of_todays_schedule(db : str, username : str) -> list:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 
  
    c.execute("SELECT * FROM lessons WHERE username=:username", {"username" : username}) 

    lesson_list = [] 

    for lesson in c.fetchall():
        next_recap_date = datetime.date(lesson[3], lesson[4], lesson[5])
        if next_recap_date <= today:
            lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    conn.commit()
    conn.close()

    return lesson_list

def get_all_lessons(db : str, username : str) -> list:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 
    
    c.execute("SELECT * FROM lessons WHERE username=:username", {"username" : username}) 

    lesson_list = [] 

    for lesson in c.fetchall():
        lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    conn.commit()
    conn.close()

    return lesson_list

def remove_lesson(db : str, username : str, course : str, topic : str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()     

    c.execute("DELETE FROM lessons WHERE username=:username AND course=:course AND topic=:topic", 
    {"username" : username, "course": course, "topic": topic})

    conn.commit()
    conn.close()

def remove_lessons(db : str, username : str, lesson_list_json) -> None:
    for lesson in lesson_list_json:
        remove_lesson(db, username, lesson["course"], lesson["topic"])

##### Users #####

def insert_user(db : str, username : str, email : str, password : str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("INSERT INTO users VALUES (:username, :email, :password, :auth)",
    {"username" : username, 
    "email": email, 
    "password": password, 
    "auth": "LOGGED OUT" 
    })

    conn.commit()
    conn.close()

def set_users_new_auth_key(db : str, username : str, new_auth_key : str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("UPDATE users SET auth=:auth WHERE username=:username", 
    {"auth" : new_auth_key, "username" : username})

    conn.commit()
    conn.close()

def log_out_user(db : str, username : str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("UPDATE users SET auth=:auth WHERE username=:username", 
    {"auth" : "LOGGED OUT", "username" : username})

    conn.commit()
    conn.close()

def does_username_exist(db : str, username : str) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=:username", {"username": username})
    
    user = c.fetchone()

    conn.commit()
    conn.close()

    if user != None:
        return True
    else:
        return False  

def are_credentials_valid(db : str, username : str, password : str) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=:username AND password=:password", 
    {"username": username, "password": password})
    
    user = c.fetchone()

    conn.commit()
    conn.close()

    if user != None:
        return True
    else:
        return False  

##### HTTP Server #####

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/view_all_lessons")
def view_all_lessons():
    return render_template("view-all-lessons.html")

@app.route("/register")
def register():
    return render_template("register.html") 

@app.route("/register/new-user", methods = ["POST"])
def register_new_user():
    new_username = request.form.get("username")

    if not(does_username_exist(DATABASE, new_username)):
        insert_user(DATABASE, new_username, request.form.get("email"), 
        request.form.get("password"))

        new_auth_key = create_new_auth_key()
        set_users_new_auth_key(DATABASE, new_username, new_auth_key)

        return new_auth_key 
    else:
        return "USERNAME NOT UNIQUE"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/existing-user", methods = ["PUT"])
def login_existing_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if does_username_exist(DATABASE, username):
        if are_credentials_valid(DATABASE, username, password):
            new_auth_key = create_new_auth_key()
            set_users_new_auth_key(DATABASE, username, new_auth_key)
            return new_auth_key  
        else:
            return "INCORRECT PASSWORD"
    else:
        return "NO SUCH ACCOUNT"

@app.route("/logout")
def logout():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE, auth_key):
        username = get_username_from_auth_key(DATABASE, auth_key)
    
        log_out_user(DATABASE, username)

    return "Logged out" 

@app.route("/api/lessons/modify", methods = ["POST", "DELETE", "PUT"])
def interact_with_db():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE, auth_key):
        username = get_username_from_auth_key(DATABASE, auth_key)

        if request.method == "POST":
            insert_lesson(DATABASE, username, request.form.get("course"), request.form.get("topic"))
            return "New Lesson Received"
        elif request.method == "DELETE":
            if(request.content_type.startswith('application/json')):
                remove_lessons(DATABASE, username, request.get_json())
                return "Lesson(s) Deleted"
            else:
                remove_lesson(DATABASE, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Deleted"
        elif request.method == "PUT":
            if request.form.get("option") == "finish":
                update_lesson_finish(DATABASE, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Studied Today"
            elif request.form.get("option") == "delay":
                update_lesson_delay(DATABASE, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Delayed to Tomorrow"
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/today", methods = ["GET"])
def send_todays_schedule():
    auth_key = request.headers.get("Authorization")
    
    if is_auth_key_valid(DATABASE, auth_key):
        username = get_username_from_auth_key(DATABASE, auth_key)

        if request.method == "GET":
            lessons_list = get_lesson_list_of_todays_schedule(DATABASE, username) 
            return jsonify(lessons_list)
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/all", methods = ["GET"])
def send_all_lessons():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE, auth_key):
        username = get_username_from_auth_key(DATABASE, auth_key)

        if request.method == "GET":
            lesson_list = get_all_lessons(DATABASE, username) 
            return jsonify(lesson_list)
    else:
        return "INVALID AUTH KEY"

if __name__ == '__main__':
    app.run()
