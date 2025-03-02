from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.models.driver import Driver
from app.models.track import Track
from app.models.team import Team
from app.models.result import Result, QualifyingResult, RaceResult
from app.services.points_calculator import PointsCalculator
from app.services.pdf_scraper import get_available_races, get_final_race_results, get_final_quali_results
from app.models.poule import Poule
from app.database.connection import get_db_cursor
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Check if the user is an admin."""
    if not session.get('is_admin', False):
        return redirect(url_for('poule.dashboard'))

@admin_bp.route('/')
def dashboard():
    """Render the admin dashboard."""
    return render_template('admin.html')

@admin_bp.route('/users')
def manage_users():
    """Render the user management page."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT user_id, username, is_admin FROM users ORDER BY username")
        users = cursor.fetchall()
    return render_template('manageUsers.html', users=users)

@admin_bp.route('/users/toggle_admin/<int:user_id>', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin status for a user."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # First check if this is the last admin
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true")
            admin_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
            current_status = cursor.fetchone()[0]
            
            # Prevent removing admin status if this is the last admin
            if admin_count == 1 and current_status:
                flash('Cannot remove admin status from the last admin user.', 'error')
                return redirect(url_for('admin.manage_users'))
            
            # Toggle the admin status
            cursor.execute(
                "UPDATE users SET is_admin = NOT is_admin WHERE user_id = %s",
                (user_id,)
            )
            flash('User admin status updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating user admin status: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if this is an admin user
            cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
            is_admin = cursor.fetchone()[0]
            
            if is_admin:
                # Count number of admins
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true")
                admin_count = cursor.fetchone()[0]
                
                if admin_count == 1:
                    flash('Cannot delete the last admin user.', 'error')
                    return redirect(url_for('admin.manage_users'))
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/add_data')
def add_data():
    """Render the add data page."""
    teams = Team.get_all()
    drivers = Driver.get_all()
    tracks = Track.get_all()
    poules = Poule.get_all()
    available_years = Track.get_available_years()
    available_poule_years = Poule.get_available_years()
    current_year = datetime.now().year
    selected_year = request.args.get('year', type=int)
    selected_poule_year = request.args.get('poule_year', type=int)
    
    if selected_year:
        tracks = Track.get_all(year=selected_year)
    if selected_poule_year:
        poules = Poule.get_all(year=selected_poule_year)
    
    # Get the most recent track's combinations
    with get_db_cursor() as cursor:
        cursor.execute("""
            WITH RankedTracks AS (
                SELECT id, track_name,
                       ROW_NUMBER() OVER (ORDER BY track_race_date DESC) as rn
                FROM track
            )
            SELECT 
                hc.id,
                hc.driver1_id,
                hc.driver2_id,
                d1.driver_name as driver1_name,
                d2.driver_name as driver2_name,
                t.track_name
            FROM RankedTracks rt
            JOIN headtohead_combinations hc ON rt.id = hc.track
            JOIN driver d1 ON hc.driver1_id = d1.driver_id
            JOIN driver d2 ON hc.driver2_id = d2.driver_id
            JOIN track t ON hc.track = t.id
            WHERE rt.rn = 1
            ORDER BY hc.id
        """)
        previous_combinations = []
        for row in cursor.fetchall():
            previous_combinations.append({
                'id': row[0],
                'driver1_id': row[1],
                'driver2_id': row[2],
                'driver1_name': row[3],
                'driver2_name': row[4],
                'track_name': row[5]
            })
        
        # Get all combinations for display
        cursor.execute("""
            SELECT 
                hc.id,
                d1.driver_name as driver1_name,
                d2.driver_name as driver2_name,
                t.track_name as track_name,
                EXTRACT(YEAR FROM t.track_race_date) as year
            FROM headtohead_combinations hc
            JOIN driver d1 ON hc.driver1_id = d1.driver_id
            JOIN driver d2 ON hc.driver2_id = d2.driver_id
            JOIN track t ON hc.track = t.id
            ORDER BY year DESC, t.track_name, d1.driver_name
        """)
        headtohead_combinations = []
        for row in cursor.fetchall():
            headtohead_combinations.append({
                'id': row[0],
                'driver1_name': row[1],
                'driver2_name': row[2],
                'track_name': row[3],
                'year': row[4]
            })
    
    return render_template(
        'addData.html',
        teams=teams,
        drivers=drivers,
        tracks=tracks,
        poules=poules,
        available_years=available_years,
        available_poule_years=available_poule_years,
        selected_year=selected_year,
        selected_poule_year=selected_poule_year,
        current_year=current_year,
        headtohead_combinations=headtohead_combinations,
        previous_combinations=previous_combinations
    )

@admin_bp.route('/add_driver', methods=['POST'])
def add_driver():
    """Add a new driver."""
    driver_name = request.form.get('driver_name')
    team_name = request.form.get('driver_team')  # Form field name stays the same for backward compatibility
    
    Result.insert_driver(driver_name, team_name)
    
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/add_track', methods=['POST'])
def add_track():
    """Add a new track with head-to-head combinations."""
    track_name = request.form.get('track_name')
    quali_date = request.form.get('quali_date')
    race_date = request.form.get('race_date')
    
    # Get driver combinations
    driver1_ids = request.form.getlist('driver1[]')
    driver2_ids = request.form.getlist('driver2[]')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Insert track first
            cursor.execute("""
                INSERT INTO track (track_name, track_quali_date, track_race_date)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (track_name, quali_date, race_date))
            track_id = cursor.fetchone()[0]
            
            # Insert head-to-head combinations
            for d1_id, d2_id in zip(driver1_ids, driver2_ids):
                if d1_id and d2_id and d1_id != d2_id:  # Only insert if both drivers are selected and different
                    # Check if this combination already exists
                    cursor.execute("""
                        SELECT id FROM headtohead_combinations 
                        WHERE (driver1_id = %s AND driver2_id = %s AND track = %s)
                        OR (driver1_id = %s AND driver2_id = %s AND track = %s)
                    """, (d1_id, d2_id, track_id, d2_id, d1_id, track_id))
                    
                    if not cursor.fetchone():  # Only insert if combination doesn't exist
                        cursor.execute("""
                            INSERT INTO headtohead_combinations (driver1_id, driver2_id, track)
                            VALUES (%s, %s, %s)
                        """, (d1_id, d2_id, track_id))
            
        flash('Track and head-to-head combinations added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding track and combinations: {str(e)}', 'error')
    
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/add_team', methods=['POST'])
def add_team():
    """Add a new team."""
    team_name = request.form.get('team_name')
    Team.create(team_name)
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/add_poule', methods=['POST'])
def add_poule():
    """Add a new poule."""
    poule_name = request.form.get('poule_name')
    poule_year = request.form.get('poule_year', type=int)
    
    if not poule_name or not poule_year:
        flash('Please provide both poule name and year.', 'error')
        return redirect(url_for('admin.add_data'))
    
    # Check if poule with same name exists
    existing_poule = Poule.get_by_name(poule_name)
    if existing_poule:
        flash('A poule with this name already exists.', 'error')
        return redirect(url_for('admin.add_data'))
    
    poule = Poule(name=poule_name, year=poule_year)
    poule.create()
    flash('Poule added successfully.', 'success')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/results', methods=['GET', 'POST'])
def results():
    """Render the results page."""
    # Get race names from FIA website for the classification dropdown
    selected_year = request.args.get('year', type=int) or request.form.get('year', type=int) or 2024
    classified_tracks = get_available_races(selected_year)
    
    # Get active and inactive drivers separately
    active_drivers = Driver.get_all(active_only=True)
    inactive_drivers = Driver.get_all(active_only=False, exclude_active=True)
    
    # Combine drivers with active drivers first
    drivers = active_drivers + inactive_drivers
    
    tracks = Track.get_all()
    available_years = Track.get_available_years()
    
    track_link = None
    final_results = []
    dnfs = []
    fastest_lap = ''
    
    if request.method == 'POST':
        load_track = request.form.get('classified_tracks')
        data_type = request.form.get('type')  # Get the type of data (race or qualifying)
        year = request.form.get('year', type=int) or 2024
        
        # Load data based on the type
        if data_type == 'qualifying':
            # Fetch qualifying data from PDF
            results = get_final_quali_results(load_track, year)
            track_link = f"https://www.formula1.com/en/results.html/{year}/races/{load_track.replace(' ', '-')}/qualifying.html"
        else:
            # Fetch race data from PDF
            results = get_final_race_results(load_track, year)
            track_link = f"https://www.formula1.com/en/results.html/{year}/races/{load_track.replace(' ', '-')}/race-result.html"
        
        # Extract individual components from the results
        final_results = results[0]  # List of final results (driver positions)
        dnfs = results[1]           # List of drivers who did not finish
        fastest_lap = results[2]    # Fastest lap driver name
        
        # Reorder drivers based on results
        if final_results:
            # Create a mapping of driver names to their full driver data
            driver_map = {driver[1]: driver for driver in drivers}
            
            # Create ordered list of drivers based on results, followed by remaining drivers
            ordered_drivers = []
            
            # First add drivers from results in order
            for driver_name in final_results:
                if driver_name in driver_map:
                    ordered_drivers.append(driver_map[driver_name])
                    del driver_map[driver_name]  # Remove from map to track remaining drivers
            
            # Then add any remaining drivers that weren't in the results
            ordered_drivers.extend(driver_map.values())
            
            # Update the drivers list with the new order
            drivers = ordered_drivers
    
    return render_template(
        "addResults.html", 
        drivers=drivers, 
        tracks=tracks, 
        final_results=final_results, 
        dnfs=dnfs, 
        fastest_lap=fastest_lap, 
        classified_tracks=classified_tracks, 
        track_link=track_link,
        available_years=available_years,
        selected_year=selected_year
    )

@admin_bp.route('/get_classified_tracks')
def get_classified_tracks():
    """Get classified tracks for a specific year."""
    year = request.args.get('year', type=int) or 2024
    tracks = get_available_races(year)
    return jsonify({'tracks': tracks})

@admin_bp.route('/submit_results', methods=['POST'])
def submit_results():
    """Submit race or qualifying results."""
    track_id = request.form.get('track')
    racesession = request.form.get('racesession')
    driver_positions = request.form.getlist('driver_positions[]')
    driver_ids = request.form.getlist('driver_ids[]')
    fastest_lap = request.form.get('fl')
    driver_of_day = request.form.get('dod')
    
    # Get DNF status
    driver_dnfs = request.form.getlist('driver_dnf[]')
    dnfs = []
    for driver_id in driver_ids:
        if driver_id in driver_dnfs:
            dnfs.append(driver_id)
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # First, delete any existing results for this track and session
            cursor.execute(f"DELETE FROM {racesession} WHERE track_id = %s", (track_id,))
            
            # Insert new results
            for position, driver_id in enumerate(driver_ids, 1):
                dnf = driver_id in dnfs
                cursor.execute(f"""
                    INSERT INTO {racesession} (track_id, position, driver_id, dnf)
                    VALUES (%s, %s, %s, %s)
                """, (track_id, position, driver_id, dnf))
            
            # Handle bonus results (fastest lap and driver of the day)
            if racesession == 'raceresults':  # Only update bonus results for race session
                # First, delete any existing bonus results for this track
                cursor.execute("DELETE FROM bonusresults WHERE track = %s", (track_id,))
                
                # Insert new bonus results
                cursor.execute("""
                    INSERT INTO bonusresults (fl, dod, track)
                    VALUES (%s, %s, %s)
                """, (fastest_lap, driver_of_day, track_id))
        
        flash('Results submitted successfully.', 'success')
    except Exception as e:
        flash(f'Error submitting results: {str(e)}', 'error')
    
    return redirect(url_for('admin.results'))

@admin_bp.route('/calc_points', methods=['GET', 'POST'])
def calc_points():
    """Calculate points for predictions."""
    # Get available years and selected year
    available_years = Track.get_available_years()
    selected_year = request.args.get('year', type=int) or datetime.now().year
    
    # Get tracks filtered by year
    tracks = Track.get_all(year=selected_year)
    raceresults = []
    qualiresults = []
    
    for track in tracks:
        raceresults.append(RaceResult.get_result(track[0]))
        qualiresults.append(QualifyingResult.get_result(track[0]))
    
    if request.method == 'POST':
        track_id = request.form.get('track')
        racesession = request.form.get('racesession')
        
        try:
            calculator = PointsCalculator()
            if racesession == "qualiresults":
                calculator.calculate_qualifying_points(track_id)
            else:
                calculator.calculate_race_points(track_id)
                calculator.calculate_head_to_head(track_id)
                calculator.calculate_bonus_points(track_id)
        except Exception as e:
            print(f"Error calculating points: {e}")
    
    return render_template(
        "calcPoints.html", 
        tracks=tracks, 
        qualiresults=qualiresults, 
        raceresults=raceresults,
        available_years=available_years,
        selected_year=selected_year
    )

@admin_bp.route('/copy_predictions', methods=['POST'])
def copy_predictions():
    """Copy missing predictions from previous track to target track."""
    target_track_id = request.form.get('target_track')
    
    if not target_track_id:
        flash('Please select a target track.', 'error')
        return redirect(url_for('admin.calc_points'))
    
    with get_db_cursor(commit=True) as cursor:
        # Get the previous track ID
        cursor.execute("""
            SELECT id FROM track 
            WHERE track_race_date < (SELECT track_race_date FROM track WHERE id = %s)
            ORDER BY track_race_date DESC 
            LIMIT 1
        """, (target_track_id,))
        prev_track = cursor.fetchone()
        
        if not prev_track:
            flash('No previous track found.', 'error')
            return redirect(url_for('admin.calc_points'))
        
        prev_track_id = prev_track[0]
        
        # Get all user-poule combinations
        cursor.execute("SELECT user_id, poule_id FROM user_poule")
        user_poule_combinations = cursor.fetchall()
        
        # Initialize counters for each prediction type
        copied_quali = 0
        copied_race = 0
        copied_bonus = 0
        copied_h2h = 0
        updated_quali = 0
        updated_race = 0
        updated_bonus = 0
        updated_h2h = 0
        
        for user_id, poule_id in user_poule_combinations:
            # Handle qualifying predictions
            # First try to insert completely missing predictions
            cursor.execute("""
                WITH missing_predictions AS (
                    SELECT t.user_id, t.driver1_id, t.driver2_id, t.driver3_id, t.poule
                    FROM top3_quali t
                    WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM top3_quali 
                        WHERE user_id = %s AND track = %s AND poule = %s
                    )
                )
                INSERT INTO top3_quali (user_id, track, driver1_id, driver2_id, driver3_id, poule)
                SELECT user_id, %s, driver1_id, driver2_id, driver3_id, poule
                FROM missing_predictions
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id,
                  target_track_id))
            copied_quali += len(cursor.fetchall())
            
            # Then update partial predictions
            cursor.execute("""
                WITH prev_predictions AS (
                    SELECT driver1_id, driver2_id, driver3_id
                    FROM top3_quali
                    WHERE user_id = %s AND track = %s AND poule = %s
                )
                UPDATE top3_quali t
                SET 
                    driver1_id = COALESCE(t.driver1_id, p.driver1_id),
                    driver2_id = COALESCE(t.driver2_id, p.driver2_id),
                    driver3_id = COALESCE(t.driver3_id, p.driver3_id)
                FROM prev_predictions p
                WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                AND (t.driver1_id IS NULL OR t.driver2_id IS NULL OR t.driver3_id IS NULL)
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id))
            updated_quali += len(cursor.fetchall())
            
            # Handle race predictions
            # First try to insert completely missing predictions
            cursor.execute("""
                WITH missing_predictions AS (
                    SELECT t.user_id, t.driver1_id, t.driver2_id, t.driver3_id, t.driver4_id, t.driver5_id, t.poule
                    FROM top5_race t
                    WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM top5_race 
                        WHERE user_id = %s AND track = %s AND poule = %s
                    )
                )
                INSERT INTO top5_race (user_id, track, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, poule)
                SELECT user_id, %s, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, poule
                FROM missing_predictions
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id,
                  target_track_id))
            copied_race += len(cursor.fetchall())
            
            # Then update partial predictions
            cursor.execute("""
                WITH prev_predictions AS (
                    SELECT driver1_id, driver2_id, driver3_id, driver4_id, driver5_id
                    FROM top5_race
                    WHERE user_id = %s AND track = %s AND poule = %s
                )
                UPDATE top5_race t
                SET 
                    driver1_id = COALESCE(t.driver1_id, p.driver1_id),
                    driver2_id = COALESCE(t.driver2_id, p.driver2_id),
                    driver3_id = COALESCE(t.driver3_id, p.driver3_id),
                    driver4_id = COALESCE(t.driver4_id, p.driver4_id),
                    driver5_id = COALESCE(t.driver5_id, p.driver5_id)
                FROM prev_predictions p
                WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                AND (t.driver1_id IS NULL OR t.driver2_id IS NULL OR t.driver3_id IS NULL 
                     OR t.driver4_id IS NULL OR t.driver5_id IS NULL)
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id))
            updated_race += len(cursor.fetchall())
            
            # Handle bonus predictions
            # First try to insert completely missing predictions
            cursor.execute("""
                WITH missing_predictions AS (
                    SELECT t.user_id, t.fastestlap, t.dnf, t.dod, t.poule
                    FROM bonusprediction t
                    WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM bonusprediction 
                        WHERE user_id = %s AND track = %s AND poule = %s
                    )
                )
                INSERT INTO bonusprediction (user_id, track, fastestlap, dnf, dod, poule)
                SELECT user_id, %s, fastestlap, dnf, dod, poule
                FROM missing_predictions
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id,
                  target_track_id))
            copied_bonus += len(cursor.fetchall())
            
            # Then update partial predictions
            cursor.execute("""
                WITH prev_predictions AS (
                    SELECT fastestlap, dnf, dod
                    FROM bonusprediction
                    WHERE user_id = %s AND track = %s AND poule = %s
                )
                UPDATE bonusprediction t
                SET 
                    fastestlap = COALESCE(t.fastestlap, p.fastestlap),
                    dnf = COALESCE(t.dnf, p.dnf),
                    dod = COALESCE(t.dod, p.dod)
                FROM prev_predictions p
                WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                AND (t.fastestlap IS NULL OR t.dnf IS NULL OR t.dod IS NULL)
                RETURNING 1
            """, (user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id))
            updated_bonus += len(cursor.fetchall())
            
            # Handle head-to-head predictions
            # First get the ordered combinations for both tracks
            cursor.execute("""
                WITH prev_track_combinations AS (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY id) as rn
                    FROM headtohead_combinations 
                    WHERE track = %s
                ),
                current_track_combinations AS (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY id) as rn
                    FROM headtohead_combinations 
                    WHERE track = %s
                ),
                prev_predictions AS (
                    SELECT h.rn, hp.driverselected
                    FROM headtoheadprediction hp
                    JOIN prev_track_combinations h ON hp.headtohead_id = h.id
                    WHERE hp.user_id = %s AND hp.track = %s AND hp.poule = %s
                    ORDER BY h.rn
                )
                INSERT INTO headtoheadprediction (user_id, track, headtohead_id, driverselected, poule)
                SELECT 
                    %s as user_id,
                    %s as track,
                    c.id as headtohead_id,
                    p.driverselected,
                    %s as poule
                FROM current_track_combinations c
                JOIN prev_predictions p ON c.rn = p.rn
                WHERE NOT EXISTS (
                    SELECT 1 FROM headtoheadprediction hp
                    WHERE hp.user_id = %s AND hp.track = %s AND hp.poule = %s
                    AND hp.headtohead_id = c.id
                )
                RETURNING 1
            """, (prev_track_id, target_track_id,
                  user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id,
                  user_id, target_track_id, poule_id))
            copied_h2h += len(cursor.fetchall())
            
            # Then update any partial predictions by position
            cursor.execute("""
                WITH prev_track_combinations AS (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY id) as rn
                    FROM headtohead_combinations 
                    WHERE track = %s
                ),
                current_track_combinations AS (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY id) as rn
                    FROM headtohead_combinations 
                    WHERE track = %s
                ),
                prev_predictions AS (
                    SELECT h.rn, hp.driverselected
                    FROM headtoheadprediction hp
                    JOIN prev_track_combinations h ON hp.headtohead_id = h.id
                    WHERE hp.user_id = %s AND hp.track = %s AND hp.poule = %s
                    ORDER BY h.rn
                )
                UPDATE headtoheadprediction t
                SET driverselected = p.driverselected
                FROM current_track_combinations c
                JOIN prev_predictions p ON c.rn = p.rn
                WHERE t.user_id = %s AND t.track = %s AND t.poule = %s
                AND t.headtohead_id = c.id
                AND t.driverselected IS NULL
                RETURNING 1
            """, (prev_track_id, target_track_id,
                  user_id, prev_track_id, poule_id,
                  user_id, target_track_id, poule_id))
            updated_h2h += len(cursor.fetchall())
    
    # Create a detailed message about what was copied and updated
    messages = []
    if copied_quali > 0:
        messages.append(f"Copied {copied_quali} new qualifying predictions")
    if updated_quali > 0:
        messages.append(f"Updated {updated_quali} partial qualifying predictions")
    if copied_race > 0:
        messages.append(f"Copied {copied_race} new race predictions")
    if updated_race > 0:
        messages.append(f"Updated {updated_race} partial race predictions")
    if copied_bonus > 0:
        messages.append(f"Copied {copied_bonus} new bonus predictions")
    if updated_bonus > 0:
        messages.append(f"Updated {updated_bonus} partial bonus predictions")
    if copied_h2h > 0:
        messages.append(f"Copied {copied_h2h} new head-to-head predictions")
    if updated_h2h > 0:
        messages.append(f"Updated {updated_h2h} partial head-to-head predictions")
    
    if messages:
        flash('Successfully processed predictions: ' + ', '.join(messages) + '.', 'success')
    else:
        flash('No predictions needed to be copied or updated.', 'info')
    
    return redirect(url_for('admin.calc_points'))

