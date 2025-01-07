import os
import psycopg2
from psycopg2 import OperationalError, sql
from dotenv import load_dotenv

load_dotenv('key.env')

SQL_ADRES = os.getenv("SQL_ADRES")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_PORT = os.getenv("SQL_PORT")

def create_connection():
    try:
        connection = psycopg2.connect(
            host=SQL_ADRES,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            port=SQL_PORT,
            client_encoding='UTF8'
        )

        cursor = connection.cursor()
        print("Успешное подключение к базе данных")
        return connection
    except OperationalError as e:
        print(f"Ошибка подключения: {e}")
        return None

def create_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS slack_messages (
                id SERIAL PRIMARY KEY,
                original_message TEXT,
                original_user_name VARCHAR(100),
                user_name VARCHAR(100),
                channel_name VARCHAR(100),
                date TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Таблица создана")
        except Exception as e:
            print(f"ERORR create table: { e }")
        finally:
            cursor.close()
            connection.close()


def insert_message(original_message, original_user_name, user_name, channel_name, date_normal):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO slack_messages (original_message, original_user_name, user_name, channel_name, date)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (original_message, original_user_name, user_name, channel_name, date_normal))
        connection.commit()
        cursor.close()
        connection.close()
        print("Сообщение добавлено")