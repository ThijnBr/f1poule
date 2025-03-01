from flask import Blueprint, render_template, request, redirect, url_for, session
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
    users = poule.get_users()
    user_id = session.get('user_id')
    return render_template('poule.html', poule=poule_id, users=users, user_id=user_id) 