@admin_bp.route('/edit_team/<int:team_id>', methods=['POST'])
def edit_team(team_id):
    """Edit a team's name."""
    team_name = request.form.get('team_name')
    try:
        Team.update(team_id, team_name)
        flash('Team updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating team: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    """Delete a team."""
    try:
        Team.delete(team_id)
        flash('Team deleted successfully', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting team: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/edit_driver/<int:driver_id>', methods=['POST'])
def edit_driver(driver_id):
    """Edit a driver."""
    driver_name = request.form.get('driver_name')
    team_name = request.form.get('driver_team')
    try:
        Driver.update(driver_id, driver_name, team_name)
        flash('Driver updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating driver: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/delete_driver/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    """Delete a driver."""
    try:
        Driver.delete(driver_id)
        flash('Driver deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting driver: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/edit_track/<int:track_id>', methods=['POST'])
def edit_track(track_id):
    """Edit a track."""
    track_name = request.form.get('track_name')
    quali_date = request.form.get('quali_date')
    race_date = request.form.get('race_date')
    try:
        Track.update(track_id, track_name, quali_date, race_date)
        flash('Track updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating track: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/delete_track/<int:track_id>', methods=['POST'])
def delete_track(track_id):
    """Delete a track."""
    try:
        Track.delete(track_id)
        flash('Track deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting track: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/edit_poule/<int:poule_id>', methods=['POST'])
def edit_poule(poule_id):
    """Edit an existing poule."""
    poule = Poule.get_by_id(poule_id)
    if not poule:
        flash('Poule not found.', 'error')
        return redirect(url_for('admin.add_data'))
    
    poule_name = request.form.get('poule_name')
    poule_year = request.form.get('poule_year', type=int)
    
    if not poule_name or not poule_year:
        flash('Please provide both poule name and year.', 'error')
        return redirect(url_for('admin.add_data'))
    
    # Check if another poule with same name exists
    existing_poule = Poule.get_by_name(poule_name)
    if existing_poule and existing_poule.poule_id != poule_id:
        flash('Another poule with this name already exists.', 'error')
        return redirect(url_for('admin.add_data'))
    
    poule.poule_name = poule_name
    poule.year = poule_year
    poule.update()
    flash('Poule updated successfully.', 'success')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/delete_poule/<int:poule_id>', methods=['POST'])
def delete_poule(poule_id):
    """Delete a poule."""
    poule = Poule.get_by_id(poule_id)
    if not poule:
        flash('Poule not found.', 'error')
        return redirect(url_for('admin.add_data'))
    
    poule.delete()
    flash('Poule deleted successfully.', 'success')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/delete_headtohead_combination/<int:combo_id>', methods=['POST'])
def delete_headtohead_combination(combo_id):
    """Delete a head-to-head combination."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM headtohead_combinations WHERE id = %s", (combo_id,))
        flash('Head-to-head combination deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting head-to-head combination: {str(e)}', 'error')
    return redirect(url_for('admin.add_data'))

@admin_bp.route('/update_driver_status/<int:driver_id>', methods=['POST'])
def update_driver_status(driver_id):
    """Update a driver's active status."""
    try:
        data = request.get_json()
        active = data.get('active', False)
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE driver 
                SET active = %s 
                WHERE driver_id = %s
            """, (active, driver_id))
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 