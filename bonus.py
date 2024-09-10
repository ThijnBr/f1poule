import databaseconnection
def insertBonus(user_id, poule, track, fl, dnf, dod, conn):
    fl = None if fl == '' else fl
    dnf = None if dnf == '' else dnf
    dod = None if dod == '' else dod
    query = """INSERT INTO bonusprediction (user_id, poule, track, fastestlap, dnf, dod)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (user_id, poule, track)
DO UPDATE SET
  fastestlap = EXCLUDED.fastestlap,
  dnf = EXCLUDED.dnf,
  dod = EXCLUDED.dod;
"""
    cursor = conn.cursor()
    try:
        cursor.execute(query, (user_id, poule, track, fl, dnf, dod))
    except:
        conn.rollback()
    conn.commit()

def getBonus(user_id, poule, track, conn):
    query = "SELECT fastestlap, dnf, dod FROM  bonusprediction WHERE user_id = %s AND poule = %s AND track = %s"
    cursor = conn.cursor()
    cursor.execute(query, (user_id, poule, track))
    data = cursor.fetchall()
    return data

def getBonusResults(track, conn):
    query = "SELECT fl, dod FROM bonusresults WHERE track = %s"
    cursor = conn.cursor()
    cursor.execute(query, (track,))
    data = cursor.fetchall()
    if data != []:
        return data[0]
    
def bonusResultClosed(track, user_id, poule, conn):
    query = """SELECT 
    driver1.driver_name AS fastestlap_name, 
    driver2.driver_name AS dnf_name, 
    driver3.driver_name AS dod_name,
	flpoints, dnfpoints, dodpoints
FROM 
    bonusprediction
LEFT JOIN 
    driver AS driver1 ON bonusprediction.fastestlap = driver1.driver_id
LEFT JOIN 
    driver AS driver2 ON bonusprediction.dnf = driver2.driver_id
LEFT JOIN 
    driver AS driver3 ON bonusprediction.dod = driver3.driver_id
WHERE poule = %s AND user_id = %s AND track = %s

"""
    cursor = conn.cursor()
    cursor.execute(query, (poule, user_id, track))
    data = cursor.fetchall()
    return data