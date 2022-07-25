from flask import Flask, request, render_template, jsonify
import sqlite3
import datetime

DATABASE = "lessons.db"

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

def insert_lesson(db : str, course : str, topic : str) -> None:
    today = datetime.date.today()
    days = 0

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("INSERT INTO lessons VALUES (:course, :topic, :next_recap_date_year, \
    :next_recap_date_month, :next_recap_date_day, :days)",
    {"course" : course, 
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

def update_lesson_finish(db : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE course=:course AND topic=:topic",
    {"course": course, 
    "topic": topic})
    lesson = c.fetchone()
    updated_lesson_new_days = lesson[5] + 1
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

def update_lesson_delay(db : str, course : str, topic : str) -> None:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 

    c.execute("SELECT * FROM lessons WHERE course=:course AND topic=:topic",
    {"course": course, 
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

def get_lesson_list_of_todays_schedule(db : str) -> list:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 
  
    c.execute("SELECT * FROM lessons") 

    lesson_list = [] 

    for lesson in c.fetchall():
        next_recap_date = datetime.date(lesson[2], lesson[3], lesson[4])
        if next_recap_date <= today:
            lesson_list.append({"course": lesson[0], "topic": lesson[1]})

    conn.commit()
    conn.close()

    return lesson_list

def get_all_lessons(db : str) -> list:
    today = datetime.date.today()

    conn = sqlite3.connect(db)
    c = conn.cursor() 
    
    c.execute("SELECT * FROM lessons") 

    lesson_list = [] 

    for lesson in c.fetchall():
        lesson_list.append({"course": lesson[0], "topic": lesson[1]})

    conn.commit()
    conn.close()

    return lesson_list

def remove_lesson(db : str, course : str, topic : str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()     

    c.execute("DELETE FROM lessons WHERE course=:course AND topic=:topic", 
    {"course": course, "topic": topic})

    conn.commit()
    conn.close()

def remove_lessons(db : str, lesson_list_json) -> None:
    for lesson in lesson_list_json:
        remove_lesson(db, lesson["course"], lesson["topic"])

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/lessons/modify", methods = ["POST", "DELETE", "PUT"])
def interact_with_db():
    if request.method == "POST":
        insert_lesson(DATABASE, request.form.get("course"), request.form.get("topic"))
        return "New Lesson Received"
    elif request.method == "DELETE":
        if(request.content_type.startswith('application/json')):
            remove_lessons(DATABASE, request.get_json())
            return "Lesson(s) Deleted"
        else:
            remove_lesson(DATABASE, request.form.get("course"), request.form.get("topic"))
            return "Lesson Deleted"
    elif request.method == "PUT":
        if request.form.get("option") == "finish":
            update_lesson_finish(DATABASE, request.form.get("course"), request.form.get("topic"))
            return "Lesson Studied Today"
        elif request.form.get("option") == "delay":
            update_lesson_delay(DATABASE, request.form.get("course"), request.form.get("topic"))
            return "Lesson Delayed to Tomorrow"

@app.route("/api/lessons/today", methods = ["GET"])
def send_todays_schedule():
    if request.method == "GET":
        lessons_list = get_lesson_list_of_todays_schedule(DATABASE) 
        return jsonify(lessons_list)

@app.route("/api/lessons/all", methods = ["GET"])
def send_all_lessons():
    if request.method == "GET":
        lesson_list = get_all_lessons(DATABASE) 
        return jsonify(lesson_list)

if __name__ == '__main__':
    app.run()
