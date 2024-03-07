import databaseconnection

def getHeadToHead(conn):
    query = """SELECT h.id, d1.driver_name AS driver1_name, d2.driver_name AS driver2_name
                FROM headtohead h
                JOIN driver d1 ON h.driver1_id = d1.driver_id
                JOIN driver d2 ON h.driver2_id = d2.driver_id;
                """
    cursor = conn.cursor()
    cursor.execute(query)
    hth = cursor.fetchall()
    return hth

def getHthPoints(user_id, track, poule):
    conn = databaseconnection.connect()
    query = "SELECT points FROM headtoheadprediction WHERE user_id = %s AND track = %s AND poule = %s ORDER BY headtohead_id"
    cursor = conn.cursor()
    cursor.execute(query, (user_id, track, poule))
    hth = cursor.fetchall()
    return hth

def getPredictions(user_id, track, poule, conn):
    query = """SELECT headtohead_id, driverselected 
                FROM headtoheadprediction 
                WHERE user_id = %s AND track = %s AND poule = %s"""
    cursor = conn.cursor()
    cursor.execute(query,(user_id, track, poule))
    data = cursor.fetchall()
    return data

def makePredictions(user_id, headtohead_id, driverselected, track, poule):
    query = """INSERT INTO headtoheadprediction (user_id, headtohead_id, driverselected, track, poule)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (user_id, headtohead_id, track, poule) DO UPDATE
               SET
                   driverselected = EXCLUDED.driverselected
            """
    conn = databaseconnection.connect()
    cursor = conn.cursor()
    cursor.execute(query,(user_id, headtohead_id, driverselected, track, poule))
    conn.commit()