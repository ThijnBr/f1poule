import databaseconnection

def register(username, password):
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    conn = databaseconnection.connect()
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    conn.commit()
