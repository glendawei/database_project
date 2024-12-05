import psycopg2
import logging
def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="yokura",
        password="123",
        host="localhost",
        port="5432"
    )