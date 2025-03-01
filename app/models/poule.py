from app.database.connection import get_db_cursor
from datetime import datetime

class Poule:
    """Poule model for F1 prediction groups."""
    
    def __init__(self, id=None, name=None, year=None):
        self.id = id
        self.name = name
        self.year = year
    
    @classmethod
    def get_by_id(cls, poule_id):
        """Get a poule by ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT poule_id, poule_name, year 
                FROM poules 
                WHERE poule_id = %s
                """,
                (poule_id,)
            )
            poule_data = cursor.fetchone()
            
            if poule_data:
                return cls(id=poule_data[0], name=poule_data[1], year=poule_data[2])
            return None
    
    @classmethod
    def get_by_name(cls, poule_name):
        """Get a poule by name."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT poule_id, poule_name, year FROM poules WHERE poule_name = %s",
                (poule_name,)
            )
            poule_data = cursor.fetchone()
            
            if poule_data:
                return cls(id=poule_data[0], name=poule_data[1], year=poule_data[2])
            return None

    @classmethod
    def get_all(cls, year=None):
        """Get all poules, optionally filtered by year."""
        with get_db_cursor() as cursor:
            if year:
                cursor.execute(
                    "SELECT poule_id, poule_name, year FROM poules WHERE year = %s ORDER BY year DESC, poule_name",
                    (year,)
                )
            else:
                cursor.execute(
                    "SELECT poule_id, poule_name, year FROM poules ORDER BY year DESC, poule_name"
                )
            return cursor.fetchall()

    @classmethod
    def get_available_years(cls):
        """Get all years that have poules."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT DISTINCT year FROM poules ORDER BY year DESC")
            years = cursor.fetchall()
            return [year[0] for year in years]

    def create(self):
        """Create a new poule."""
        with get_db_cursor(commit=True) as cursor:
            # First, get the next available ID
            cursor.execute("SELECT COALESCE(MAX(poule_id), 0) + 1 FROM poules")
            next_id = cursor.fetchone()[0]
            
            # Insert with explicit ID to avoid sequence issues
            cursor.execute(
                "INSERT INTO poules (poule_id, poule_name, year) VALUES (%s, %s, %s) RETURNING poule_id",
                (next_id, self.name, self.year)
            )
            self.id = cursor.fetchone()[0]
            
            # Update the sequence to match
            cursor.execute(
                "SELECT setval('poules_poule_id_seq', %s)", 
                (self.id,)
            )
            return self.id

    def update(self):
        """Update an existing poule."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE poules SET poule_name = %s, year = %s WHERE poule_id = %s",
                (self.name, self.year, self.id)
            )
            return True

    def delete(self):
        """Delete a poule."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "DELETE FROM poules WHERE poule_id = %s",
                (self.id,)
            )
            return True

    def get_users(self):
        """Get all users in the poule with their total points."""
        with get_db_cursor() as cursor:
            # Get users in the poule
            cursor.execute("""
                SELECT users.user_id, username 
                FROM user_poule
                JOIN users ON users.user_id = user_poule.user_id
                WHERE poule_id = %s
            """, (self.id,))
            users = cursor.fetchall()
            
            # For each user, calculate their total points
            user_points = []
            for user in users:
                user_id = user[0]
                username = user[1]
                total_points = 0
                
                # Get qualifying points
                cursor.execute("""
                    SELECT COALESCE(SUM(driver1points + driver2points + driver3points), 0) as totalpoints 
                    FROM top3_quali
                    WHERE poule = %s AND user_id = %s
                    GROUP BY user_id, poule
                """, (self.id, user_id))
                points = cursor.fetchone()
                total_points += points[0] if points else 0
                
                # Get race points
                cursor.execute("""
                    SELECT COALESCE(SUM(driver1points + driver2points + driver3points + driver4points + driver5points), 0) as totalpoints 
                    FROM top5_race
                    WHERE poule = %s AND user_id = %s
                    GROUP BY user_id, poule
                """, (self.id, user_id))
                points = cursor.fetchone()
                total_points += points[0] if points else 0
                
                # Get head-to-head points
                cursor.execute("""
                    SELECT COALESCE(SUM(points), 0)
                    FROM headtoheadprediction 
                    WHERE poule = %s AND user_id = %s 
                    GROUP BY user_id, poule
                """, (self.id, user_id))
                points = cursor.fetchone()
                total_points += points[0] if points else 0
                
                # Get bonus points
                cursor.execute("""
                    SELECT COALESCE(SUM(flpoints + dnfpoints + dodpoints), 0)
                    FROM bonusprediction 
                    WHERE poule = %s AND user_id = %s 
                    GROUP BY user_id, poule
                """, (self.id, user_id))
                points = cursor.fetchone()
                total_points += points[0] if points else 0
                
                user_points.append((username, total_points, user_id))
            
            # Sort by points (descending)
            return sorted(user_points, key=lambda x: x[1], reverse=True)

    @classmethod
    def get_active_poules(cls):
        """Get all poules from the current year."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT poule_id, poule_name, year 
                FROM poules 
                WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
                ORDER BY poule_name
                """
            )
            return cursor.fetchall()

    @classmethod
    def get_previous_poules(cls):
        """Get all poules from previous years."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT poule_id, poule_name, year 
                FROM poules 
                WHERE year < EXTRACT(YEAR FROM CURRENT_DATE)
                ORDER BY year DESC, poule_name
                """
            )
            return cursor.fetchall()

    @staticmethod
    def get_current_year():
        """Get the current F1 season year based on the next race date."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT EXTRACT(YEAR FROM track_race_date)
                FROM track
                WHERE track_race_date > CURRENT_TIMESTAMP
                ORDER BY track_race_date
                LIMIT 1
                """
            )
            result = cursor.fetchone()
            return result[0] if result else datetime.now().year

    def get_user_points(self, user_id):
        """Get total points for a user in this poule."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                WITH points AS (
                    SELECT COALESCE(SUM(driver1points + driver2points + driver3points), 0) as total_points
                    FROM top3_quali
                    WHERE poule = %s AND user_id = %s
                    UNION ALL
                    SELECT COALESCE(SUM(driver1points + driver2points + driver3points + driver4points + driver5points), 0) as total_points
                    FROM top5_race
                    WHERE poule = %s AND user_id = %s
                    UNION ALL
                    SELECT COALESCE(SUM(points), 0) as total_points
                    FROM headtoheadprediction
                    WHERE poule = %s AND user_id = %s
                    UNION ALL
                    SELECT COALESCE(SUM(flpoints + dnfpoints + dodpoints), 0) as total_points
                    FROM bonusprediction
                    WHERE poule = %s AND user_id = %s
                )
                SELECT SUM(total_points)
                FROM points
                """,
                (self.id, user_id, self.id, user_id, self.id, user_id, self.id, user_id)
            )
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0

    def get_user_rank(self, user_id):
        """Get user's rank in this poule."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                WITH user_points AS (
                    SELECT user_id,
                           (
                               COALESCE((SELECT SUM(driver1points + driver2points + driver3points) 
                                       FROM top3_quali 
                                       WHERE poule = %s AND user_id = u.user_id), 0) +
                               COALESCE((SELECT SUM(driver1points + driver2points + driver3points + driver4points + driver5points) 
                                       FROM top5_race 
                                       WHERE poule = %s AND user_id = u.user_id), 0) +
                               COALESCE((SELECT SUM(points) 
                                       FROM headtoheadprediction 
                                       WHERE poule = %s AND user_id = u.user_id), 0) +
                               COALESCE((SELECT SUM(flpoints + dnfpoints + dodpoints) 
                                       FROM bonusprediction 
                                       WHERE poule = %s AND user_id = u.user_id), 0)
                           ) as total_points
                    FROM user_poule u
                    WHERE poule_id = %s
                ),
                rankings AS (
                    SELECT user_id,
                           RANK() OVER (ORDER BY total_points DESC) as rank
                    FROM user_points
                )
                SELECT rank
                FROM rankings
                WHERE user_id = %s
                """,
                (self.id, self.id, self.id, self.id, self.id, user_id)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    @classmethod
    def get_poules_for_user(cls, user_id):
        """Get all poules for a specific user."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT p.poule_id, p.poule_name, p.year
                FROM poules p
                JOIN user_poule up ON p.poule_id = up.poule_id
                WHERE up.user_id = %s
                ORDER BY p.year DESC, p.poule_name
                """,
                (user_id,)
            )
            poules = cursor.fetchall()
            return [cls(id=p[0], name=p[1], year=p[2]) for p in poules] 