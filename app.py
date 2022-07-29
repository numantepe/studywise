from flask import Flask, request, render_template, jsonify, g
import datetime
import random
import os
import urllib.parse as up
import psycopg2

##### Auth #####

def create_new_auth_key() -> str:
    all_characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    new_auth_key = ""

    for i in range(random.randint(200, 300)):
        new_auth_key += random.choice(all_characters)
    
    return new_auth_key

def get_username_from_auth_key(auth : str) -> str:
    g.DATABASE_CURSOR.execute("SELECT * FROM users WHERE auth=%s", (auth,))

    user = g.DATABASE_CURSOR.fetchone()

    username = user[0]
    
    return username

def is_auth_key_valid(auth : str) -> bool:
    g.DATABASE_CURSOR.execute("SELECT * FROM users WHERE auth=%s", (auth,))
    
    user = g.DATABASE_CURSOR.fetchone()

    if user != None:
        return True
    else:
        return False

##### Lessons #####

def insert_lesson(username : str, course : str, topic : str) -> None:
    today = datetime.date.today()
    days = 0

    g.DATABASE_CURSOR.execute("INSERT INTO lessons (username, course, topic, next_recap_date_year, \
    next_recap_date_month, next_recap_date_day, days) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    (username, course, topic, today.year, today.month, today.day, days))

def update_lesson_finish(username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    g.DATABASE_CURSOR.execute("SELECT * FROM lessons WHERE username=%s AND course=%s AND topic=%s",
    (username, course, topic))
    lesson = g.DATABASE_CURSOR.fetchone()
    updated_lesson_new_days = lesson[6] + 1
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=updated_lesson_new_days)
    g.DATABASE_CURSOR.execute("UPDATE lessons SET next_recap_date_year=%s, \
    next_recap_date_month=%s, \
    next_recap_date_day=%s, \
    days=%s WHERE course=%s AND topic=%s",
                (updated_lesson_new_next_recap_date.year,
                 updated_lesson_new_next_recap_date.month,
                 updated_lesson_new_next_recap_date.day,
                 updated_lesson_new_days,
                 course,
                 topic))

def update_lesson_delay(username : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    g.DATABASE_CURSOR.execute("SELECT * FROM lessons WHERE username=%s AND course=%s AND topic=%s",
    (username, course, topic))
    lesson = g.DATABASE_CURSOR.fetchone()
    updated_lesson_new_next_recap_date = today + datetime.timedelta(days=1)
    g.DATABASE_CURSOR.execute("UPDATE lessons SET next_recap_date_year=%s, \
    next_recap_date_month=%s, \
    next_recap_date_day=%s WHERE course=%s AND topic=%s",
                (updated_lesson_new_next_recap_date.year,
                 updated_lesson_new_next_recap_date.month,
                 updated_lesson_new_next_recap_date.day,
                 course,
                 topic))

def get_lesson_list_of_todays_schedule(username : str) -> list:
    today = datetime.date.today()
  
    g.DATABASE_CURSOR.execute("SELECT * FROM lessons WHERE username=%s", (username,)) 

    lesson_list = [] 

    for lesson in g.DATABASE_CURSOR.fetchall():
        next_recap_date = datetime.date(lesson[3], lesson[4], lesson[5])
        if next_recap_date <= today:
            lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    return lesson_list

def get_all_lessons(username : str) -> list:
    today = datetime.date.today()

    g.DATABASE_CURSOR.execute("SELECT * FROM lessons WHERE username=%s", (username,)) 

    lesson_list = [] 

    for lesson in g.DATABASE_CURSOR.fetchall():
        lesson_list.append({"course": lesson[1], "topic": lesson[2]})

    return lesson_list

def remove_lesson(username : str, course : str, topic : str) -> None:
    g.DATABASE_CURSOR.execute("DELETE FROM lessons WHERE username=%s AND course=%s AND topic=%s", 
    (username, course, topic))

def remove_lessons(username : str, lesson_list_json) -> None:
    for lesson in lesson_list_json:
        remove_lesson(username, lesson["course"], lesson["topic"])

##### Users #####

def insert_user(username : str, email : str, password : str) -> None:
    g.DATABASE_CURSOR.execute("INSERT INTO users (username, email, password, auth) VALUES (%s, %s, %s, %s)",
    (username, email, password, "LOGGED OUT" ))

def set_users_new_auth_key(username : str, new_auth_key : str) -> None:
    g.DATABASE_CURSOR.execute("UPDATE users SET auth=%s WHERE username=%s", 
    (new_auth_key, username))

def log_out_user(username : str) -> None:
    g.DATABASE_CURSOR.execute("UPDATE users SET auth=%s WHERE username=%s", 
    ("LOGGED OUT", username))

def does_username_exist(username : str) -> bool:
    g.DATABASE_CURSOR.execute("SELECT * FROM users WHERE username=%s", (username,))
    
    user = g.DATABASE_CURSOR.fetchone()

    if user != None:
        return True
    else:
        return False  

def are_credentials_valid(username : str, password : str) -> bool:
    g.DATABASE_CURSOR.execute("SELECT * FROM users WHERE username=%s AND password=%s", 
    (username, password))
    
    user = g.DATABASE_CURSOR.fetchone()

    if user != None:
        return True
    else:
        return False  

def get_user_info_from_username(username : str) -> str:
    g.DATABASE_CURSOR.execute("SELECT * FROM users WHERE username=%s", (username,))
    
    user = g.DATABASE_CURSOR.fetchone()

    return user[0] + " " + user[1] + " " + user[2]

def update_user_info(old_username : str, new_username : str, new_email : str, new_password : str) -> None:
    g.DATABASE_CURSOR.execute("UPDATE users SET username=%s, email=%s, password=%s WHERE username=%s", 
                (new_username, new_email, new_password, old_username))

    if(old_username != new_username): 
        g.DATABASE_CURSOR.execute("UPDATE lessons SET username=%s WHERE username=%s", (new_username, old_username))

def delete_account_with_username(username : str) -> None:
    g.DATABASE_CURSOR.execute("DELETE FROM lessons WHERE username=%s", (username,))

    g.DATABASE_CURSOR.execute("DELETE FROM users WHERE username=%s", (username,))

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

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/register/new-user", methods = ["POST"])
def register_new_user():
    new_username = request.form.get("username")

    if not(does_username_exist(new_username)):
        insert_user(new_username, request.form.get("email"), 
        request.form.get("password"))

        new_auth_key = create_new_auth_key()
        set_users_new_auth_key(new_username, new_auth_key)

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

    if does_username_exist(username):
        if are_credentials_valid(username, password):
            new_auth_key = create_new_auth_key()
            set_users_new_auth_key(username, new_auth_key)
            return new_auth_key  
        else:
            return "INCORRECT PASSWORD"
    else:
        return "NO SUCH ACCOUNT"

@app.route("/logout")
def logout():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)
    
        log_out_user(username)

    return "Logged out" 

@app.route("/api/lessons/modify", methods = ["POST", "DELETE", "PUT"])
def interact_with_db():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)

        if request.method == "POST":
            insert_lesson(username, request.form.get("course"), request.form.get("topic"))
            return "New Lesson Received"
        elif request.method == "DELETE":
            if(request.content_type.startswith('application/json')):
                remove_lessons(username, request.get_json())
                return "Lesson(s) Deleted"
            else:
                remove_lesson(username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Deleted"
        elif request.method == "PUT":
            if request.form.get("option") == "finish":
                update_lesson_finish(username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Studied Today"
            elif request.form.get("option") == "delay":
                update_lesson_delay(username, request.form.get("course"), request.form.get("topic"))
                return "Lesson Delayed to Tomorrow"
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/today", methods = ["GET"])
def send_todays_schedule():
    auth_key = request.headers.get("Authorization")
    
    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)

        if request.method == "GET":
            lessons_list = get_lesson_list_of_todays_schedule(username) 
            return jsonify(lessons_list)
    else:
        return "INVALID AUTH KEY"

@app.route("/api/lessons/all", methods = ["GET"])
def send_all_lessons():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)

        if request.method == "GET":
            lesson_list = get_all_lessons(username) 
            return jsonify(lesson_list)
    else:
        return "INVALID AUTH KEY"

