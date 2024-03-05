import psycopg2
def connect():
    conn = psycopg2.connect(
        database='poulef1',
        user='postgres',
        password='sTEAM.pROJECT',
        host='192.168.1.98'
    )
    return conn
