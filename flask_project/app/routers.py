import random
import string
from datetime import datetime, timedelta
from time import perf_counter

from flask import Flask, request, Response, jsonify, redirect, abort
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload, noload

from .database import engine
from .models import *
from .tools import serialize_list

app = Flask(__name__)


@app.route("/whoami/", methods=["GET"])
def whoami():
    return {
        "user_agent": request.headers.get("User-Agent"),
        "IP": request.remote_addr,
        "timestamp": datetime.now().isoformat(),
    }


@app.route("/register/", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        body = request.form
        user = User(
            email=body["email"],
            password=body["password"],
            name=body["name"],
            surname=body["surname"],
        )
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
        start = perf_counter()
        users = (
            session.query(User)
            .options(
                joinedload(
                    User.courses_as_student
                ),  # joined load for many to many, one to one, many to one
                selectinload(User.courses_as_teacher),  # select in load for one to many
                noload(User.answers),  # return answers: []
            )
            .all()
        )

        print(str(perf_counter() - start))

    return (
        jsonify(
            serialize_list(users, include_relationships=True, exclude=("answers",))
        ),
        200,
    )


@app.route("/courses/", methods=["GET"])
def get_courses():
    with Session(engine) as session:
        courses = (
            session.query(Course)
            .options(joinedload(Course.teacher), joinedload(Course.students))
            .all()
        )

    return jsonify(serialize_list(courses, include_relationships=True)), 200


@app.route("/courses/create/", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            course = Course(
                teacher_id=int(body["teacher_id"]),
                title=body["title"],
                description=body["description"],
            )
            students_ids = [
                int(student_id.strip()) for student_id in body.get("students_ids", [])
            ]
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
            Description:   <input type="text" name="description" value="" /> <br>

            <input type="submit" value="CREATE" /> <br>
        </form>
     """


@app.route("/courses/<int:course_id>/", methods=["GET"])
def get_course_info(course_id):
    with Session(engine) as session:
        course = (
            session.query(Course)
            .filter(Course.id == course_id)
            .one()
            .as_dict(include_relationships=True)
        )
        lectures = (
            session.query(Lecture).filter(Lecture.course_id == course["id"]).all()
        )
        course["lectures"] = serialize_list(lectures)
        raw_tasks = session.query(Task).filter(Task.course_id == course["id"]).all()
        tasks = serialize_list(raw_tasks, include_relationships=True)
        for task in tasks:
            for answer in task["answers"]:
                mark = (
                    session.query(Mark).filter(Mark.answer_id == answer["id"]).first()
                )
                if mark:
                    answer["mark"] = mark.as_dict()
        course["tasks"] = tasks

    return jsonify(course), 200


@app.route("/courses/<int:course_id>/lectures/", methods=["GET", "POST"])
def add_lectures_to_course(course_id):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            lecture = Lecture(
                course_id=course_id,
                title=body["title"],
                description=body["description"],
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


@app.route("/courses/<int:course_id>/tasks/", methods=["GET", "POST"])
def task_page(course_id):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            task = Task(
                course_id=course_id,
                description=body["description"],
                max_mark=int(body["max_mark"]),
                deadline=datetime.strptime(body["deadline"], "%Y-%m-%d").date(),
            )
            session.add(task)
            session.commit()

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


@app.route(
    "/courses/<int:course_id>/tasks/<int:task_id>/answers/", methods=["GET", "POST"]
)
def task_answer(course_id: int, task_id: int):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            answer = Answer(
                task_id=task_id,
                description=body["description"],
                student_id=int(body["student_id"]),
            )
            session.add(answer)
            session.commit()

        return redirect(f"/courses/{course_id}/", code=302)

    return """
        <form method="POST">
            Description:  <input type="text" name="description" /> <br>
            Student ID:   <input type="number" name="student_id" /> <br>

            <input type="submit" value="ANSWER" /> <br>
        </form>
     """


@app.route(
    "/courses/<int:course_id>/tasks/<int:task_id>/answers/<int:answer_id>/mark/",
    methods=["GET", "POST"],
)
def get_mark(course_id: int, task_id: int, answer_id: int):
    if request.method == "POST":
        body = request.form

        with Session(engine) as session:
            start = perf_counter()
            mark = session.query(Mark).filter(Mark.answer_id == answer_id).first()
            if mark:
                mark.teacher_id = int(body["teacher_id"])
                mark.mark_value = int(body["mark"])
            else:
                mark = Mark(
                    answer_id=answer_id,
                    mark_value=int(body["mark"]),
                    date=datetime.strptime(body["date"], "%Y-%m-%d").date(),
                    teacher_id=int(body["teacher_id"]),
                )

            session.add(mark)
            session.commit()
        print(str(perf_counter() - start))
        return redirect(f"/courses/{course_id}", code=302)

    else:
        default_date = datetime.now().today().strftime("%Y-%m-%d")
        with Session(engine) as session:
            max_mark = session.query(Task).filter(Task.id == task_id).all()

        return f"""
            <form method="POST">
                Datetime:    <input type="date" name="date" value="{default_date}" readonly /> <br>
                Mark:        <input type="number" name="mark" min="0" max="{max_mark}"/> <br>
                Teacher ID:  <input type="number" name="teacher_id" /> <br>

                <input type="submit" value="SEND" /> <br>
            </form>
         """


@app.route("/courses/<int:course_id>/rating/", methods=["GET", "POST"])
def get_rating(course_id):
    if request.method == "POST":
        return abort(404, description="Not Implemented")

    with Session(engine) as session:
        avg_mark = func.round(func.avg(Mark.mark_value).label("avg_mark"), 2)

        raw_results = (
            session.query(User.id, User.name, User.surname, avg_mark)
            .join(User.courses_as_student)
            .join(Answer)
            .join(Mark)
            .filter(Course.id == course_id)
            .group_by(User.id)
            .order_by(avg_mark)
            .all()
        )

        results = [
            {
                "id": raw_result[0],
                "name": raw_result[1],
                "surname": raw_result[2],
                "avg_mark": raw_result[3],
            }
            for raw_result in raw_results
        ]

        return jsonify(results), 200


@app.route("/source_code/")
def source_code():
    with open("routers.py", "r") as file:
        content = file.read()
        return Response(content, mimetype="text/python")


# /random?length=42&specials=1&digits=0
@app.route("/random/")
def get_random_string():
    length = request.args.get("length", default=8, type=int)
    specials = request.args.get("specials", default=0, type=int)
    digits = request.args.get("digits", default=0, type=int)

    if length > 100 or length < 1:
        return jsonify("Length must be between 1 and 100"), 400
    if specials not in {0, 1}:
        return jsonify("Specials must be 0 or 1"), 400
    if digits not in {0, 1}:
        return jsonify("Digits must be 0 or 1"), 400

    all_characters = string.ascii_letters
    if specials:
        all_characters += string.punctuation
    if digits:
        all_characters += string.digits

    return "".join(random.choices(all_characters, k=length))
