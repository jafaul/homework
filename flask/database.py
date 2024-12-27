import psycopg2

from config import config

conn = psycopg2.connect(
    database=config.DB_NAME,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    host="db",
    port=config.DB_PORT
)
