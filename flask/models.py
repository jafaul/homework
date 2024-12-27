import datetime as dt

from sqlalchemy import ForeignKey, String, SmallInteger, Date, Text, VARCHAR, Column, Table, Integer, BigInteger
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

course_student = Table(
    'course_student',
    Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column("course_id", BigInteger, ForeignKey("course.id")),
    Column("student_id", BigInteger, ForeignKey("user.id")),
)


class Answer(Base):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    mark: Mapped[int] = mapped_column(SmallInteger)
    submission_date: Mapped[dt.date] = mapped_column(Date, default=dt.date.today())


class Lecture(Base):
    __tablename__ = "lecture"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)


class Mark(Base):
    __tablename__ = "mark"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answer.id"))
    date: Mapped[dt.date] = mapped_column(Date)
    mark: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    description: Mapped[str] = mapped_column(Text)
    max_mark: Mapped[int] = mapped_column(SmallInteger, default=5, nullable=False)
    deadline: Mapped[dt.date] = mapped_column(Date, default=dt.date.today() + dt.timedelta(days=7))


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    teacher: Mapped["User"] = relationship(back_populates="courses_as_teacher")
    students: Mapped[list["User"]] = relationship(secondary=course_student, back_populates="courses_as_student")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(36), nullable=False)
    password: Mapped[str] = mapped_column(VARCHAR(36), nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(36), nullable=False)
    surname: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    photo: Mapped[bytes] = mapped_column(OID)
    phone_number: Mapped[str] = mapped_column(VARCHAR(17))

    courses_as_student: Mapped[list[Course]] = relationship(
        secondary=course_student,
        primaryjoin=id == course_student.c.student_id,
        back_populates="students",
    )

    courses_as_teacher: Mapped[list[Course]] = relationship(back_populates="teacher")

