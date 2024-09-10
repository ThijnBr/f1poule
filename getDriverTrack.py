import databaseconnection


def getDriver(conn):
    query = "SELECT * FROM driver"
    cursor = conn.cursor()
    cursor.execute(query)
    drivers = cursor.fetchall()
    return drivers

def getTracks(conn):
    query = "SELECT * FROM track ORDER BY track_race_date"
    cursor = conn.cursor()
    cursor.execute(query)
    tracks = cursor.fetchall()
    return tracks

def getRaceResult(trackid):
    conn = databaseconnection.connect()
    query = "SELECT * FROM raceresults  WHERE track_id = %s ORDER BY position"
    cursor = conn.cursor()
    cursor.execute(query, (trackid,))
    result = cursor.fetchall()
    conn.close()
    return result

def getQualiResult(trackid):
    conn = databaseconnection.connect()
    query = "SELECT * FROM qualiresults  WHERE track_id = %s ORDER BY position"
    cursor = conn.cursor()
    cursor.execute(query, (trackid,))
    result = cursor.fetchall()
    conn.close()
    return result

def getTrackData(trackid, conn):
    query = "SELECT * FROM track WHERE id = %s"
    cursor = conn.cursor()
    cursor.execute(query, (trackid,))
    tracks = cursor.fetchall()
    return tracks

def getUserInfo(user_id, track_id, poule_id, conn):
    queryUser = "SELECT username FROM users WHERE user_id = %s;"
    queryTrack = "SELECT track_name FROM track WHERE id = %s;"
    queryPoule = "SELECT poule_name FROM poules WHERE poule_id = %s;"

    cursor = conn.cursor()
    cursor.execute(queryUser, (user_id,))
    user_name = cursor.fetchone()
    cursor.execute(queryTrack,(track_id,))
    track_name = cursor.fetchone()
    cursor.execute(queryPoule,(poule_id,))
    poule_name = cursor.fetchone()
    cursor.close()
    return (user_name[0], track_name[0], poule_name[0])