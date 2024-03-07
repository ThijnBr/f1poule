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
            elif difference > 9:
                points.append(0)
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

def getHeadtohead(track_id):
    conn = databaseconnection.connect()
    query = """SELECT headtoheadprediction.id, driver1_id, driver2_id, driverselected FROM headtoheadprediction
            JOIN headtohead ON headtohead.id = headtoheadprediction.headtohead_id WHERE track = %s"""
    cursor = conn.cursor()
    cursor.execute(query, (track_id,))
    hth = cursor.fetchall()
    return hth

def calcQualiPoints(trackid):
    conn = databaseconnection.connect()
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
        print(points)

        id = x[0]
        query = "UPDATE top3_quali SET driver1points = %s, driver2points = %s, driver3points = %s WHERE id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (points[0], points[1], points[2], id))
    conn.commit()
    conn.close()

calcQualiPoints(3)

def calcRacePoints(trackid):
    conn = databaseconnection.connect()
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

        cursor = conn.cursor()
        cursor.execute(query, (points[0], points[1], points[2],points[3], points[4], id))
    conn.commit()
    conn.close()
    
import databaseconnection  # Make sure to import your database connection module

def calcHeadtoHead(trackid, conn):
    results_data = [x[0] for x in getRaceResult(trackid)]
    predictions = getHeadtohead(trackid)

    # Create a list to store the updated records
    updated_records = []

    for prediction in predictions:
        updated_records.append(calcHth(results_data, *prediction))
    updateHthPoints(updated_records, conn)

def calcHth(driver_ids, id, driver1_id, driver2_id, is_reversed):
    print(driver1_id, driver2_id, is_reversed)

    if driver1_id not in driver_ids or driver2_id not in driver_ids:
        raise ValueError("Invalid driver IDs in the provided list")

    index_driver1 = driver_ids.index(driver1_id)
    index_driver2 = driver_ids.index(driver2_id)
    if (index_driver1 < index_driver2) != is_reversed:
        return (id, 15)
    else:
        return (id, 0)

def updateHthPoints(records, conn):
    query = "UPDATE headtoheadprediction SET points = %s WHERE id = %s"
    
    with conn.cursor() as cursor:
        cursor.executemany(query, records)

import bonus
def getDnfs(track, conn):
    query = "SELECT driver_id FROM raceresults WHERE track_id = %s AND dnf = true"
    cursor = conn.cursor()
    cursor.execute(query, (track,))
    data = cursor.fetchall()
    return data

def updateBonus(id, x, points, conn):
    query = f"UPDATE bonusprediction SET {x} = %s WHERE id = %s "
    cursor = conn.cursor()
    cursor.execute(query, (points, id))

def getBonusPredictions(track, conn):
    query = "SELECT id, fastestlap, dnf, dod FROM bonusprediction WHERE track = %s"
    cursor = conn.cursor()
    cursor.execute(query, (track,))
    data = cursor.fetchall()
    print(data)
    results = bonus.getBonusResults(track, conn)
    dnfs = getDnfs(track)
    dnfList = []
    for x in dnfs:
        dnfList.append(x[0])
    print(dnfList)
    for x in data:
        if x[1] == results[0]:
            updateBonus(x[0], 'flpoints', 15)
        else:
            updateBonus(x[0], 'flpoints', 0)
        if x[3] == results[1]:
            updateBonus(x[0], 'dodpoints', 15)
        else:
            updateBonus(x[0], 'dodpoints', 0)
        if x[2] in dnfList:
            updateBonus(x[0], 'dnfpoints', 15)
        elif x[2] == None and dnfList == []:
            updateBonus(x[0], 'dnfpoints', 15)
        else:
            updateBonus(x[0], 'dnfpoints', 0)
    conn.commit()

