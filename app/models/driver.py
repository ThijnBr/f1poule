from app.database.connection import get_db_cursor

class Driver:
    """Driver model for F1 drivers."""
    
    def __init__(self, driver_id=None, driver_name=None, team=None):
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.team = team
    
    @classmethod
    def get_all(cls, active_only=False, exclude_active=False):
        """Get all drivers.
        
        Args:
            active_only: If True, only return active drivers.
            exclude_active: If True, only return inactive drivers. Ignored if active_only is True.
        """
        with get_db_cursor() as cursor:
            query = """
                SELECT d.driver_id, d.driver_name, t.team_name, d.active 
                FROM driver d
                JOIN team t ON d.team_id = t.team_id
            """
            if active_only:
                query += " WHERE d.active = true"
            elif exclude_active:
                query += " WHERE d.active = false"
            query += " ORDER BY d.driver_name"  # Sort alphabetically by default
            cursor.execute(query)
            drivers = cursor.fetchall()
            return drivers
    
    @classmethod
    def get_by_id(cls, driver_id):
        """Get a driver by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, d.driver_name, t.team_name 
                FROM driver d
                JOIN team t ON d.team_id = t.team_id
                WHERE d.driver_id = %s
            """, (driver_id,))
            driver_data = cursor.fetchone()
            
            if driver_data:
                return cls(
                    driver_id=driver_data[0],
                    driver_name=driver_data[1],
                    team=driver_data[2]
                )
            return None
    
    @classmethod
    def create(cls, driver_name, team_name):
        """Create a new driver."""
        with get_db_cursor(commit=True) as cursor:
            # First ensure team exists
            cursor.execute(
                "INSERT INTO team (team_name) VALUES (%s) ON CONFLICT (team_name) DO UPDATE SET team_name = EXCLUDED.team_name RETURNING team_id",
                (team_name,)
            )
            team_id = cursor.fetchone()[0]
            
            # Then create driver with team_id
            cursor.execute(
                "INSERT INTO driver (driver_name, team_id) VALUES (%s, %s) RETURNING driver_id",
                (driver_name, team_id)
            )
            driver_id = cursor.fetchone()[0]
            return cls(driver_id=driver_id, driver_name=driver_name, team=team_name)

    @classmethod
    def update(cls, driver_id, driver_name, team_name):
        """Update a driver's information."""
        with get_db_cursor(commit=True) as cursor:
            # First ensure team exists and get team_id
            cursor.execute(
                "INSERT INTO team (team_name) VALUES (%s) ON CONFLICT (team_name) DO UPDATE SET team_name = EXCLUDED.team_name RETURNING team_id",
                (team_name,)
            )
            team_id = cursor.fetchone()[0]
            
            # Then update driver
            cursor.execute(
                "UPDATE driver SET driver_name = %s, team_id = %s WHERE driver_id = %s",
                (driver_name, team_id, driver_id)
            )

    @classmethod
    def delete(cls, driver_id):
        """Delete a driver and all associated data."""
        with get_db_cursor(commit=True) as cursor:
            # Delete all associated data in the correct order to respect foreign key constraints
            
            # Delete race and qualifying results
            cursor.execute("DELETE FROM raceresults WHERE driver_id = %s", (driver_id,))
            cursor.execute("DELETE FROM qualiresults WHERE driver_id = %s", (driver_id,))
            
            # Delete predictions
            cursor.execute("""
                DELETE FROM top3_quali 
                WHERE driver1_id = %s OR driver2_id = %s OR driver3_id = %s
            """, (driver_id, driver_id, driver_id))
            
            cursor.execute("""
                DELETE FROM top5_race 
                WHERE driver1_id = %s OR driver2_id = %s OR driver3_id = %s 
                OR driver4_id = %s OR driver5_id = %s
            """, (driver_id, driver_id, driver_id, driver_id, driver_id))
            
            # Delete bonus predictions and results
            cursor.execute("""
                DELETE FROM bonusprediction 
                WHERE fastestlap = %s OR dnf = %s OR dod = %s
            """, (driver_id, driver_id, driver_id))
            
            cursor.execute("""
                DELETE FROM bonusresults 
                WHERE fl = %s OR dod = %s
            """, (driver_id, driver_id))
            
            # Delete head-to-head predictions that reference this driver
            cursor.execute("""
                DELETE FROM headtoheadprediction
                WHERE headtohead_id IN (
                    SELECT id FROM headtohead_combinations 
                    WHERE driver1_id = %s OR driver2_id = %s
                )
            """, (driver_id, driver_id))
            
            # Delete head-to-head combinations
            cursor.execute("""
                DELETE FROM headtohead_combinations 
                WHERE driver1_id = %s OR driver2_id = %s
            """, (driver_id, driver_id))
            
            # Finally delete the driver
            cursor.execute("DELETE FROM driver WHERE driver_id = %s", (driver_id,)) 