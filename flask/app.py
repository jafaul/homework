import random
import string
from datetime import datetime, timedelta

from flask import Flask, request, Response, jsonify, redirect
from sqlalchemy.orm import Session, joinedload

from database import engine
from tools import serialize_list
from models import *
from config import config

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

        user = User(email=body["email"], password=body["password"], name=body["name"], surname=body["surname"])
        with Session(engine) as session:
            session.add(user)
            session.commit()

        return redirect("/users/", code=302)

    return """
        <form method="POST">
            Email:    <input type="email" name="email" /> <br>
            Password: <input type="password" name="password" /> <br>
            Name:     <input type="text" name="name" /> <br>
            Surname:  <input type="text" name="surname" /> <br>

            <input type="submit" value="REGISTER" /> <br>
        </form>
        """


@app.route("/users/", methods=["GET"])
def get_users():
   # https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html
    with Session(engine) as session:
        users = session.query(User).options(
            joinedload(User.courses_as_student),
            joinedload(User.courses_as_teacher)
        ).all()

    return jsonify(serialize_list(users, include_relationships=True)), 200


@app.route("/courses/", methods=["GET"])
def get_courses():
    with Session(engine) as session:
        courses = session.query(Course).options(
            joinedload(Course.teacher),
            joinedload(Course.students)
        ).all()

    return jsonify(serialize_list(courses, include_relationships=True)), 200


@app.route("/courses/create/", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            course = Course(
                teacher_id=int(body["teacher_id"]),
                title=body["title"],
                description=body["description"]
            )
            students_ids = [int(student_id.strip()) for student_id in body.get("students_ids", [])]
            if students_ids:
                students = session.query(User).filter(User.id.in_(students_ids)).all()
                course.students = students
            session.add(course)
            session.flush()
            course_id = course.id
            session.commit()

        return redirect(f"/courses/{course_id}", 302)

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
    with Session(engine) as session:
        course = session.query(Course).filter(Course.id == course_id).one().as_dict(include_relationships=True)
        lectures = session.query(Lecture).filter(Lecture.course_id == course["id"]).all()
        course["lectures"] = serialize_list(lectures)
        tasks = session.query(Task).filter(Task.course_id == course["id"]).all()
        course["tasks"] = serialize_list(tasks)

    return jsonify(course), 200


@app.route("/courses/<course_id>/lectures/", methods=["GET", "POST"])
def add_lectures_to_course(course_id):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            lecture = Lecture(
                course_id=course_id,
                title=body["title"],
                description=body["description"]
            )
            session.add(lecture)
            session.commit()

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
        with Session(engine) as session:
            pass
        # try:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             'INSERT INTO "task" (course_id, description, max_mark, deadline) VALUES (%s, %s, %s, %s)',
        #             (course_id, body["description"], body["max_mark"], body["deadline"])
        #         )
        #         conn.commit()
        # except psycopg2.Error as e:
        #     print(e)
        #     conn.rollback()

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

# @app.route("/courses/<course_id>/tasks/<task_id>/answers", methods=["GET", "POST"])
# def task_answer(course_id, task_id):
#     if request.method == "POST":
#         body = request.form
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute(
#                     'INSERT INTO "answer" (task_id, description, student_id) VALUES (%s, %s, %s)',
#                     (task_id, body["description"], body["student_id"])
#                 )
#                 conn.commit()
#         except psycopg2.Error as e:
#             print(e)
#             conn.rollback()
#
#         return redirect(f"/courses/{course_id}/", code=302)
#
#     return """
#         <form method="POST">
#             Description:  <input type="text" name="description" /> <br>
#             Student ID:   <input type="number" name="student_id" /> <br>
#
#             <input type="submit" value="ANSWER" /> <br>
#         </form>
#      """
#
#
# @app.route("/courses/<course_id>/tasks/<task_id>/answers/<answer_id>/mark", methods=["GET", "POST"])
# def get_mark(course_id, task_id, answer_id):
#     if request.method == "POST":
#         body = request.form
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute(
#                     'INSERT INTO "mark" (answer_id, date, mark, teacher_id) VALUES (%s, %s, %s, %s)',
#                     (answer_id, body["date"], body["mark"], body["teacher_id"])
#                 )
#
#                 cursor.execute(
#                     'UPDATE "answer" SET mark = %s WHERE answer.id = %s',
#                     (body["mark"], answer_id)
#                 )
#                 conn.commit()
#         except psycopg2.Error as e:
#             print(e)
#             conn.rollback()
#
#         return redirect(f"/courses/{course_id}", code=302)
#
#     else:
#         with conn.cursor() as cursor:
#             cursor.execute('SELECT "max_mark" from "task" WHERE id = %s', (task_id,))
#             max_mark = cursor.fetchone()[0]
#
#         default_date = datetime.now().today().strftime("%Y-%m-%d")
#
#         return f"""
#             <form method="POST">
#                 Datetime:    <input type="date" name="date" value="{default_date}" readonly /> <br>
#                 Mark:        <input type="number" name="mark" min="0" max="{max_mark}"/> <br>
#                 Teacher ID:  <input type="number" name="teacher_id" /> <br>
#
#                 <input type="submit" value="SEND" /> <br>
#             </form>
#          """
#
#
# @app.route("/courses/<course_id>/rating", methods=["GET", "POST"])
# def get_rating(course_id):
#     if request.method == "POST":
#         return abort(404, description="Not Implemented")
#
#     with conn.cursor() as cursor:
#         cursor.execute('''
#              SELECT "user".*, round(AVG("answer".mark),2) AS avg_mark
#              FROM "user"
#                  JOIN "course_student" ON "user".id = "course_student".student_id
#                  JOIN "answer" ON "user".id = answer.student_id
#              WHERE "course_student".course_id = %s
#              GROUP BY "user".id
#              ORDER BY avg_mark DESC
#              ''', (course_id,)
#         )
#         rating = selector(cursor)
#         return jsonify(rating), 200


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
    app.run(debug=config.DEBUG, host=config.APP_HOST, port=config.APP_PORT)
