from flask import Flask, request, render_template,jsonify
import sqlite3
import asyncio

app = Flask(__name__)

def create_connection():
    conn = sqlite3.connect("user_data.db")
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS user_data (id INTEGER PRIMARY KEY)")
    conn.commit()

def add_column(conn, column_name):
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE user_data ADD COLUMN '{}' TEXT".format(column_name))
    except:
        pass
    conn.commit()

def store_data_in_database(data):
    conn = create_connection()
    create_table(conn)
    key = data["key"]
    column_name = data["column_name"]
    column_value = data["value"]
    add_column(conn, column_name)   
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO user_data ( id, {column_name} ) VALUES ('{key}','{column_value}')" )
    except:            
        c.execute(f"UPDATE user_data set {column_name} = '{column_value}' where id = '{key}'")
    conn.commit()
    conn.close()
    

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":                       
        data = request.form        
        store_data_in_database(data)
                

    return render_template("index.html")

if __name__ == "__main__":
    app.run()
