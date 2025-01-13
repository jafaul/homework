import random
import string
from datetime import datetime, timedelta
from functools import lru_cache
from time import perf_counter

from flask import Flask, request, Response, jsonify, redirect, abort, render_template, url_for
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload, selectinload, noload

from .database import engine
from .models import *
from .tools import serialize_list

app = Flask(__name__)

@lru_cache
def get_menu():
    menu = [
        {"url": url_for("index", _external=True), "name": "Home"},
        {"url": url_for("get_courses", _external=True), "name": "Courses"},
        {"url": url_for("create_course", _external=True), "name": "Create Course"},
        {"url": url_for("get_users", _external=True), "name": "Users"},
        {"url": url_for("user_create", _external=True), "name": "Sign up"},
    ]
    return menu

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", menu=get_menu(), title="Welcome to our school!")


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

    fields = [
        {"title": "Email", "type": "email", "name": "email", "is_required": True},
        {"title": "Password", "type": "password", "name": "password", "is_required": True},
        {"title": "Name", "type": "name", "name": "name", "is_required": True},
        {"title": "Surname", "type": "surname", "name": "surname", "is_required": True},
        {"title": "Phone number", "type": "phone_number", "name": "phone_number", "is_required": False},
    ]

    return render_template(
        "input_form.html", title="Sign Up", fields=fields, submit_name="Sign Up", menu=get_menu())


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
            .order_by(desc(User.id)).all()
        )

        print(str(perf_counter() - start))
    return render_template("users.html", users=users, menu=get_menu(), title="Users")


@app.route("/courses/", methods=["GET"])
def get_courses():
    with Session(engine) as session:
        courses = (
            session.query(Course)
            .options(joinedload(Course.teacher), joinedload(Course.students))
            .order_by(desc(Course.id)).all()
        )
    return render_template("courses.html", courses=courses, menu=get_menu(), title="Courses")


@app.route("/courses/create/", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        body = request.form
        print(body)
        with Session(engine) as session:
            students = body.get("students", [])
            students_ids = [int(student.split('.', maxsplit=1)[0]) for student in students]

            teacher_id = int(body["teacher"].split(".", maxsplit=1)[0])

            course = Course(
                teacher_id=int(teacher_id),
                title=body["title"],
                description=body["description"],
            )

            if students_ids:
                students = session.query(User).filter(User.id.in_(students_ids)).all()
                course.students = students
            session.add(course)
            session.flush()
            course_id = course.id
            session.commit()

        return redirect(f"/courses/{course_id}", 302)

    with Session(engine) as session:
        users = session.query(User).all()
        users_for_web = [
            str(user.id) + "." + str(user.name) + " " + str(user.surname) for user in users
        ]

    fields = [
        {"title": "Title of course", "type": "text", "name": "title", "is_required": True},
        {
            "title": "Teacher", "type": "list", "name": "teacher", "is_required": True,
            "options": users_for_web, "multiple": False
        },
        {
            "title": "Students", "type": "list", "name": "students", "is_required": True,
            "placeholder": "Select students", "options": users_for_web, "multiple": True
        },
        {"title": "Description", "type": "text", "name": "description", "is_required": False},
    ]
    return render_template(
        "create_course.html",
        title="Create Course",
        fields=fields,
        submit_name="Create",
        menu=get_menu()
    )


@app.route("/courses/<int:course_id>/", methods=["GET"])
def get_course_info(course_id):
    with Session(engine) as session:
        course = (
            session.query(Course)
            .options(
                joinedload(Course.lectures),
                joinedload(Course.tasks)
                .joinedload(Task.answers)
                .joinedload(Answer.mark)
                .noload(Mark.teacher),
                joinedload(Course.teacher)
        )
            .filter(Course.id == course_id)
            .one()
        )

        serialized_lectures = [
            {
                "title": lecture.title,
                "description": lecture.description,
            }
            for lecture in course.lectures
        ]

        serialized_tasks = []
        for task in course.tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "max_mark": task.max_mark,
                "deadline": task.deadline,
                "description": task.description,
                "answers": [
                    {
                        "id": answer.id,
                        "student_name": f"{answer.student.name} {answer.student.surname}",
                        "description": answer.description,
                        "submission_date": answer.submission_date,
                        "mark": answer.mark.mark_value if answer.mark else "Pending to review",
                        "teacher_name": f"{answer.mark.teacher.name} {answer.mark.teacher.surname}"
                                        if answer.mark else "Pending to review",
                    }
                    for answer in task.answers
                ],
            }
            serialized_tasks.append(task_dict)
        print(serialized_tasks)
    return render_template(
        "course.html", menu=get_menu(), course=course,
        title=course.title, tasks=serialized_tasks, lectures=serialized_lectures)


