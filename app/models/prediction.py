from app.database.connection import get_db_cursor

class Prediction:
    """Base class for predictions."""
    
    @staticmethod
    def get_head_to_head_options(track_id):
        """Get all head-to-head options for a specific track."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT hc.id, d1.driver_name as driver1_name, d2.driver_name as driver2_name
                FROM headtohead_combinations hc
                JOIN driver d1 ON hc.driver1_id = d1.driver_id
                JOIN driver d2 ON hc.driver2_id = d2.driver_id
                WHERE hc.track = %s
                ORDER BY hc.id
            """, (track_id,))
            return cursor.fetchall()
    
    @staticmethod
    def get_head_to_head_prediction(user_id, track_id, poule_id):
        """Get head-to-head predictions for a user, track, and poule."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT hc.id, driverselected 
                FROM headtoheadprediction hp
                JOIN headtohead_combinations hc ON hp.headtohead_id = hc.id
                WHERE hp.user_id = %s AND hp.track = %s AND hp.poule = %s
                ORDER BY hc.id
            """, (user_id, track_id, poule_id))
            return cursor.fetchall()
    
    @staticmethod
    def make_head_to_head_prediction(user_id, headtohead_id, driver_selected, track_id, poule_id):
        """Make a head-to-head prediction."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO headtoheadprediction (user_id, headtohead_id, driverselected, track, poule)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id, headtohead_id, track, poule)
                DO UPDATE SET driverselected = EXCLUDED.driverselected
            """, (user_id, headtohead_id, driver_selected, track_id, poule_id))
            return True


class QualifyingPrediction(Prediction):
    """Model for qualifying predictions (top 3)."""
    
    @staticmethod
    def get_prediction(user_id, track_id, poule_id):
        """Get a user's qualifying prediction for a track and poule."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT driver1_id, driver2_id, driver3_id 
                FROM top3_quali 
                WHERE user_id = %s AND track = %s AND poule = %s
            """, (user_id, track_id, poule_id))
            return cursor.fetchone()
    
    @staticmethod
    def save_prediction(user_id, track_id, poule_id, driver1_id, driver2_id, driver3_id):
        """Save a qualifying prediction."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO top3_quali (user_id, driver1_id, driver2_id, driver3_id, track, date, poule)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
                ON CONFLICT (user_id, track, poule)
                DO UPDATE SET 
                    driver1_id = EXCLUDED.driver1_id, 
                    driver2_id = EXCLUDED.driver2_id, 
                    driver3_id = EXCLUDED.driver3_id,
                    date = CURRENT_TIMESTAMP
            """, (user_id, driver1_id, driver2_id, driver3_id, track_id, poule_id))
            return True
    
    @staticmethod
    def get_results_with_points(user_id, track_id, poule_id):
        """Get qualifying results with points."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d1.driver_name AS driver1_name,
                    t1.team_name AS driver1_team,
                    d2.driver_name AS driver2_name,
                    t2.team_name AS driver2_team,
                    d3.driver_name AS driver3_name,
                    t3.team_name AS driver3_team,
                    driver1points, driver2points, driver3points
                FROM 
                    top3_quali 
                JOIN 
                    driver AS d1 ON top3_quali.driver1_id = d1.driver_id
                JOIN 
                    team AS t1 ON d1.team_id = t1.team_id
                JOIN 
                    driver AS d2 ON top3_quali.driver2_id = d2.driver_id
                JOIN 
                    team AS t2 ON d2.team_id = t2.team_id
                JOIN 
                    driver AS d3 ON top3_quali.driver3_id = d3.driver_id
                JOIN 
                    team AS t3 ON d3.team_id = t3.team_id
                WHERE 
                    top3_quali.poule = %s 
                    AND top3_quali.user_id = %s 
                    AND top3_quali.track = %s
            """, (poule_id, user_id, track_id))
            result = cursor.fetchone()
            
            if not result:
                return [("No prediction made", "", "")]
            
            # Combine driver names with points and team names
            driver_names = result[::2][:3]  # Take every other element for names
            driver_teams = result[1::2][:3]  # Take every other element for teams
            points = result[6:]  # Points start at index 6
            return [(name, point, team) for name, team, point in zip(driver_names, driver_teams, points)]


