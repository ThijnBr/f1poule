from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.models.poule import Poule
from app.models.track import Track
from datetime import datetime
from app.database.connection import get_db_cursor
from collections import namedtuple

poule_bp = Blueprint('poule', __name__, url_prefix='/poule')

# Define a namedtuple for predictions
Prediction = namedtuple('Prediction', ['track_name', 'date', 'type', 'status', 'track_id', 'user_id', 'poule_name', 'poule_id'])

@poule_bp.before_request
def check_auth():
    """Check if the user is authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))

@poule_bp.route('/dashboard')
def dashboard():
    """Dashboard view showing active and previous poules."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    # Get all poules for the user
    poules = Poule.get_poules_for_user(user_id)
    current_year = Poule.get_current_year()
    
    # Split poules into active and previous
    active_poules = []
    previous_poules = []
    
    for poule in poules:
        points = poule.get_user_points(user_id)
        rank = poule.get_user_rank(user_id)
        next_race = Track.get_next_race(poule.year)
        # Format as tuple: (id, name, year, points, rank, next_race)
        poule_data = (poule.id, poule.name, poule.year, points, rank, next_race)
        
        if poule.year == current_year:
            active_poules.append(poule_data)
        else:
            previous_poules.append(poule_data)
    
    # Get recent predictions for all active poules
    recent_predictions = []
    if active_poules:
        with get_db_cursor() as cursor:
            # Get qualifying and race predictions for the last track of each poule
            cursor.execute(
                """
                WITH UserPoules AS (
                    -- Get all poules where user has made any predictions
                    SELECT DISTINCT poule
                    FROM (
                        SELECT poule FROM top3_quali WHERE user_id = %s
                        UNION
                        SELECT poule FROM top5_race WHERE user_id = %s
                    ) all_poules
                ),
                LastTracks AS (
                    -- Get the most recent track for each poule
                    SELECT DISTINCT ON (p.poule_id) 
                        t.id, t.track_name, t.track_quali_date, t.track_race_date, p.poule_id, p.poule_name
                    FROM track t
                    CROSS JOIN UserPoules up
                    JOIN poules p ON p.poule_id = up.poule
                    WHERE t.track_race_date <= CURRENT_TIMESTAMP
                        AND p.year = EXTRACT(YEAR FROM CURRENT_DATE)
                    ORDER BY p.poule_id, t.track_race_date DESC
                )
                SELECT t.track_name, t.track_quali_date as event_date, 'Qualifying' as type,
                       CASE 
                           WHEN EXISTS (SELECT 1 FROM qualiresults WHERE track_id = t.id) THEN 'points'
                           ELSE 'pending'
                       END as status,
                       t.id as track_id,
                       %s as user_id,
                       lt.poule_name,
                       lt.poule_id
                FROM LastTracks lt
                JOIN track t ON t.id = lt.id
                JOIN top3_quali p ON p.track = t.id AND p.poule = lt.poule_id
                WHERE p.user_id = %s
                UNION ALL
                SELECT t.track_name, t.track_race_date as event_date, 'Race' as type,
                       CASE 
                           WHEN EXISTS (SELECT 1 FROM raceresults WHERE track_id = t.id) THEN 'points'
                           ELSE 'pending'
                       END as status,
                       t.id as track_id,
                       %s as user_id,
                       lt.poule_name,
                       lt.poule_id
                FROM LastTracks lt
                JOIN track t ON t.id = lt.id
                JOIN top5_race p ON p.track = t.id AND p.poule = lt.poule_id
                WHERE p.user_id = %s
                ORDER BY event_date DESC
                """,
                (user_id, user_id, user_id, user_id, user_id, user_id)
            )
            # Convert tuples to namedtuples
            recent_predictions = [Prediction(*row) for row in cursor.fetchall()]
    
    return render_template(
        'dashboard.html',
        user=user,
        active_poules=active_poules,
        previous_poules=previous_poules,
        recent_predictions=recent_predictions
    )

@poule_bp.route('/join', methods=['POST'])
def join_poule():
    """Join a poule."""
    poule_name = request.form.get('poulename')
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if user.join_poule(poule_name):
        return redirect(url_for('poule.dashboard'))
    else:
        # Handle error (poule not found)
        return redirect(url_for('poule.dashboard'))

