import databaseconnection

def insert_results(track_id, driver_positions, results):
    conn = databaseconnection.connect()
    cursor = conn.cursor()

    try:
        # Check if results for the given track already exist
        query_check = f"SELECT * FROM {results} WHERE track_id = %s;"
        cursor.execute(query_check, (track_id,))
        existing_results = cursor.fetchall()

        if existing_results:
                query_update = f"""
                    DELETE FROM {results} WHERE track_id = %s;
                """
                cursor.execute(query_update, (track_id,))
        for driver_id, position in driver_positions:
            query_insert = f"INSERT INTO {results} (track_id, driver_id, position) VALUES (%s, %s, %s);"
            cursor.execute(query_insert, (track_id, driver_id, position))

        conn.commit()
        return True  # Indicate successful insertion or update
    except Exception as e:
        print(f"Error inserting or updating results: {e}")
        conn.rollback()
        return False  # Indicate insertion or update failure
    finally:
        conn.close()


def insert_driver(driver_name, driver_team):
    try:
        conn = databaseconnection.connect()
        cursor = conn.cursor()

        # Insert into the 'driver' table
        query = "INSERT INTO driver (driver_name, driver_team) VALUES (%s, %s)"
        cursor.execute(query, (driver_name, driver_team))
        conn.commit()

        return True
    except Exception as e:
        print(f"Error inserting driver data: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def insert_track(track_name, quali_date, race_date):
    try:
        conn = databaseconnection.connect()
        cursor = conn.cursor()

        # Insert into the 'track' table
        query = "INSERT INTO track (track_name, track_quali_date, track_race_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (track_name, quali_date, race_date))
        conn.commit()

        return True
    except Exception as e:
        print(f"Error inserting track data: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()