import psycopg2
def connect():
    conn = psycopg2.connect(
        database='poulef1',
        user='postgres',
        password='Broekie2004',
        host='192.168.1.131'
    )
    return conn
