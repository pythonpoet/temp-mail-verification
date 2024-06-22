import sqlite3
import psycopg2
import pandas as pd
from typing import List
import numpy as np
class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        # Connect to SQLite database (creates if it doesn't exist)
        #self.conn = sqlite3.connect(db_name)
        # Connect to the PostgreSQL database
        self.conn = psycopg2.connect(
            dbname="<db_name>",
            user="<db_user>",
            password="<db_password>",
            host="<db_host>"
        )
        # Create a cursor object to execute SQL commands
        self.cursor = self.conn.cursor()
        print(f"Initialise database with db_name: {self.db_name}")

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print(f"Destructing database instance: {self.db_name}")

    def create_userID_table(self):
        # Define the SQL command to create the table
        create_table_query =   """
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY
        );
            """
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("Country table created successfully.")
    def insert_userID(user_id:str):
        # Define the SQL command to insert the user ID into the users table
        insert_query = f"INSERT INTO users (id) VALUES ({user_id})"
        self.cursor.execute(sql_command)
        self.conn.commit()
        print(f"user id: {user_id} registered in db successfully")

    def user_id_already_exists(user_id):
        # Define the SQL command to check if the user ID exists in the users table
        insert_query = f"SELECT * FROM users WHERE id = {user_id}"
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result is None