@app.route("/settings")
def view_user_settings():
    return render_template("settings.html")

@app.route("/settings/update", methods = ["PUT"])
def update_user_settings():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        old_username = get_username_from_auth_key(auth_key)
        new_username = request.form.get("username")
        if old_username == new_username or not(does_username_exist(new_username)):
            update_user_info(old_username, new_username, request.form.get("email"), request.form.get("password"))
            return "USER INFO SUCCESSFULLY UPDATED"
        else:
            return "USERNAME NOT UNIQUE"
    else:
        return "INVALID AUTH KEY"

@app.route("/settings/get-user-info")
def get_user_info():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)

        if request.method == "GET":
            userinfo = get_user_info_from_username(username) 
            return userinfo 
    else:
        return "INVALID AUTH KEY" 

@app.route("/settings/delete-account", methods = ["DELETE"])
def delete_account():
    auth_key = request.headers.get("Authorization")

    if is_auth_key_valid(auth_key):
        username = get_username_from_auth_key(auth_key)
        delete_account_with_username(username)
        return "RIP"
    else:
        return "INVALID AUTH KEY"

@app.before_request
def setup_database_connection_and_cursor():
    up.uses_netloc.append("postgres")
    url = up.urlparse(os.environ["DATABASE_URL"])

    g.DATABASE_CONNECTION = psycopg2.connect(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)
    
    g.DATABASE_CURSOR = g.DATABASE_CONNECTION.cursor()

@app.after_request
def close_database_connection(response):
    g.DATABASE_CONNECTION.commit()
    g.DATABASE_CONNECTION.close()    

    return response

if __name__ == '__main__':
    app.run()