class RacePrediction(Prediction):
    """Model for race predictions (top 5)."""
    
    @staticmethod
    def get_prediction(user_id, track_id, poule_id):
        """Get a user's race prediction for a track and poule."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT driver1_id, driver2_id, driver3_id, driver4_id, driver5_id 
                FROM top5_race 
                WHERE user_id = %s AND track = %s AND poule = %s
            """, (user_id, track_id, poule_id))
            return cursor.fetchone()
    
    @staticmethod
    def save_prediction(user_id, track_id, poule_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id):
        """Save a race prediction."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO top5_race (user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, track, date, poule)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
                ON CONFLICT (user_id, track, poule)
                DO UPDATE SET 
                    driver1_id = EXCLUDED.driver1_id, 
                    driver2_id = EXCLUDED.driver2_id, 
                    driver3_id = EXCLUDED.driver3_id,
                    driver4_id = EXCLUDED.driver4_id,
                    driver5_id = EXCLUDED.driver5_id,
                    date = CURRENT_TIMESTAMP
            """, (user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, track_id, poule_id))
            return True
    
    @staticmethod
    def get_results_with_points(user_id, track_id, poule_id):
        """Get race results with points."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d1.driver_name AS driver1_name,
                    t1.team_name AS driver1_team,
                    d2.driver_name AS driver2_name,
                    t2.team_name AS driver2_team,
                    d3.driver_name AS driver3_name,
                    t3.team_name AS driver3_team,
                    d4.driver_name AS driver4_name,
                    t4.team_name AS driver4_team,
                    d5.driver_name AS driver5_name,
                    t5.team_name AS driver5_team,
                    driver1points, driver2points, driver3points, driver4points, driver5points
                FROM 
                    top5_race 
                JOIN 
                    driver AS d1 ON top5_race.driver1_id = d1.driver_id
                JOIN 
                    team AS t1 ON d1.team_id = t1.team_id
                JOIN 
                    driver AS d2 ON top5_race.driver2_id = d2.driver_id
                JOIN 
                    team AS t2 ON d2.team_id = t2.team_id
                JOIN 
                    driver AS d3 ON top5_race.driver3_id = d3.driver_id
                JOIN 
                    team AS t3 ON d3.team_id = t3.team_id
                JOIN 
                    driver AS d4 ON top5_race.driver4_id = d4.driver_id
                JOIN 
                    team AS t4 ON d4.team_id = t4.team_id
                JOIN 
                    driver AS d5 ON top5_race.driver5_id = d5.driver_id
                JOIN 
                    team AS t5 ON d5.team_id = t5.team_id
                WHERE 
                    top5_race.poule = %s 
                    AND top5_race.user_id = %s 
                    AND top5_race.track = %s
            """, (poule_id, user_id, track_id))
            result = cursor.fetchone()
            
            if not result:
                return [("No prediction made", "", "")]
            
            # Combine driver names with points and team names
            driver_names = result[::2][:5]  # Take every other element for names
            driver_teams = result[1::2][:5]  # Take every other element for teams
            points = result[10:]  # Points start at index 10
            return [(name, point, team) for name, team, point in zip(driver_names, driver_teams, points)]


class BonusPrediction(Prediction):
    """Model for bonus predictions (fastest lap, DNF, driver of the day)."""
    
    @staticmethod
    def get_prediction(user_id, track_id, poule_id):
        """Get a user's bonus predictions for a track and poule."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT fastestlap, dnf, dod 
                FROM bonusprediction 
                WHERE user_id = %s AND track = %s AND poule = %s
            """, (user_id, track_id, poule_id))
            return cursor.fetchone()
    
    @staticmethod
    def save_prediction(user_id, track_id, poule_id, fastest_lap, dnf, driver_of_day):
        """Save bonus predictions."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO bonusprediction (user_id, poule, track, fastestlap, dnf, dod)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, poule, track)
                DO UPDATE SET 
                    fastestlap = EXCLUDED.fastestlap, 
                    dnf = EXCLUDED.dnf, 
                    dod = EXCLUDED.dod
            """, (user_id, poule_id, track_id, fastest_lap, dnf, driver_of_day))
            return True
    
    @staticmethod
    def get_results_with_points(user_id, track_id, poule_id):
        """Get bonus results with points."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d1.driver_name AS fastestlap_name,
                    t1.team_name AS fastestlap_team,
                    d2.driver_name AS dnf_name,
                    t2.team_name AS dnf_team,
                    d3.driver_name AS dod_name,
                    t3.team_name AS dod_team,
                    flpoints, dnfpoints, dodpoints
                FROM 
                    bonusprediction 
                LEFT JOIN 
                    driver AS d1 ON bonusprediction.fastestlap = d1.driver_id
                LEFT JOIN 
                    team AS t1 ON d1.team_id = t1.team_id
                LEFT JOIN 
                    driver AS d2 ON bonusprediction.dnf = d2.driver_id
                LEFT JOIN 
                    team AS t2 ON d2.team_id = t2.team_id
                LEFT JOIN 
                    driver AS d3 ON bonusprediction.dod = d3.driver_id
                LEFT JOIN 
                    team AS t3 ON d3.team_id = t3.team_id
                WHERE 
                    bonusprediction.poule = %s 
                    AND bonusprediction.user_id = %s 
                    AND bonusprediction.track = %s
            """, (poule_id, user_id, track_id))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Create a dictionary with the results
            return {
                'fastest_lap': {'name': result[0] or 'None', 'team': result[1] or 'no_team', 'points': result[6]},
                'dnf': {'name': result[2] or 'None', 'team': result[3] or 'no_team', 'points': result[7]},
                'driver_of_day': {'name': result[4] or 'None', 'team': result[5] or 'no_team', 'points': result[8]}
            } 