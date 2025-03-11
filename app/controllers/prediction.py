from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from app.models.track import Track
from app.models.driver import Driver
from app.models.prediction import Prediction, QualifyingPrediction, RacePrediction, BonusPrediction
from app.models.poule import Poule
from app.models.user import User
from datetime import datetime

prediction_bp = Blueprint('prediction', __name__, url_prefix='/prediction')

@prediction_bp.before_request
def check_auth():
    """Check if the user is authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))

@prediction_bp.route('/list/<int:poule_id>/<int:user_id>')
def prediction_list(poule_id, user_id):
    """Show list of tracks for predictions."""
    session['poule'] = poule_id
    
    # Get poule to determine year
    poule = Poule.get_by_id(poule_id)
    if not poule:
        flash('Poule not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Get tracks for the poule's year
    tracks = Track.get_all(year=poule.year)
    now = datetime.now()
    
    # Split tracks into upcoming and past
    upcoming_tracks = [track for track in tracks if track[3] > now]  # track[3] is race_date
    past_tracks = [track for track in tracks if track[3] <= now]  # track[3] is race_date
    
    # Sort tracks by date
    upcoming_tracks.sort(key=lambda x: x[3])  # Sort by race_date ascending
    past_tracks.sort(key=lambda x: x[3], reverse=True)  # Sort by race_date descending
    
    return render_template(
        'predictList.html', 
        avaTracks=upcoming_tracks, 
        disTracks=past_tracks, 
        poule=poule_id, 
        userid=user_id
    )

@prediction_bp.route('/<int:track_id>', methods=['GET', 'POST'])
def predict(track_id):
    """Make predictions for a track."""
    user_id = session.get('user_id')
    poule_id = request.args.get('poule_id', type=int) or session.get('poule')
    
    if not poule_id:
        flash('Poule not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Store poule_id in session for subsequent requests
    session['poule'] = poule_id
    
    # Get poule to determine year
    poule = Poule.get_by_id(poule_id)
    if not poule:
        flash('Poule not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Get track data to check if prediction is still allowed
    track = Track.get_by_id(track_id)
    if not track:
        flash('Track not found', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Check if track is from the same year as the poule
    track_year = track.race_date.year
    if track_year != poule.year:
        flash('You cannot make predictions for tracks from a different year than the poule', 'error')
        return redirect(url_for('prediction.prediction_list', poule_id=poule_id, user_id=user_id))
    
    # Get head-to-head options
    hth_options = Prediction.get_head_to_head_options(track_id)
    hth_predictions = Prediction.get_head_to_head_prediction(user_id, track_id, poule_id)
    
    # Format head-to-head data
    hth_list = []
    for option in hth_options:
        option_data = list(option)
        for prediction in hth_predictions:
            if option[0] == prediction[0]:
                option_data.append(prediction[1])
        hth_list.append(option_data)
    
    # Get existing predictions
    top3 = QualifyingPrediction.get_prediction(user_id, track_id, poule_id)
    top5 = RacePrediction.get_prediction(user_id, track_id, poule_id)
    bonus = BonusPrediction.get_prediction(user_id, track_id, poule_id)
    
    # Set default values
    top3_default = top3 or (0, 0, 0)
    top5_default = top5 or (0, 0, 0, 0, 0)
    bonus_default = bonus or (0, 0, 0)
    
    # Zip the values for the template
    top3_zipped = list(zip(range(1, 4), top3_default))
    top5_zipped = list(zip(range(1, 6), top5_default))
    
    # Get user, track, and poule info
    user = User.get_by_id(user_id)
    user_name = user.username if user else None
    track_name = track.track_name
    poule_name = poule.name
    
    # Format deadline times for JavaScript
    quali_deadline = track.quali_date.strftime('%Y-%m-%dT%H:%M:%S')
    race_deadline = track.race_date.strftime('%Y-%m-%dT%H:%M:%S')
    now = datetime.now()
    
    # Check if predictions are still allowed
    quali_active = track.quali_date > now
    race_active = track.race_date > now
    
    # Check for flashed messages
    message = str(get_flashed_messages(category_filter=['message']))[2:-2]
    ontime = str(get_flashed_messages(category_filter=['ontime']))[1:-1]
    if ontime == "False":
        ontime = False
    else:
        ontime = True
    
    # Get all active drivers for selection
    drivers = Driver.get_all(active_only=True)
    
    return render_template(
        "predict.html",
        userid=user_id,
        trackid=track_id,
        drivers=drivers,
        tracks=[track],
        poule=poule_id,
        message=message,
        ontime=ontime,
        top3_zipped=top3_zipped,
        top5_zipped=top5_zipped,
        headtohead=hth_list,
        bonusValues=bonus_default,
        track_name=track_name,
        user_name=user_name,
        poule_name=poule_name,
        quali_deadline=quali_deadline,
        race_deadline=race_deadline,
        quali_active=quali_active,
        race_active=race_active
    )

@prediction_bp.route('/top3/<int:track_id>', methods=['POST'])
def predict_top3(track_id):
    """Submit qualifying (top 3) predictions."""
    user_id = session.get('user_id')
    poule_id = session.get('poule')
    
    # Get poule and track to validate year
    poule = Poule.get_by_id(poule_id)
    track = Track.get_by_id(track_id)
    
    if not poule or not track:
        flash('Invalid poule or track', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Check if track is from the same year as the poule
    track_year = track.race_date.year
    if track_year != poule.year:
        flash('You cannot make predictions for tracks from a different year than the poule', 'error')
        return redirect(url_for('prediction.prediction_list', poule_id=poule_id, user_id=user_id))
    
    # Check if prediction is still allowed
    if track.quali_date < datetime.now():
        flash('Your qualifying prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        # Get predictions from form
        driver1_id = request.form.get('top3_qualifying_1')
        driver2_id = request.form.get('top3_qualifying_2')
        driver3_id = request.form.get('top3_qualifying_3')
        
        # Convert empty or 'None' values to None
        if driver1_id in ['None', '0', '']: driver1_id = None
        if driver2_id in ['None', '0', '']: driver2_id = None
        if driver3_id in ['None', '0', '']: driver3_id = None
        
        # Check for duplicate drivers
        drivers = [d for d in [driver1_id, driver2_id, driver3_id] if d is not None]
        if len(drivers) != len(set(drivers)):
            return 'Duplicate drivers are not allowed', 400
        
        # Save prediction
        QualifyingPrediction.save_prediction(
            user_id, track_id, poule_id, driver1_id, driver2_id, driver3_id
        )
        flash('Qualifying prediction saved', 'success')
        return '', 204  # No content response for AJAX
    
    return redirect(url_for('prediction.predict', track_id=track_id))

@prediction_bp.route('/top5/<int:track_id>', methods=['POST'])
def predict_top5(track_id):
    """Submit race (top 5) predictions."""
    user_id = session.get('user_id')
    poule_id = session.get('poule')
    
    # Get poule and track to validate year
    poule = Poule.get_by_id(poule_id)
    track = Track.get_by_id(track_id)
    
    if not poule or not track:
        flash('Invalid poule or track', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Check if track is from the same year as the poule
    track_year = track.race_date.year
    if track_year != poule.year:
        flash('You cannot make predictions for tracks from a different year than the poule', 'error')
        return redirect(url_for('prediction.prediction_list', poule_id=poule_id, user_id=user_id))
    
    # Check if prediction is still allowed
    if track.race_date < datetime.now():
        flash('Your race prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        # Get predictions from form
        driver1_id = request.form.get('top5_race_1')
        driver2_id = request.form.get('top5_race_2')
        driver3_id = request.form.get('top5_race_3')
        driver4_id = request.form.get('top5_race_4')
        driver5_id = request.form.get('top5_race_5')
        
        # Convert empty or 'None' values to None
        if driver1_id in ['None', '0', '']: driver1_id = None
        if driver2_id in ['None', '0', '']: driver2_id = None
        if driver3_id in ['None', '0', '']: driver3_id = None
        if driver4_id in ['None', '0', '']: driver4_id = None
        if driver5_id in ['None', '0', '']: driver5_id = None
        
        # Get bonus predictions
        fastest_lap = request.form.get("fastestlap")
        dnf = request.form.get("dnf")
        dod = request.form.get("dod")
        
        # Convert empty or 'None' values to None
        if fastest_lap in ['None', '0', '']: fastest_lap = None
        if dnf in ['None', '0', '', 'No DNF']: dnf = None
        if dod in ['None', '0', '']: dod = None
        
        # Check for duplicate drivers in race prediction
        race_drivers = [d for d in [driver1_id, driver2_id, driver3_id, driver4_id, driver5_id] if d is not None]
        if len(race_drivers) != len(set(race_drivers)):
            return 'Duplicate drivers are not allowed', 400
        
        # Save predictions
        RacePrediction.save_prediction(
            user_id, track_id, poule_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id
        )
        BonusPrediction.save_prediction(
            user_id, track_id, poule_id, fastest_lap, dnf, dod
        )
        flash('Race prediction saved', 'success')
        return '', 204  # No content response for AJAX
    
    return redirect(url_for('prediction.predict', track_id=track_id))

@prediction_bp.route('/headtohead/<int:track_id>', methods=['POST'])
def predict_headtohead(track_id):
    """Submit head-to-head predictions."""
    user_id = session.get('user_id')
    poule_id = session.get('poule')
    
    # Get poule and track to validate year
    poule = Poule.get_by_id(poule_id)
    track = Track.get_by_id(track_id)
    
    if not poule or not track:
        flash('Invalid poule or track', 'error')
        return redirect(url_for('poule.dashboard'))
    
    # Check if track is from the same year as the poule
    track_year = track.race_date.year
    if track_year != poule.year:
        flash('You cannot make predictions for tracks from a different year than the poule', 'error')
        return redirect(url_for('prediction.prediction_list', poule_id=poule_id, user_id=user_id))
    
    # Check if prediction is still allowed
    if track.race_date < datetime.now():
        flash('Your head-to-head prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        # Get prediction from form
        driver = request.form.get('driver_selection')
        headtohead_id, driver_selected = driver.split('-')
        
        # Save prediction
        Prediction.make_head_to_head_prediction(
            user_id, headtohead_id, driver_selected, track_id, poule_id
        )
        flash('Head-to-head prediction saved', 'success')
        return '', 204  # No content response for AJAX
    
    return redirect(url_for('prediction.predict', track_id=track_id)) 