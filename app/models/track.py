from app.database.connection import get_db_cursor
from datetime import datetime

class Track:
    """Track model for F1 race tracks."""
    
    def __init__(self, track_id=None, track_name=None, quali_date=None, race_date=None):
        self.track_id = track_id
        self.track_name = track_name
        self.quali_date = quali_date
        self.race_date = race_date
    
    @classmethod
    def get_all(cls, year=None):
        """Get all tracks ordered by race date.
        
        Args:
            year (int, optional): Filter tracks by year. If None, returns all tracks.
        """
        with get_db_cursor() as cursor:
            if year is not None:
                cursor.execute("""
                    SELECT id, track_name, track_quali_date, track_race_date 
                    FROM track 
                    WHERE EXTRACT(YEAR FROM track_race_date) = %s
                    ORDER BY track_race_date
                """, (year,))
            else:
                cursor.execute("""
                    SELECT id, track_name, track_quali_date, track_race_date 
                    FROM track 
                    ORDER BY track_race_date
                """)
            tracks = cursor.fetchall()
            return tracks
    
    @classmethod
    def get_available_years(cls):
        """Get a list of years that have tracks."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT EXTRACT(YEAR FROM track_race_date)::integer as year
                FROM track
                ORDER BY year DESC
            """)
            return [year[0] for year in cursor.fetchall()]
    
    @classmethod
    def get_by_id(cls, track_id):
        """Get a track by ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, track_name, track_quali_date, track_race_date FROM track WHERE id = %s",
                (track_id,)
            )
            track_data = cursor.fetchone()
            
            if track_data:
                return cls(
                    track_id=track_data[0],
                    track_name=track_data[1],
                    quali_date=track_data[2],
                    race_date=track_data[3]
                )
            return None
    
    @classmethod
    def create(cls, track_name, quali_date, race_date):
        """Create a new track."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO track (track_name, track_quali_date, track_race_date) VALUES (%s, %s, %s) RETURNING id",
                (track_name, quali_date, race_date)
            )
            track_id = cursor.fetchone()[0]
            return cls(track_id=track_id, track_name=track_name, quali_date=quali_date, race_date=race_date)
    
    @classmethod
    def get_upcoming_tracks(cls):
        """Get tracks with upcoming races."""
        now = datetime.now()
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, track_name, track_quali_date, track_race_date FROM track WHERE track_race_date > %s ORDER BY track_race_date",
                (now,)
            )
            tracks = cursor.fetchall()
            return tracks
    
    @classmethod
    def get_past_tracks(cls):
        """Get tracks with past races."""
        now = datetime.now()
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, track_name, track_quali_date, track_race_date FROM track WHERE track_race_date <= %s ORDER BY track_race_date DESC",
                (now,)
            )
            tracks = cursor.fetchall()
            return tracks

    @classmethod
    def update(cls, track_id, track_name, quali_date, race_date):
        """Update a track's information."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE track SET track_name = %s, track_quali_date = %s, track_race_date = %s WHERE id = %s",
                (track_name, quali_date, race_date, track_id)
            )

    @classmethod
    def delete(cls, track_id):
        """Delete a track and all its associated data."""
        with get_db_cursor(commit=True) as cursor:
            # Delete all associated data in the correct order to respect foreign key constraints
            
            # Delete race and qualifying results
            cursor.execute("DELETE FROM raceresults WHERE track_id = %s", (track_id,))
            cursor.execute("DELETE FROM qualiresults WHERE track_id = %s", (track_id,))
            
            # Delete predictions
            cursor.execute("DELETE FROM top3_quali WHERE track = %s", (track_id,))
            cursor.execute("DELETE FROM top5_race WHERE track = %s", (track_id,))
            cursor.execute("DELETE FROM headtoheadprediction WHERE track = %s", (track_id,))
            cursor.execute("DELETE FROM bonusprediction WHERE track = %s", (track_id,))
            
            # Delete bonus results
            cursor.execute("DELETE FROM bonusresults WHERE track = %s", (track_id,))
            
            # Delete head-to-head combinations
            cursor.execute("DELETE FROM headtohead_combinations WHERE track = %s", (track_id,))
            
            # Finally delete the track itself
            cursor.execute("DELETE FROM track WHERE id = %s", (track_id,)) 