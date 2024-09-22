import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='numo'
)

cursor = conn.cursor()