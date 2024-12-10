import psycopg2
import logging
def get_db_connection():
    return psycopg2.connect(
        dbname="IMBANK",
        user="postgres",
        password="021202",
        host="localhost",
        port="5432"
    )