@app.route("/courses/<int:course_id>/lectures/", methods=["GET", "POST"])
def add_lectures_to_course(course_id):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            lecture = Lecture(
                course_id=course_id,
                title=body["title"],
                description=body.get("description", ""),
            )
            session.add(lecture)
            session.commit()

        return redirect(f"/courses/{course_id}/", code=302)


    fields = [
        {"title": "Lecture Title", "type": "text", "name": "title", "is_required": True},
        {"title": "Description", "type": "text", "name": "description", "is_required": False}
    ]
    return render_template(
        "input_form.html",
        title="Add Lecture",
        fields=fields,
        submit_name="Add",
        menu=get_menu()
    )


@app.route("/courses/<int:course_id>/tasks/", methods=["GET", "POST"])
def task_page(course_id):
    if request.method == "POST":
        body = request.form
        with Session(engine) as session:
            task = Task(
                title=body["title"],
                course_id=course_id,
                description=body["description"],
                max_mark=int(body["max_mark"]),
                deadline=datetime.strptime(body["deadline"], "%Y-%m-%d").date(),
            )
            session.add(task)
            session.commit()

        return redirect(f"/courses/{course_id}", code=302)
    default_date = (datetime.now().today() + timedelta(days=7)).strftime("%Y-%m-%d")

    fields = [
        {"title": "Title", "type": "text", "name": "title", "is_required": True},
        {"title": "Description", "type": "text", "name": "description", "is_required": False},
        {
            "title": "Max mark", "type": "number", "name": "max_mark", "is_required": True,
            "max": 200, "min": 5, "default_value": 5
        },
        {"title": "Deadline", "type": "date", "name": "deadline", "is_required": True, "default_value": default_date},

    ]
    return render_template(
        "input_form.html",
        title="Add Task",
        fields=fields,
        submit_name="Add",
        menu=get_menu()
    )


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

    with Session(engine) as session:
        users = session.query(User).options(joinedload(User.courses_as_student)).filter(Course.id == course_id).all()
        users_for_web = [
            str(user.id) + "." + str(user.name) + " " + str(user.surname) for user in users
        ]
        print(users_for_web)

    fields = [
        {"title": "Student's answer", "type": "text", "name": "description", "is_required": True},
        {
            "title": "Student name", "type": "list", "name": "student", "is_required": True,
            "options": users_for_web, "multiple": False
        },
    ]
    return render_template(
        "input_form.html",
        title="Send a homework",
        fields=fields,
        submit_name="Send",
        menu=get_menu()
    )

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
def set_mark(course_id: int, task_id: int, answer_id: int):
    if request.method == "POST":
        body = request.form

        with Session(engine) as session:
            start = perf_counter()
            mark = session.query(Mark).filter(Mark.answer_id == answer_id).first()
            if mark:
                mark.teacher_id = int(body["teacher_id"])
                mark.mark_value = int(body["mark_value"])
            else:
                mark = Mark(
                    answer_id=answer_id,
                    mark_value=int(body["mark_value"]),
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
            max_mark = session.query(Task).filter(Task.id == task_id).first().max_mark

        return f"""
            <form method="POST">
                Datetime:    <input type="date" name="date" value="{default_date}" readonly /> <br>
                Mark:        <input type="number" name="mark_value" min="0" max="{max_mark}"/> <br>
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
            .order_by(avg_mark.desc())
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
