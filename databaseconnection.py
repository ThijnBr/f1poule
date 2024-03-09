import psycopg2
def connect():
    conn = psycopg2.connect(
        database='poulef1',
        user='postgres',
        password='Broekie2004',
        host='172.23.210.63'
    )
    return conn
