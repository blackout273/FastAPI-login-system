import mysql.connector
from dotenv import load_dotenv
load_dotenv()
import os
 
def connect():
    db = mysql.connector.connect(
    host='localhost',
    user= 'root',
    password='12345678',
    database='python_teste'
    )
    return db