import psycopg2
import logging
def get_db_connection():
    return psycopg2.connect(
        dbname="IMBANK_NEW",
        user="postgres",
        password="705018",
        host="localhost",
        port="5432"
    )