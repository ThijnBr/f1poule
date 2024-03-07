import databaseconnection

def getPoules(userid):
    query = """
        SELECT poules.poule_id, poules.poule_name
        FROM user_poule
        JOIN poules ON user_poule.poule_id = poules.poule_id
        WHERE user_poule.user_id = %s;
    """
    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (userid,))
        poules = cursor.fetchall()
    return poules

def getPouleUsers(pouleid):
    userquery = """SELECT users.user_id, username FROM user_poule
                    JOIN users ON users.user_id = user_poule.user_id
                    WHERE poule_id = %s"""
    
    top3query = """SELECT SUM(driver1points + driver2points + driver3points) as totalpoints FROM top3_quali
                    WHERE poule = %s AND user_id = %s
                    GROUP BY user_id, poule"""
    
    top5query = """SELECT SUM(driver1points + driver2points + driver3points + driver4points + driver5points) as totalpoints FROM top5_race
                    WHERE poule = %s AND user_id = %s
                    GROUP BY user_id, poule"""
    hthquery = """SELECT SUM(points) FROM headtoheadprediction WHERE poule = %s AND user_id = %s GROUP BY user_id, poule"""
    bonusquery = "SELECT SUM(flpoints + dnfpoints + dodpoints) FROM bonusprediction WHERE poule = %s AND user_id = %s GROUP BY user_id, poule"
    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(userquery, (pouleid,))
        users = cursor.fetchall()

        namepoints = []
        for x in users:
            totalpoints = 0

            cursor.execute(top3query, (pouleid, x[0]))
            points = cursor.fetchone()
            if points != None:
                totalpoints += points[0]
                
            cursor.execute(top5query, (pouleid, x[0]))
            points = cursor.fetchone()
            if points != None:
                totalpoints += points[0]

            cursor.execute(hthquery, (pouleid, x[0]))
            points = cursor.fetchone()
            try:
                if points != None:
                    totalpoints += points[0]
            except:
                print(points)

            cursor.execute(bonusquery, (pouleid, x[0]))
            points = cursor.fetchone()
            try:
                if points != None:
                    totalpoints += points[0]
            except:
                print(points)


            print(x[1], totalpoints)

            namepoints.append((x[1], totalpoints))
            
    sorted_namepoints = sorted(namepoints, key=lambda x: x[1], reverse=True)
    print(sorted_namepoints)
    return sorted_namepoints

def joinPoule(poulename, userid):
    query_select = "SELECT poule_id FROM poules WHERE poule_name = %s;"
    query_insert = "INSERT INTO user_poule (user_id, poule_id) VALUES (%s, %s);"
    
    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query_select, (poulename,))
        poule_id = cursor.fetchone()
        
        if poule_id:
            cursor.execute(query_insert, (userid, poule_id[0]))
            conn.commit()

def getTop3Open(pouleid, userid, trackid):
    query = "SELECT driver1_id, driver2_id, driver3_id FROM top3_quali WHERE poule = %s AND user_id = %s AND track = %s"
    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (pouleid, userid, trackid))
        data = cursor.fetchone()
        return data

def getTop5Open(pouleid, userid, trackid):
    query = "SELECT driver1_id, driver2_id, driver3_id, driver4_id, driver5_id FROM top5_race WHERE poule = %s AND user_id = %s AND track = %s"
    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (pouleid, userid, trackid))
        data = cursor.fetchone()
        return data
    
def getTop3Closed(pouleid, userid, trackid):
    query = """
        SELECT 
            d1.driver_name AS driver1_name, 
            d2.driver_name AS driver2_name, 
            d3.driver_name AS driver3_name 
        FROM 
            top3_quali 
        JOIN 
            driver AS d1 ON top3_quali.driver1_id = d1.driver_id
        JOIN 
            driver AS d2 ON top3_quali.driver2_id = d2.driver_id
        JOIN 
            driver AS d3 ON top3_quali.driver3_id = d3.driver_id
        WHERE 
            top3_quali.poule = %s 
            AND top3_quali.user_id = %s 
            AND top3_quali.track = %s
    """

    query2 = "SELECT driver1points, driver2points, driver3points FROM top3_quali WHERE poule = %s AND user_id = %s AND track = %s"

    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (pouleid, userid, trackid))
        top3_names = cursor.fetchone()

        cursor.execute(query2, (pouleid, userid, trackid))
        points = cursor.fetchone()

        lst = []
        try:
            for name, point in zip(top3_names, points):
                lst.append((name, point))
        except:
            lst.append(("No prediction made", ""))

        return lst

    
def getTop5Closed(pouleid, userid, trackid):
    query = """
        SELECT 
            d1.driver_name AS driver1_name, 
            d2.driver_name AS driver2_name, 
            d3.driver_name AS driver3_name, 
            d4.driver_name AS driver4_name, 
            d5.driver_name AS driver5_name
        FROM 
            top5_race 
        JOIN 
            driver AS d1 ON top5_race.driver1_id = d1.driver_id
        JOIN 
            driver AS d2 ON top5_race.driver2_id = d2.driver_id
        JOIN 
            driver AS d3 ON top5_race.driver3_id = d3.driver_id
        JOIN 
            driver AS d4 ON top5_race.driver4_id = d4.driver_id
        JOIN 
            driver AS d5 ON top5_race.driver5_id = d5.driver_id
        WHERE 
            top5_race.poule = %s 
            AND top5_race.user_id = %s 
            AND top5_race.track = %s
    """

    query2 = "SELECT driver1points, driver2points, driver3points, driver4points, driver5points FROM top5_race WHERE poule = %s AND user_id = %s AND track = %s"

    with databaseconnection.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (pouleid, userid, trackid))
        top5_names = cursor.fetchone()

        cursor.execute(query2, (pouleid, userid, trackid))
        points = cursor.fetchone()

        lst = []
        try:
            for name, point in zip(top5_names, points):
                lst.append((name, point))
        except:
            lst.append(("No prediction made", ""))

        return lst