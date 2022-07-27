from flask import Flask, request, render_template, jsonify
# import sqlite3
import datetime
import random

DATABASE = "app.db"

import os
import urllib.parse as up
import psycopg2

up.uses_netloc.append("postgres")
DATABASE_URL = up.urlparse(os.environ["DATABASE_URL"])

#conn = psycopg2.connect(database=db_url.path[1:],
#                        user=db_url.username,
#                        password=db_url.password,
#                        host=db_url.hostname,
#                        port=db_url.port)
#
#c = conn.cursor()

#c.execute("""CREATE TABLE lessons (
#            username text,
#            course text,
#            topic text,
#            next_recap_date_year integer, 
#            next_recap_date_month integer, 
#            next_recap_date_day integer, 
#            days integer);""")
#
#c.execute("""CREATE TABLE users (
#            username text,
#            email text,
#            password text,
#            auth text);""")

#conn.commit()
#conn.close()

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

def get_username_from_auth_key(db_url : str, auth : str) -> str:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE auth=%s", (auth,))

    user = c.fetchone()

    conn.commit()
    conn.close()

    username = user[0]
    
    return username

def is_auth_key_valid(db_url : str, auth : str) -> bool:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE auth=%s", (auth,))
    
    user = c.fetchone()

    conn.commit()
    conn.close()

    if user != None:
        return True
    else:
        return False

##### Lessons #####

def insert_lesson(db_url : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()
    days = 0

    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 

    c.execute("INSERT INTO lessons (username, course, topic, next_recap_date_year, \
    next_recap_date_month, next_recap_date_day, days) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    (username, course, topic, today.year, today.month, today.day, days))

    conn.commit()
    conn.close()

#insert_lesson(DATABASE, "Physics", "Quantum Mechanics")
#insert_lesson(DATABASE, "Biology", "Digestive System")
#insert_lesson(DATABASE, "Geography", "Provinces of Canada")

def update_lesson_finish(db_url : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE username=%s AND course=%s AND topic=%s",
    (username, course, topic))
    lesson = c.fetchone()
    updated_lesson_new_days = lesson[6] + 1
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=updated_lesson_new_days)
    c.execute("UPDATE lessons SET next_recap_date_year=%s, \
    next_recap_date_month=%s, \
    next_recap_date_day=%s, \
    days=%s WHERE course=%s AND topic=%s",
                (updated_lesson_new_next_recap_date.year,
                 updated_lesson_new_next_recap_date.month,
                 updated_lesson_new_next_recap_date.day,
                 updated_lesson_new_days,
                 course,
                 topic))

    conn.commit()
    conn.close()

def update_lesson_delay(db_url : str, username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE username=%s AND course=%s AND topic=%s",
    (username, course, topic))
    lesson = c.fetchone()
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=1)
    c.execute("UPDATE lessons SET next_recap_date_year=%s, \
    next_recap_date_month=%s, \
    next_recap_date_day=%s WHERE course=%s AND topic=%s",
                (updated_lesson_new_next_recap_date.year,
                 updated_lesson_new_next_recap_date.month,
                 updated_lesson_new_next_recap_date.day,
                 course,
                 topic))

    conn.commit()
    conn.close()

def get_lesson_list_of_todays_schedule(db_url : str, username : str) -> list:
    today = datetime.date.today()

    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 
  
    c.execute("SELECT * FROM lessons WHERE username=%s", (username,)) 

    lesson_list = [] 

    for lesson in c.fetchall():
        next_recap_date = datetime.date(lesson[3], lesson[4], lesson[5])
        if next_recap_date <= today:
            lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    conn.commit()
    conn.close()

    return lesson_list

def get_all_lessons(db_url : str, username : str) -> list:
    today = datetime.date.today()

    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 
    
    c.execute("SELECT * FROM lessons WHERE username=%s", (username,)) 

    lesson_list = [] 

    for lesson in c.fetchall():
        lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    conn.commit()
    conn.close()

    return lesson_list

def remove_lesson(db_url : str, username : str, course : str, topic : str) -> None:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()     

    c.execute("DELETE FROM lessons WHERE username=%s AND course=%s AND topic=%s", 
    (username, course, topic))

    conn.commit()
    conn.close()

