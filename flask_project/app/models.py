import datetime as dt
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    SmallInteger,
    Date,
    Text,
    VARCHAR,
    Column,
    Table,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

CourseStudent = Table(
    "course_student",
    Base.metadata,
    Column("id", BigInteger, primary_key=True),
    Column("course_id", BigInteger, ForeignKey("course.id")),
    Column("student_id", BigInteger, ForeignKey("user.id")),
)


class Lecture(Base):
    __tablename__ = "lecture"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)

    course: Mapped["Course"] = relationship("Course", back_populates="lectures")


class Answer(Base):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    description: Mapped[str] = mapped_column(String(300))
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    submission_date: Mapped[dt.date] = mapped_column(Date, default=dt.date.today(), nullable=True)

    mark: Mapped[Optional["Mark"]] = relationship(
        "Mark", back_populates="answer", uselist=False
    )
    task: Mapped["Task"] = relationship("Task", uselist=False)
    student: Mapped["User"] = relationship(
        "User", back_populates="answers", uselist=False
    )


class Mark(Base):
    __tablename__ = "mark"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answer.id"))
    date: Mapped[dt.date] = mapped_column(Date)
    mark_value: Mapped[int] = mapped_column(SmallInteger)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    answer: Mapped[Answer] = relationship(
        "Answer", back_populates="mark", uselist=False
    )
    teacher: Mapped["User"] = relationship(
        "User", back_populates="marks", uselist=False
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    max_mark: Mapped[int] = mapped_column(SmallInteger, default=5)
    deadline: Mapped[dt.date] = mapped_column(
        Date, default=dt.date.today() + dt.timedelta(days=7)
    )

    answers: Mapped[list["Answer"]] = relationship("Answer", back_populates="task")
    course: Mapped["Course"] = relationship("Course", back_populates="tasks")


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

    teacher: Mapped["User"] = relationship(back_populates="courses_as_teacher")
    students: Mapped[list["User"]] = relationship(
        secondary=CourseStudent, back_populates="courses_as_student"
    )
    lectures: Mapped[list["Lecture"]] = relationship("Lecture", back_populates='course')
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="course")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(36))
    password: Mapped[str] = mapped_column(VARCHAR(36))
    name: Mapped[str] = mapped_column(VARCHAR(36))
    surname: Mapped[str] = mapped_column(VARCHAR(40))
    photo: Mapped[bytes] = mapped_column(OID, nullable=True)
    phone_number: Mapped[str] = mapped_column(VARCHAR(17), nullable=True)

    courses_as_student: Mapped[list[Course]] = relationship(
        secondary=CourseStudent,
        primaryjoin=id == CourseStudent.c.student_id,
        back_populates="students",
    )

    courses_as_teacher: Mapped[list[Course]] = relationship(back_populates="teacher")
    answers: Mapped[list["Answer"]] = relationship(back_populates="student")
    marks: Mapped[list["Mark"]] = relationship("Mark", back_populates="teacher")