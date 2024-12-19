--
-- [ ] Описати за допомогою SQL систему таблиць, яка буде зберігати інформацію для школи:
-- * Користувач
--   1. Id
--   2. Email
--   3. Пароль
--   4. Ім’я
--   5. Прізвище
--   6. Ім’я собаки
--   7. Фото (Опціонально)
--
CREATE TABLE "user" (
    "id" bigserial PRIMARY KEY,
    "email" VARCHAR(36) NOT NULL UNIQUE,
    "password" VARCHAR(36) NOT NULL,
    "name" VARCHAR(36) NOT NULL,
    "surname" VARCHAR(40) NOT NULL,
    "dog_name" VARCHAR(36) NOT NULL,
    "photo" oid

   -- CONSTRAINT "unique_user_id" UNIQUE("id")
    )
;
-- * Курс
--   1. Id
--   2. Посилається на користувача в ролі викладача
--   3. Посилається на багато користувачів в ролі студента
--   4. Назва
--   5. Опис
CREATE TABLE "course" (
    "id" bigserial PRIMARY KEY,
    "teacher_id" bigserial NOT NULL,
    "title" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,

    CONSTRAINT fk_teacher FOREIGN KEY("teacher_id") REFERENCES "user"(id)
);

CREATE TABLE "course_student" (
    "id" bigserial PRIMARY KEY,
    "course_id" bigserial NOT NULL,
    "student_id" bigserial NOT NULL,

    CONSTRAINT fk_course FOREIGN KEY("course_id") REFERENCES "course"(id),
    CONSTRAINT fk_student FOREIGN KEY("student_id") REFERENCES "user"(id),

    UNIQUE("course_id", "student_id")
);
-- * Заняття
--   a. Id
--   b. Посилається на курс
--   c. Назва
--   d. Опис

CREATE TABLE "lecture" (
    "id" bigserial PRIMARY KEY,
    "course_id" bigserial NOT NULL,
    "title" VARCHAR(30) NOT NULL,
    "description" VARCHAR(300),

    CONSTRAINT fk_course FOREIGN KEY("course_id") REFERENCES "course"(id)
    )
;
--
-- * Домашнє завдання
--   1. Id
--   2. Посилається на курс
--   3. Опис
--   4. Максимальна оцінка
    CREATE TABLE "task" (
    "id" bigserial PRIMARY KEY,
    "course_id" bigserial NOT NULL,
    "description" VARCHAR(300),
    "max_mark" smallint NOT NULL DEFAULT 5,

    CONSTRAINT fk_course FOREIGN KEY("course_id") REFERENCES "course"(id)
    );


--
-- * Відповідь на домашнє завдання
--   1. Id
--   2. Посилається на завдання
--   3. Опис
--   4. Посилається на студента
--   5. Оцінка
CREATE TABLE "answer"(
    "id" bigserial PRIMARY KEY,
    task_id bigserial NOT NULL,
    "description" VARCHAR(300),
    "student_id" bigserial NOT NULL,
    "mark" smallint,

    CONSTRAINT fk_task FOREIGN KEY(task_id) REFERENCES "task"(id),
    CONSTRAINT fk_student FOREIGN KEY("student_id") REFERENCES "user"(id)

    )
;
-- 📌 Завдання 3
--
-- [ ] Зробити ще один sql скрипт, який буде змінювати таблиці
-- * Додає користувачу поле Номер телефону та видаляє Ім’я собаки
    ALTER TABLE "user" ADD "phone_number" VARCHAR(17);
    ALTER TABLE "user" DROP COLUMN "dog_name";
-- * Додає нову Таблицю “Оцінка ДЗ”
--   1. Id
--   2. Посилання на відповідь
--   3. Дата
--   4. Оцінка
--   5. Посилання на вчителя
CREATE TABLE "mark" (
    "id" bigserial PRIMARY KEY,
    "answer_id" bigserial NOT NULL,
    "date" DATE DEFAULT now(),
    "mark" smallint NOT NULL,
    "teacher_id" bigserial NOT NULL,

    CONSTRAINT fk_answer FOREIGN KEY("answer_id") REFERENCES "answer"(id),
    CONSTRAINT fk_teacher FOREIGN KEY("teacher_id") REFERENCES "user"(id)
    )
;

-- * Додає дедлайн до ДЗ
ALTER TABLE "task" ADD "deadline" DATE DEFAULT now();
-- * Додає дату здачі до відповіді
ALTER TABLE "answer" ADD "submission_date" DATE DEFAULT now();

-- todo check poetry

-- todo geeks for geek (data structer, algorithms courses), leetcode.com, теория множеств

-- todo read flask doc, pep8

-- 0 форма
    --  нет порядка строк и столбцов(2)

-- 1 нормальная форма:
 -- 3. нет одинаковых строк
 -- 4. каждое пересечение колонки и столбца содерждит только одно значение (в ячейке только одно значение)
 -- 5. в кажой ячейке только одно атомарное значение
 -- 6. в столбце данные одного типа

-- 2 нормальная форма
  -- в таблицу не молжно быть данных которые можно получить зная только половину ключа

-- 3 нормальная форма зависят от значения других неключевых столбцов)
    -- ни одна колонка не может быть выведена из другой колонки (например колонка ребенок и колонка год рождения это нарушение)

----------------------------------------------------------------------------
-- усиленный вариант 3нф Boyce-Codd Normal Form (BCNF)
    -- каждый атрибут зависит от одного суперключа

-- 4 nf
    -- нетривиальная многозначная зависимость

----------------------------------------------------------------------------
-- 5 nf (нужно углубляться с специфику исходных данных)

-- 6 nf для хронологических бд

-- денормализация для ускорения в крайнем случае)