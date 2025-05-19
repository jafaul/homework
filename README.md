# 🧠 Python Web Development Homework

This repository contains homework assignments completed as part of the **Python Web Development** course by [robotdreams.cc](https://robotdreams.cc). The assignments are focused on building core backend development skills using Python and cover topics ranging from system-level scripting to fully functional web applications using Flask and PostgreSQL.

---

## 📁 Repository Structure & Module Descriptions

### `linux_base/` — **Linux Command Line & Shell Scripting**

- Working with files and directories (listing, permissions, archiving)
- Managing user and group permissions (`chmod`, `chown`)
- Monitoring system resources and processes (`ps`, `top`, `htop`)
- Writing Bash scripts for automation
- Scheduling jobs with `cron`
- Text parsing using `grep`, `awk`, `sed`, `find`

📌 **Goal:** Learn to navigate and automate tasks in Unix-based systems — a vital skill for deploying and managing Python applications.

---

### `oop/` — **Object-Oriented Programming in Python**

- Implementing custom classes and methods
- Encapsulation, inheritance, and polymorphism
- Using abstract base classes via `abc`
- Overriding dunder (magic) methods like `__str__`, `__repr__`, `__eq__`
- Applying basic design patterns (Factory, Decorator, etc.)

📌 **Goal:** Build a solid understanding of object-oriented principles and how to structure maintainable, scalable Python code.

---

### `postgres_intro/` — **Databases & SQL with PostgreSQL**

- Designing and creating relational database schemas
- Writing SQL queries: `SELECT`, `JOIN`, `GROUP BY`, subqueries
- Using primary and foreign keys, indexing strategies
- Connecting to PostgreSQL via `psycopg2`
- Executing queries, transactions, and handling exceptions

📌 **Goal:** Learn how to model, query, and interact with a relational database from Python applications.

---

### `sockets/` — **Low-Level Network Programming**

- Working with TCP and UDP sockets using Python’s `socket` module
- Building basic client-server applications (e.g., chat server)
- Handling concurrent connections with `threading` and `select`
- Graceful error handling and timeouts
- Understanding data serialization and basic protocol design

📌 **Goal:** Gain hands-on experience in building communication protocols and understanding network-level data flow.

---

### `flask_project/` — **Mini Web Application with Flask**

- Defining routes and views with `@app.route`
- Creating dynamic HTML templates using Jinja2
- Handling HTTP methods (GET, POST), forms, and user input validation
- Connecting to a PostgreSQL database via SQLAlchemy ORM
- Managing models, relationships, and migrations
- Implementing a clean UI with Bootstrap

📌 **Goal:** Develop a fully functional web application with persistent storage and server-side logic using Python.

---

## ⚙️ Tech Stack

- **Language:** Python 3.10+
- **Web Framework:** Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Other Tools:** Bash, cron, systemd, socket API, Jinja2

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/jafaul/homework.git
cd homework

# Example: Run the Flask project
cd flask_project
pip install -r requirements.txt
python app.py
```

---

## 📚 Purpose & Learning Goals

This repository serves both as an educational log and a practical portfolio. Each task emphasizes:

- Writing clean, readable, and modular code
- Following SOLID and DRY principles
- Building from foundational system-level skills to full-stack web development

---