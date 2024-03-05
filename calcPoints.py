import databaseconnection
import getDriverTrack

def calculate_points(result, prediction):
    points = []
    for i in range(len(prediction)):
        if i < len(result):
            difference = abs(result[i] - prediction[i])
            if difference == 0:
                points.append(25)
            elif difference == 1:
                points.append(18)
            elif difference == 2:
                points.append(15)
            elif difference == 3:
                points.append(12)
            elif difference == 4:
                points.append(10)
            elif difference == 5:
                points.append(8)
            elif difference == 6:
                points.append(6)
            elif difference == 7:
                points.append(4)
            elif difference == 8:
                points.append(2)
            elif difference == 9:
                points.append(1)
    return points


def getRaceResult(trackid):
    conn = databaseconnection.connect()
    query = "SELECT driver_id FROM raceresults  WHERE track_id = %s ORDER BY position"
    cursor = conn.cursor()
    cursor.execute(query, (trackid,))
    result = cursor.fetchall()
    return result

def getQualiResult(trackid):
    conn = databaseconnection.connect()
    query = "SELECT driver_id FROM qualiresults  WHERE track_id = %s ORDER BY position"
    cursor = conn.cursor()
    cursor.execute(query, (trackid,))
    result = cursor.fetchall()
    return result

#id, userid, driver1_id, driver2_id, driver3_id, track, date, poule
def gettop3(track_id):
    conn = databaseconnection.connect()
    query = "SELECT id, driver1_id, driver2_id, driver3_id FROM top3_quali WHERE track = %s"
    cursor = conn.cursor()
    cursor.execute(query, (track_id,))
    top3 = cursor.fetchall()
    return top3

def gettop5(track_id):
    conn = databaseconnection.connect()
    query = "SELECT id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id FROM top5_race WHERE track = %s"
    cursor = conn.cursor()
    cursor.execute(query, (track_id,))
    top5 = cursor.fetchall()
    return top5

def calcQualiPoints(trackid):
    resultsData = getQualiResult(trackid)
    results = []
    for x in resultsData:
        results.append(x[0])

    predictionsData = gettop3(trackid)
    for x in predictionsData:
        prediction = []
        prediction.append(x[1])
        prediction.append(x[2])
        prediction.append(x[3])
        points = calculate_points(results, prediction)

        id = x[0]
        query = "UPDATE top3_quali SET driver1points = %s, driver2points = %s, driver3points = %s WHERE id = %s"

        conn = databaseconnection.connect()
        cursor = conn.cursor()
        cursor.execute(query, (points[0], points[1], points[2], id))
    conn.commit()
    conn.close()

def calcRacePoints(trackid):
    resultsData = getRaceResult(trackid)
    results = []
    for x in resultsData:
        results.append(x[0])
    print(results)

    predictionsData = gettop5(trackid)
    for x in predictionsData:
        prediction = []
        prediction.append(x[1])
        prediction.append(x[2])
        prediction.append(x[3])
        prediction.append(x[4])
        prediction.append(x[5])
        points = calculate_points(results, prediction)
        print(points)

        id = x[0]
        query = "UPDATE top5_race SET driver1points = %s, driver2points = %s, driver3points = %s, driver4points = %s, driver5points = %s WHERE id = %s"

        conn = databaseconnection.connect()
        cursor = conn.cursor()
        cursor.execute(query, (points[0], points[1], points[2],points[3], points[4], id))
    conn.commit()
    conn.close()
