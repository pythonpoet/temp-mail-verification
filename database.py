import sqlite3
import psycopg2
import pandas as pd
from typing import List
import numpy as np

class Database:
    def __init__(self, db_name: str, db_type: str = "sqlite", db_user: str = None, db_password: str = None, db_host: str = None):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.db_type = db_type

        if db_type == "sqlite":
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
        elif db_type == "postgres":
            self.conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        self.cursor = self.conn.cursor()
        # table declaration
        self.create_userID_table()
        self.create_token_list_table()
        print(f"Initialize {db_type} database with db_name: {self.db_name}")
        

    def __del__(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print(f"Destructing {self.db_type} database instance: {self.db_name}")

    def create_userID_table(self):
        # Define the SQL command to create the table
        create_table_query =   """
        CREATE TABLE IF NOT EXISTS users (
            id text PRIMARY KEY
        );
            """
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("Country table created successfully.")

    def create_token_list_table(self):
        # Define the SQL command to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS token_list (
            id serial PRIMARY KEY,
            token text NOT NULL,
            timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        self.conn.commit()
        print("Token table created successfully.")

    def insert_userID(self,user_id:str):
        # Define the SQL command to insert the user ID into the users table
        insert_query = f"INSERT INTO users (id) VALUES ({user_id})"
        self.cursor.execute(insert_query)
        self.conn.commit()
        print(f"user id: {user_id} registered in db successfully")

    def check_token_exists(self, token):
        # Define the SQL command to check if the token exists
        insert_query = f"SELECT EXISTS(SELECT 1 FROM token_list WHERE token='{token}');"
        self.cursor.execute(insert_query)
        return self.cursor.fetchone()[0]

    def insert_token(self, token):
        # Define the SQL command to insert a token
        insert_query = f"INSERT INTO token_list (token) VALUES ('{token}');"
        print("token: %s" % token)
        self.cursor.execute(insert_query)
        self.conn.commit()

    def delete_token(self, token):
        # Define the SQL command to delete a token
        delete_query = "DELETE FROM token_list WHERE token = '%s';"
        self.cursor.execute(delete_query)
        self.conn.commit()

    def user_id_already_exists(self, user_id):
        # Define the SQL command to check if the user ID exists in the users table
        insert_query = f"SELECT * FROM users WHERE id = {user_id}"
        self.cursor.execute(insert_query)
        result = self.cursor.fetchone()
        return result is None

    def insert_userID(self,user_id:str):
        # Define the SQL command to insert the user ID into the users table
        insert_query = f"INSERT INTO users (id) VALUES ({user_id})"
        self.cursor.execute(insert_query)
        self.conn.commit()
        print(f"user id: {user_id} registered in db successfully")

    def user_id_already_exists(self, user_id):
        # Define the SQL command to check if the user ID exists in the users table
        insert_query = f"SELECT * FROM users WHERE id = '{user_id}'"
        self.cursor.execute(insert_query)
        result = self.cursor.fetchone()
        return result is not None