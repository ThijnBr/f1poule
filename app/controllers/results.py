from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models.prediction import Prediction, QualifyingPrediction, RacePrediction, BonusPrediction
from app.database.connection import get_db_cursor
from app.models.user import User

results_bp = Blueprint('results', __name__, url_prefix='/results')

@results_bp.before_request
def check_auth():
    """Check if the user is authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))

@results_bp.route('/<int:track_id>/<int:user_id>')
def view_results(track_id, user_id):
    """View prediction results for a user and track."""
    poule_id = request.args.get('poule_id', type=int) or session.get('poule')
    
    if not poule_id:
        flash('Poule not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Store poule_id in session for subsequent requests
    session['poule'] = poule_id
    
    # Get qualifying results
    top3 = QualifyingPrediction.get_results_with_points(user_id, track_id, poule_id)
    
    # Get race results
    top5 = RacePrediction.get_results_with_points(user_id, track_id, poule_id)
    
    # Get head-to-head options and predictions
    hth_options = sorted(Prediction.get_head_to_head_options(track_id), key=lambda x: x[0])  # Sort by headtohead ID
    hth_predictions = Prediction.get_head_to_head_prediction(user_id, track_id, poule_id)
    
    # Format head-to-head data
    hth_list = []
    for option in hth_options:
        option_data = list(option)
        for prediction in hth_predictions:
            if option[0] == prediction[0]:
                option_data.append(prediction[1])
        hth_list.append(option_data)
    
    # Get head-to-head points
    hth_points = _get_head_to_head_points(user_id, track_id, poule_id)
    
    # Get bonus results
    bonus_data = BonusPrediction.get_results_with_points(user_id, track_id, poule_id)
    
    # Get username of the viewed user
    viewed_user = User.get_by_id(user_id)
    viewed_username = viewed_user.username if viewed_user else "Unknown User"
    
    return render_template(
        'predictResults.html', 
        top3=top3, 
        top5=top5, 
        poule=poule_id, 
        hth=hth_list,
        hthPoints=hth_points,
        bonusData=bonus_data,
        userid=user_id,
        viewed_username=viewed_username
    )

def _get_head_to_head_points(user_id, track_id, poule_id):
    """Get head-to-head points for a user, track, and poule."""
    with get_db_cursor() as cursor:
        # First get all head-to-head options for this track
        cursor.execute("""
            SELECT id 
            FROM headtohead_combinations 
            WHERE track = %s
            ORDER BY id
        """, (track_id,))
        all_hth_ids = [row[0] for row in cursor.fetchall()]
        
        # Then get the predictions
        cursor.execute("""
            SELECT headtohead_id, COALESCE(points, 0) as points
            FROM headtoheadprediction 
            WHERE user_id = %s AND track = %s AND poule = %s
        """, (user_id, track_id, poule_id))
        results = cursor.fetchall()
        
        # Create a dictionary mapping headtohead_id to points
        points_dict = {hth_id: points for hth_id, points in results}
        
        # Return None for no prediction, actual points (including 0) for predictions made
        return [points_dict.get(hth_id, None) for hth_id in all_hth_ids] 