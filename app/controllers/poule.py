from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.user import User
from app.models.poule import Poule

poule_bp = Blueprint('poule', __name__, url_prefix='/poule')

@poule_bp.before_request
def check_auth():
    """Check if the user is authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))

@poule_bp.route('/dashboard')
def dashboard():
    """Render the user dashboard with their poules."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    # Get user's poules and split them into active and previous
    all_poules = user.get_poules()
    current_year = Poule.get_current_year()
    
    active_poules = [p for p in all_poules if p[2] == current_year]
    previous_poules = [p for p in all_poules if p[2] < current_year]
    
    return render_template(
        "dashboard.html",
        active_poules=active_poules,
        previous_poules=previous_poules
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