def remove_lessons(db_url : str, username : str, lesson_list_json) -> None:
    for lesson in lesson_list_json:
        remove_lesson(db, username, lesson["course"], lesson["topic"])

##### Users #####

def insert_user(db_url : str, username : str, email : str, password : str) -> None:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor() 

    c.execute("INSERT INTO users (username, email, password, auth) VALUES (%s, %s, %s, %s)",
    (username, email, password, "LOGGED OUT" ))

    conn.commit()
    conn.close()

def set_users_new_auth_key(db_url : str, username : str, new_auth_key : str) -> None:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("UPDATE users SET auth=%s WHERE username=%s", 
    (new_auth_key, username))

    conn.commit()
    conn.close()

def log_out_user(db_url : str, username : str) -> None:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("UPDATE users SET auth=%s WHERE username=%s", 
    ("LOGGED OUT", username))

    conn.commit()
    conn.close()

def does_username_exist(db_url : str, username : str) -> bool:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=%s", (username,))
    
    user = c.fetchone()

    conn.commit()
    conn.close()

    if user != None:
        return True
    else:
        return False  

def are_credentials_valid(db_url : str, username : str, password : str) -> bool:
    conn = psycopg2.connect(database=db_url.path[1:],
                        user=db_url.username,
                        password=db_url.password,
                        host=db_url.hostname,
                        port=db_url.port)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=%s AND password=%s", 
    (username, password))
    
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

    if not(does_username_exist(DATABASE_URL, new_username)):
        insert_user(DATABASE_URL, new_username, request.form.get("email"), 
        request.form.get("password"))

        new_auth_key = create_new_auth_key()
        set_users_new_auth_key(DATABASE_URL, new_username, new_auth_key)

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

    if does_username_exist(DATABASE_URL, username):
        if are_credentials_valid(DATABASE_URL, username, password):
            new_auth_key = create_new_auth_key()
            set_users_new_auth_key(DATABASE_URL, username, new_auth_key)
            return new_auth_key  
        else:
            return "INCORRECT PASSWORD"
    else:
        return "NO SUCH ACCOUNT"

@app.route("/logout")
def logout():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE_URL, auth_key):
        username = get_username_from_auth_key(DATABASE_URL, auth_key)
    
        log_out_user(DATABASE_URL, username)

    return "Logged out" 

@app.route("/api/lessons/modify", methods = ["POST", "DELETE", "PUT"])
def interact_with_db():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE_URL, auth_key):
        username = get_username_from_auth_key(DATABASE_URL, auth_key)

        if request.method == "POST":
            insert_lesson(DATABASE_URL, username, request.form.get("course"), request.form.get("topic"))
            return "New Lesson Received"
        elif request.method == "DELETE":
            if(request.content_type.startswith('application/json')):
                remove_lessons(DATABASE_URL, username, request.get_json())
                return "Lesson(s) Deleted"
            else:
                remove_lesson(DATABASE_URL, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Deleted"
        elif request.method == "PUT":
            if request.form.get("option") == "finish":
                update_lesson_finish(DATABASE_URL, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Studied Today"
            elif request.form.get("option") == "delay":
                update_lesson_delay(DATABASE_URL, username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Delayed to Tomorrow"
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/today", methods = ["GET"])
def send_todays_schedule():
    auth_key = request.headers.get("Authorization")
    
    if is_auth_key_valid(DATABASE_URL, auth_key):
        username = get_username_from_auth_key(DATABASE_URL, auth_key)

        if request.method == "GET":
            lessons_list = get_lesson_list_of_todays_schedule(DATABASE_URL, username) 
            return jsonify(lessons_list)
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/all", methods = ["GET"])
def send_all_lessons():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(DATABASE_URL, auth_key):
        username = get_username_from_auth_key(DATABASE_URL, auth_key)

        if request.method == "GET":
            lesson_list = get_all_lessons(DATABASE_URL, username) 
            return jsonify(lesson_list)
    else:
        return "INVALID AUTH KEY"

if __name__ == '__main__':
    app.run()
