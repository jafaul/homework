import psycopg2

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="example",
    host="localhost",
    port="5432"
)
