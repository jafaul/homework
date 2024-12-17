import random
import string
from datetime import datetime, timedelta
from statistics import mean

import psycopg2
from flask import Flask, request, Response, jsonify, redirect, abort

from database import conn
from tools import selector

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

        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect("/users/", code=302)

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
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM "user"')
        users = selector(cursor)

        for user in users:
            cursor.execute(
                '''
                    SELECT * FROM "course" 
                        JOIN "course_student" ON "course".id = "course_student".course_id 
                    WHERE "course_student".student_id = %s
                ''', (user['id'],)
            )
            user["student_of"] = selector(cursor)

            cursor.execute('SELECT * FROM "course" WHERE teacher_id = %s', (user['id'],))
            user["teacher_of"] = selector(cursor)

    return jsonify(users), 200


@app.route("/courses/", methods=["GET"])
def get_courses():
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM "course"')
        courses = selector(cursor)
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
                for student_id in body["students_ids"].split(","):
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
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM "course" WHERE course.id = %s', (course_id,))
            course = selector(cursor, one=True)

            cursor.execute('SELECT * FROM "lecture" WHERE course_id = %s', (course_id,))
            lectures = selector(cursor)

            cursor.execute('''
                SELECT * FROM "user" 
                    JOIN "course_student" ON "user".id = "course_student".student_id 
                WHERE "course_student".course_id = %s
                ''', (course_id,)
            )
            students = selector(cursor)

            cursor.execute('SELECT * FROM "task" WHERE "task".course_id = %s', (course_id,))
            tasks = selector(cursor)
            for task in tasks:
                cursor.execute('SELECT * FROM "answer" WHERE answer.task_id = %s', (task['id'],))
                task["answers"] = selector(cursor)

            course.update({
                "lectures": lectures,
                "students": students,
                "tasks": tasks,
            })
    except psycopg2.Error as e:
        print(e)
        conn.rollback()

    return jsonify(course), 200


@app.route("/courses/<course_id>/lectures/", methods=["GET", "POST"])
def add_lectures_to_course(course_id):
    if request.method == "POST":
        body = request.form
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "lecture" (course_id, title, description) VALUES (%s, %s, %s)',
                    (course_id, body["title"], body["description"])
                )
                conn.commit()
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect(f"/courses/{course_id}/", code=302)
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
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "task" (course_id, description, max_mark, deadline) VALUES (%s, %s, %s, %s)',
                    (course_id, body["description"], body["max_mark"], body["deadline"])
                )
                conn.commit()
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect(f"/courses/{course_id}", code=302)

    default_date = (datetime.now().today() + timedelta(days=7)).strftime("%Y-%m-%d")
    return f"""
        <form method="POST">
            Description:  <input type="text" name="description" /> <br>
            Max mark:  <input type="number" name="max_mark" max="200" value="5" /> <br>
            Deadline:  <input type="date" name="deadline" value="{default_date}" /> <br>
            <input type="submit" value="UPDATE" /> <br>
        </form>
     """

@app.route("/courses/<course_id>/tasks/<task_id>/answers", methods=["GET", "POST"])
def task_answer(course_id, task_id):
    if request.method == "POST":
        body = request.form
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "answer" (task_id, description, student_id) VALUES (%s, %s, %s)',
                    (task_id, body["description"], body["student_id"])
                )
                conn.commit()
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect(f"/courses/{course_id}/", code=302)

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
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "mark" (answer_id, date, mark, teacher_id) VALUES (%s, %s, %s, %s)',
                    (answer_id, body["date"], body["mark"], body["teacher_id"])
                )

                cursor.execute(
                    'UPDATE "answer" SET mark = %s WHERE answer.id = %s',
                    (body["mark"], answer_id)
                )
                conn.commit()
        except psycopg2.Error as e:
            print(e)
            conn.rollback()

        return redirect(f"/courses/{course_id}", code=302)

    else:
        with conn.cursor() as cursor:
            cursor.execute('SELECT "max_mark" from "task" WHERE id = %s', (task_id,))
            max_mark = cursor.fetchone()[0]

        default_date = datetime.now().today().strftime("%Y-%m-%d")

        return f"""
            <form method="POST">
                Datetime:    <input type="date" name="date" value="{default_date}" readonly /> <br>
                Mark:        <input type="number" name="mark" min="0" max="{max_mark}"/> <br>
                Teacher ID:  <input type="number" name="teacher_id" /> <br>
    
                <input type="submit" value="SEND" /> <br>
            </form>
         """


@app.route("/courses/<course_id>/rating", methods=["GET", "POST"])
def get_rating(course_id):
    if request.method == "POST":
        return abort(404, description="Not Implemented")

    with conn.cursor() as cursor:
        cursor.execute('''
             SELECT "user".*, round(AVG("answer".mark),2) AS avg_mark
             FROM "user" 
                 JOIN "course_student" ON "user".id = "course_student".student_id 
                 JOIN "answer" ON "user".id = answer.student_id 
             WHERE "course_student".course_id = %s 
             GROUP BY "user".id
             ORDER BY avg_mark DESC
             ''', (course_id,)
        )
        rating = selector(cursor)
        return jsonify(rating), 200


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