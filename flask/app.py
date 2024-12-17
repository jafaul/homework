import random
import string
from datetime import datetime, timedelta

import psycopg2
from flask import Flask, request, Response, jsonify, redirect, abort

from database import conn
from tools import query_db

app = Flask(__name__)


@app.route('/whoami/', methods=['GET'])
def whoami():
    return {
        "user_agent": request.headers.get('User-Agent'),
        "IP": request.remote_addr,
        "timestamp": datetime.now().isoformat()
    }


@app.route("/register/", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        body = request.form
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "user" (email, password, name, surname) VALUES (%s, %s, %s, %s)',
                    (body["email"], body["password"], body["name"], body["surname"])
                )
                conn.commit()

            return redirect("/users/", code=302)
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

    return """
        <form method="POST">
            Email:    <input type="email" name="email" /> </br>
            Password: <input type="password" name="password" /> </br>
            Name:     <input type="text" name="name" /> </br>
            Surname:  <input type="text" name="surname" /> </br>
            
            <input type="submit" value="REGISTER" /> </br>
        </form>
        """


@app.route("/users/", methods=["GET"])
def get_users():
    users = query_db(conn, 'SELECT * FROM "user"')
    return jsonify(users), 200


@app.route("/courses/", methods=["GET"])
def get_courses():
    courses = query_db(conn, 'SELECT * FROM "course"')
    return jsonify(courses), 200


@app.route("/courses/create/", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        body = request.form
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "course" (teacher_id, title, description) VALUES (%s, %s, %s) RETURNING id',
                    (int(body["teacher_id"]), body["title"], body["description"])
                )
                course_id = cursor.fetchone()[0]
                for student_id in body["student_ids"]:
                    cursor.execute(
                        'INSERT INTO "course_student" (course_id, student_id) VALUES (%s, %s)',
                        (course_id, student_id)
                    )
                conn.commit()
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect(f"/courses/{course_id}/", 302)
    return """
        <form method="POST">
            Title:        <input type="text" name="title" /> <br>
            Teacher ID:   <input type="number" name="teacher_id" /> <br>
            Students IDs: <input type="text" name="students_ids" placeholder="1, 2, 3" /> <br>
            Description:   <input type="text" name="description" value="''" /> <br>
            
            <input type="submit" value="CREATE" /> <br>
        </form>
     """


@app.route("/courses/<course_id>/", methods=["GET"])
def get_course_info(course_id):
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM "course" WHERE id = %s', (course_id,))
        course = cursor.fetchone()
        return jsonify(course, type="json"), 200


@app.route("/courses/<course_id>/lectures/", methods=["GET", "POST"])
def add_lectures_to_course(course_id):
    if request.method == "POST":
        body = request.form
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "lecture" (course_id, title, description) VALUES (%s, %s, %s)',
                (course_id, body["title"], body["description"])
            )
        return redirect(f"/courses/{course_id}", code=302)
    return """
        <form method="POST">
            Title:        <input type="text" name="title" /> <br>
            Description:  <input type="text" name="description" /> <br>
            
            <input type="submit" value="CREATE" /> <br>
        </form>
     """


@app.route("/courses/<course_id>/tasks/", methods=["GET", "POST"])
def task_page(course_id):
    if request.method == "POST":
        body = request.form
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "task" (course_id, description, max_mark, deadline) VALUES (%s, %s, %s, %s)',
                (course_id, body["description"], body["max_mark"], body["deadline"])
            )
        return redirect(f"/courses/{course_id}", code=302)

    return f"""
        <form method="POST">
            Description:  <input type="text" name="description" /> <br>
            Max mark:  <input type="number" name="max_mark" max="200" value="5" /> <br>
            Deadline:  <input type="date" name="deadline" value="{datetime.now().today() + timedelta(days=7)}" /> <br>
            <input type="submit" value="UPDATE" /> <br>
        </form>
     """

@app.route("/courses/<course_id>/tasks/<task_id>/answers", methods=["GET", "POST"])
def task_answer(course_id, task_id):
    if request.method == "POST":
        body = request.form
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "answer" (task_id, description, student_id) VALUES (%s, %s, %s)',
                (course_id, body["description"], body["student_id"])
            )
        return redirect(f"/courses/{course_id}", code=302)

    return """
        <form method="POST">
            Description:  <input type="text" name="description" /> <br>
            Student ID:   <input type="number" name="student_id" /> <br>

            <input type="submit" value="ANSWER" /> <br>
        </form>
     """


@app.route("/courses/<course_id>/tasks/<task_id>/answers/<answer_id>/mark", methods=["GET", "POST"])
def get_mark(course_id, task_id, answer_id):
    if request.method == "POST":
        body = request.form
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "mark" (answer_id, date, mark, teacher_id) VALUES (%s, %s, %s, %s)',
                (answer_id, body["date"], body["mark"], body["teacher_id"])
            )

        return redirect(f"/courses/{course_id}", code=302)

    else:
        with conn.cursor() as cursor:
            cursor.execute('SELECT "max_mark" from "task" WHERE id = %s', (task_id,))
            max_mark = cursor.fetchone()[0]

        return f"""
            <form method="POST">
                Datetime:    <input type="datetime-local" name="date" /> <br>
                Mark:        <input type="number" name="mark" min="0" max="{max_mark}"/> <br>
                Teacher ID:  <input type="number" name="teacher_id" /> <br>
    
                <input type="submit" value="SEND" /> <br>
            </form>
         """


@app.route("/courses/<course_id>/rating", methods=["GET", "POST"])
def get_rating(course_id, task_id, answer_id):
    if request.method == "POST":
        return abort(404, description="Not Implemented")


@app.route('/source_code/')
def source_code():
    with open("app.py", "r") as file:
        content = file.read()
        return Response(content, mimetype='text/python')


# /random?length=42&specials=1&digits=0
@app.route('/random')
def get_random_string():
    length = request.args.get('length', default=8, type=int)
    specials = request.args.get('specials', default=0, type=int)
    digits = request.args.get('digits', default=0, type=int)

    if length > 100 or length < 1:
        return jsonify("Length must be between 1 and 100"), 400
    if specials not in {0, 1}:
        return jsonify("Specials must be 0 or 1"), 400
    if digits not in {0, 1}:
        return jsonify("Digits must be 0 or 1"), 400

    all_characters = string.ascii_letters
    if specials: all_characters += string.punctuation
    if digits: all_characters += string.digits

    return ''.join(random.choices(all_characters, k=length))



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")