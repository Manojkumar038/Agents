import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Manoj@123",
    database="employees"
)

print("Connected successfully")
conn.close()