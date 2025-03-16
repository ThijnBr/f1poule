from app.database.connection import get_db_cursor

class PointsCalculator:
    """Service for calculating points for predictions."""
    
    def calculate_qualifying_points(self, track_id):
        """Calculate points for qualifying predictions.
        
        Args:
            track_id: The track ID.
        """
        with get_db_cursor(commit=True) as cursor:
            # Get all qualifying predictions for this track
            cursor.execute("""
                SELECT user_id, driver1_id, driver2_id, driver3_id, poule
                FROM top3_quali
                WHERE track = %s
            """, (track_id,))
            predictions = cursor.fetchall()
            
            # Get qualifying results for this track
            cursor.execute("""
                SELECT driver_id, position
                FROM qualiresults
                WHERE track_id = %s
                ORDER BY position
            """, (track_id,))
            results = cursor.fetchall()
            
            # Create a dictionary of driver positions
            driver_positions = {driver_id: int(position) for driver_id, position in results}
            
            # Calculate points for each prediction
            for user_id, driver1_id, driver2_id, driver3_id, poule in predictions:
                driver1_points = self._calculate_driver_points(driver1_id, 1, driver_positions)
                driver2_points = self._calculate_driver_points(driver2_id, 2, driver_positions)
                driver3_points = self._calculate_driver_points(driver3_id, 3, driver_positions)
                
                # Update points in the database
                cursor.execute("""
                    UPDATE top3_quali
                    SET driver1points = %s, driver2points = %s, driver3points = %s
                    WHERE user_id = %s AND track = %s AND poule = %s
                """, (driver1_points, driver2_points, driver3_points, user_id, track_id, poule))
    
    def calculate_race_points(self, track_id):
        """Calculate points for race predictions.
        
        Args:
            track_id: The track ID.
        """
        with get_db_cursor(commit=True) as cursor:
            # Get all race predictions for this track
            cursor.execute("""
                SELECT user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, poule
                FROM top5_race
                WHERE track = %s
            """, (track_id,))
            predictions = cursor.fetchall()
            
            # Get race results for this track
            cursor.execute("""
                SELECT driver_id, position
                FROM raceresults
                WHERE track_id = %s
                ORDER BY position
            """, (track_id,))
            results = cursor.fetchall()
            
            # Create a dictionary of driver positions
            driver_positions = {driver_id: int(position) for driver_id, position in results}
            
            # Calculate points for each prediction
            for user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, poule in predictions:
                driver1_points = self._calculate_driver_points(driver1_id, 1, driver_positions)
                driver2_points = self._calculate_driver_points(driver2_id, 2, driver_positions)
                driver3_points = self._calculate_driver_points(driver3_id, 3, driver_positions)
                driver4_points = self._calculate_driver_points(driver4_id, 4, driver_positions)
                driver5_points = self._calculate_driver_points(driver5_id, 5, driver_positions)
                
                # Update points in the database
                cursor.execute("""
                    UPDATE top5_race
                    SET driver1points = %s, driver2points = %s, driver3points = %s, driver4points = %s, driver5points = %s
                    WHERE user_id = %s AND track = %s AND poule = %s
                """, (driver1_points, driver2_points, driver3_points, driver4_points, driver5_points, user_id, track_id, poule))
    
    def calculate_head_to_head(self, track_id):
        """Calculate points for head-to-head predictions.
        
        Args:
            track_id: The track ID.
        """
        with get_db_cursor(commit=True) as cursor:
            # Get all head-to-head predictions for this track
            cursor.execute("""
                SELECT user_id, headtohead_id, driverselected, poule
                FROM headtoheadprediction
                WHERE track = %s
            """, (track_id,))
            predictions = cursor.fetchall()
            
            # Get race results for this track
            cursor.execute("""
                SELECT driver_id, position
                FROM raceresults
                WHERE track_id = %s
                ORDER BY position
            """, (track_id,))
            results = cursor.fetchall()
            
            # Create a dictionary of driver positions
            driver_positions = {driver_id: int(position) for driver_id, position in results}
            
            # Get head-to-head combinations for this track
            cursor.execute("""
                SELECT id, driver1_id, driver2_id 
                FROM headtohead_combinations 
                WHERE track = %s
            """, (track_id,))
            matchups = cursor.fetchall()
            matchup_dict = {hth_id: (driver1, driver2) for hth_id, driver1, driver2 in matchups}
            
            # Calculate points for each prediction
            for user_id, headtohead_id, driver_selected, poule in predictions:
                points = 15  # Default to 15 points (incorrect prediction)
                
                # Get the drivers in this matchup
                driver1, driver2 = matchup_dict.get(headtohead_id, (None, None))
                
                if driver1 and driver2:
                    # Get positions of both drivers
                    pos1 = driver_positions.get(driver1, 999)
                    pos2 = driver_positions.get(driver2, 999)
                    
                    # Determine the winner (lower position is better)
                    winner = driver1 if pos1 > pos2 else driver2
                    
                    # Award 0 points if prediction was correct
                    # driver_selected is True for driver1, False for driver2
                    if (driver_selected and winner == driver1) or (not driver_selected and winner == driver2):
                        points = 0
                
                # Update points in the database
                cursor.execute("""
                    UPDATE headtoheadprediction
                    SET points = %s
                    WHERE user_id = %s AND headtohead_id = %s AND track = %s AND poule = %s
                """, (points, user_id, headtohead_id, track_id, poule))
    
    def calculate_bonus_points(self, track_id):
        """Calculate points for bonus predictions.
        
        Args:
            track_id: The track ID.
        """
        with get_db_cursor(commit=True) as cursor:
            # Get all bonus predictions for this track
            cursor.execute("""
                SELECT user_id, fastestlap, dnf, dod, poule
                FROM bonusprediction
                WHERE track = %s
            """, (track_id,))
            predictions = cursor.fetchall()
            
            # Get bonus results for this track
            cursor.execute("SELECT fl, dod FROM bonusresults WHERE track = %s", (track_id,))
            bonus_data = cursor.fetchone()
            
            if not bonus_data:
                return
            
            fastest_lap, driver_of_day = bonus_data
            
            # Get DNF drivers
            cursor.execute("""
                SELECT driver_id
                FROM raceresults
                WHERE track_id = %s AND dnf = true
            """, (track_id,))
            dnf_drivers = cursor.fetchall()
            
            # Calculate points for each prediction
            for user_id, pred_fl, pred_dnf, pred_dod, poule in predictions:
                fl_points = 15 if str(pred_fl) == str(fastest_lap) else 0
                
                # Special handling for DNF prediction
                if not dnf_drivers and pred_dnf is None:
                    # Correctly predicted no DNFs
                    dnf_points = 15
                elif dnf_drivers and pred_dnf and str(pred_dnf) in [str(d[0]) for d in dnf_drivers]:
                    # Correctly predicted a specific driver DNF
                    dnf_points = 15
                else:
                    # Incorrect prediction
                    dnf_points = 0
                
                dod_points = 15 if str(pred_dod) == str(driver_of_day) else 0
                
                # Update points in the database
                cursor.execute("""
                    UPDATE bonusprediction
                    SET flpoints = %s, dnfpoints = %s, dodpoints = %s
                    WHERE user_id = %s AND track = %s AND poule = %s
                """, (fl_points, dnf_points, dod_points, user_id, track_id, poule))
    
    def _calculate_driver_points(self, driver_id, predicted_position, actual_positions):
        """Calculate points for a driver prediction.
        
        Args:
            driver_id: The driver ID.
            predicted_position: The predicted position (1-based).
            actual_positions: A dictionary mapping driver IDs to actual positions.
            
        Returns:
            int: The points earned for this prediction.
        """
        if not driver_id:
            return 0
        
        # Get the actual position of the driver
        actual_position = actual_positions.get(driver_id, 999)
        
        # Calculate points based on accuracy (difference between predicted and actual position)
        position_difference = abs(actual_position - predicted_position)
        
        # F1 points system based on accuracy
        f1_points = {
            0: 25,  # Exact match
            1: 18,  # Off by 1 position
            2: 15,  # Off by 2 positions
            3: 12,  # Off by 3 positions
            4: 10,  # Off by 4 positions
            5: 8,   # Off by 5 positions
            6: 6,   # Off by 6 positions
            7: 4,   # Off by 7 positions
            8: 2,   # Off by 8 positions
            9: 1    # Off by 9 positions
        }
        
        # Return points based on accuracy, or 0 if off by more than 9 positions
        return f1_points.get(position_difference, 0) 