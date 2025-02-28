from app.database.connection import get_db_cursor

class Result:
    """Base class for race results."""
    
    @staticmethod
    def get_available_races():
        """Get races with available results."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT t.track_name, t.track_race_date
                FROM track t
                JOIN raceresults r ON t.id = r.track_id
                ORDER BY t.track_race_date
            """)
            return [race[0] for race in cursor.fetchall()]
    
    @staticmethod
    def insert_driver(driver_name, team_name):
        """Insert a new driver."""
        with get_db_cursor(commit=True) as cursor:
            # First ensure team exists
            cursor.execute(
                "INSERT INTO team (team_name) VALUES (%s) ON CONFLICT (team_name) DO UPDATE SET team_name = EXCLUDED.team_name RETURNING team_id",
                (team_name,)
            )
            team_id = cursor.fetchone()[0]
            
            # Then create driver with team_id and set active to true by default
            cursor.execute(
                "INSERT INTO driver (driver_name, team_id, active) VALUES (%s, %s, true) RETURNING driver_id",
                (driver_name, team_id)
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def insert_track(track_name, quali_date, race_date):
        """Insert a new track."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO track (track_name, track_quali_date, track_race_date) VALUES (%s, %s, %s) RETURNING id",
                (track_name, quali_date, race_date)
            )
            return cursor.fetchone()[0]


class QualifyingResult(Result):
    """Model for qualifying results."""
    
    @staticmethod
    def get_result(track_id):
        """Get qualifying results for a track."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM qualiresults WHERE track_id = %s ORDER BY position",
                (track_id,)
            )
            return cursor.fetchall()
    
    @staticmethod
    def insert_results(track_id, results):
        """Insert qualifying results.
        
        Args:
            track_id: The track ID.
            results: A list of tuples (driver_id, position, dnf).
        """
        with get_db_cursor(commit=True) as cursor:
            # Clear existing results for this track
            cursor.execute("DELETE FROM qualiresults WHERE track_id = %s", (track_id,))
            
            # Insert new results
            for driver_id, position, dnf in results:
                cursor.execute(
                    "INSERT INTO qualiresults (track_id, driver_id, position, dnf) VALUES (%s, %s, %s, %s)",
                    (track_id, driver_id, position, dnf)
                )
            return True
    
    @staticmethod
    def get_final_results(track_name):
        """Get final qualifying results for a track by name."""
        with get_db_cursor() as cursor:
            # Get track ID
            cursor.execute("SELECT id FROM track WHERE track_name = %s", (track_name,))
            track_id = cursor.fetchone()[0]
            
            # Get qualifying results
            cursor.execute("""
                SELECT d.driver_name, q.position, q.dnf
                FROM qualiresults q
                JOIN driver d ON q.driver_id = d.driver_id
                WHERE q.track_id = %s
                ORDER BY q.position
            """, (track_id,))
            results = cursor.fetchall()
            
            # Format results
            final_results = [driver[0] for driver in results]
            dnfs = [driver[0] for driver in results if driver[2]]
            
            return (final_results, dnfs, None)


class RaceResult(Result):
    """Model for race results."""
    
    @staticmethod
    def get_result(track_id):
        """Get race results for a track."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM raceresults WHERE track_id = %s ORDER BY position",
                (track_id,)
            )
            return cursor.fetchall()
    
    @staticmethod
    def insert_results(track_id, results):
        """Insert race results.
        
        Args:
            track_id: The track ID.
            results: A list of tuples (driver_id, position, dnf).
        """
        with get_db_cursor(commit=True) as cursor:
            # Clear existing results for this track
            cursor.execute("DELETE FROM raceresults WHERE track_id = %s", (track_id,))
            
            # Insert new results
            for driver_id, position, dnf in results:
                cursor.execute(
                    "INSERT INTO raceresults (track_id, driver_id, position, dnf) VALUES (%s, %s, %s, %s)",
                    (track_id, driver_id, position, dnf)
                )
            return True
    
    @staticmethod
    def insert_bonus_results(track_id, fastest_lap, driver_of_day):
        """Insert bonus results for a race.
        
        Args:
            track_id: The track ID.
            fastest_lap: The driver ID with the fastest lap.
            driver_of_day: The driver ID who was driver of the day.
        """
        with get_db_cursor(commit=True) as cursor:
            # Delete any existing bonus results for this track
            cursor.execute("DELETE FROM bonusresults WHERE track = %s", (track_id,))
            
            # Insert new bonus results
            cursor.execute(
                "INSERT INTO bonusresults (track, fl, dod) VALUES (%s, %s, %s)",
                (track_id, fastest_lap, driver_of_day)
            )
            return True
    
    @staticmethod
    def get_final_results(track_name):
        """Get final race results for a track by name."""
        with get_db_cursor() as cursor:
            # Get track ID
            cursor.execute("SELECT id FROM track WHERE track_name = %s", (track_name,))
            track_id = cursor.fetchone()[0]
            
            # Get race results
            cursor.execute("""
                SELECT d.driver_name, r.position, r.dnf
                FROM raceresults r
                JOIN driver d ON r.driver_id = d.driver_id
                WHERE r.track_id = %s
                ORDER BY r.position
            """, (track_id,))
            results = cursor.fetchall()
            
            # Get fastest lap
            cursor.execute("""
                SELECT d.driver_name
                FROM track t
                JOIN driver d ON t.fastest_lap = d.driver_id
                WHERE t.id = %s
            """, (track_id,))
            fastest_lap = cursor.fetchone()
            
            # Format results
            final_results = [driver[0] for driver in results]
            dnfs = [driver[0] for driver in results if driver[2]]
            
            return (final_results, dnfs, fastest_lap[0] if fastest_lap else None) 