@poule_bp.route('/<int:poule_id>')
def view_poule(poule_id):
    """View a specific poule."""
    session['poule'] = poule_id
    poule = Poule.get_by_id(poule_id)
    user_id = session.get('user_id')
    track_id = request.args.get('track_id', type=int)

    # Get all tracks for this poule's year
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, track_name 
            FROM track 
            WHERE EXTRACT(YEAR FROM track_race_date) = %s
            ORDER BY track_race_date DESC
        """, (poule.year,))
        tracks = cursor.fetchall()

    # Get users with their points
    if track_id:
        # Get points for specific track
        with get_db_cursor() as cursor:
            cursor.execute("""
                WITH user_points AS (
                    -- Qualifying points
                    SELECT u.user_id, u.username,
                           COALESCE(SUM(q.driver1points + q.driver2points + q.driver3points), 0) as quali_points
                    FROM users u
                    JOIN user_poule up ON u.user_id = up.user_id
                    LEFT JOIN top3_quali q ON u.user_id = q.user_id 
                        AND q.track = %s AND q.poule = %s
                    WHERE up.poule_id = %s
                    GROUP BY u.user_id, u.username
                ),
                race_points AS (
                    -- Race points
                    SELECT u.user_id,
                           COALESCE(SUM(r.driver1points + r.driver2points + r.driver3points + 
                                      r.driver4points + r.driver5points), 0) as race_points
                    FROM users u
                    JOIN user_poule up ON u.user_id = up.user_id
                    LEFT JOIN top5_race r ON u.user_id = r.user_id 
                        AND r.track = %s AND r.poule = %s
                    WHERE up.poule_id = %s
                    GROUP BY u.user_id
                ),
                bonus_points AS (
                    -- Bonus points
                    SELECT u.user_id,
                           COALESCE(SUM(b.flpoints + b.dnfpoints + b.dodpoints), 0) as bonus_points
                    FROM users u
                    JOIN user_poule up ON u.user_id = up.user_id
                    LEFT JOIN bonusprediction b ON u.user_id = b.user_id 
                        AND b.track = %s AND b.poule = %s
                    WHERE up.poule_id = %s
                    GROUP BY u.user_id
                )
                SELECT up.username,
                       (up.quali_points + COALESCE(rp.race_points, 0) + COALESCE(bp.bonus_points, 0)) as total_points,
                       up.user_id
                FROM user_points up
                LEFT JOIN race_points rp ON up.user_id = rp.user_id
                LEFT JOIN bonus_points bp ON up.user_id = bp.user_id
                ORDER BY total_points DESC
            """, (track_id, poule_id, poule_id, track_id, poule_id, poule_id, track_id, poule_id, poule_id))
            users = cursor.fetchall()
    else:
        # Get total points for all tracks
        users = poule.get_users()

    return render_template(
        'poule.html', 
        poule=poule_id, 
        users=users, 
        user_id=user_id,
        tracks=tracks,
        selected_track=track_id
    )

@poule_bp.route('/advanced/<int:poule_id>')
def advanced_info(poule_id):
    """Show advanced information and statistics for a poule."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.index'))
    
    poule = Poule.get_by_id(poule_id)
    if not poule:
        flash('Poule not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Get all users in the poule with their points
    users = poule.get_users()
    
    # Get driver points analysis
    with get_db_cursor() as cursor:
        # Analyze qualifying predictions
        cursor.execute("""
            WITH driver_quali_points AS (
                SELECT 
                    d.driver_id,
                    d.driver_name,
                    t.team_name,
                    COUNT(*) * 25 as total_possible,
                    SUM(
                        CASE 
                            WHEN p.driver1_id = d.driver_id THEN p.driver1points
                            WHEN p.driver2_id = d.driver_id THEN p.driver2points
                            WHEN p.driver3_id = d.driver_id THEN p.driver3points
                        END
                    ) as points_earned
                FROM driver d
                JOIN team t ON d.team_id = t.team_id
                JOIN top3_quali p ON (
                    d.driver_id IN (p.driver1_id, p.driver2_id, p.driver3_id)
                )
                WHERE p.user_id = %s AND p.poule = %s
                GROUP BY d.driver_id, d.driver_name, t.team_name
                HAVING COUNT(*) > 0
            )
            SELECT 
                driver_name,
                team_name,
                points_earned,
                total_possible,
                ROUND((points_earned::numeric / total_possible::numeric) * 100, 1) as success_rate
            FROM driver_quali_points
            ORDER BY (points_earned::numeric / total_possible::numeric) DESC
        """, (user_id, poule_id))
        quali_stats = cursor.fetchall()

        # Analyze race predictions
        cursor.execute("""
            WITH driver_race_points AS (
                SELECT 
                    d.driver_id,
                    d.driver_name,
                    t.team_name,
                    COUNT(*) * 25 as total_possible,
                    SUM(
                        CASE 
                            WHEN p.driver1_id = d.driver_id THEN p.driver1points
                            WHEN p.driver2_id = d.driver_id THEN p.driver2points
                            WHEN p.driver3_id = d.driver_id THEN p.driver3points
                            WHEN p.driver4_id = d.driver_id THEN p.driver4points
                            WHEN p.driver5_id = d.driver_id THEN p.driver5points
                        END
                    ) as points_earned
                FROM driver d
                JOIN team t ON d.team_id = t.team_id
                JOIN top5_race p ON (
                    d.driver_id IN (p.driver1_id, p.driver2_id, p.driver3_id, p.driver4_id, p.driver5_id)
                )
                WHERE p.user_id = %s AND p.poule = %s
                GROUP BY d.driver_id, d.driver_name, t.team_name
                HAVING COUNT(*) > 0
            )
            SELECT 
                driver_name,
                team_name,
                points_earned,
                total_possible,
                ROUND((points_earned::numeric / total_possible::numeric) * 100, 1) as success_rate
            FROM driver_race_points
            ORDER BY (points_earned::numeric / total_possible::numeric) DESC
        """, (user_id, poule_id))
        race_stats = cursor.fetchall()
    
    return render_template(
        'advanced_info.html',
        poule=poule,
        users=users,
        user_id=user_id,
        quali_stats=quali_stats,
        race_stats=race_stats
    ) 