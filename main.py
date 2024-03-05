from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
import databaseconnection
import getDriverTrack
import getPouleData
import results as resultsScript
from datetime import datetime
import registerUser

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Replace this with your actual authentication logic
def authenticate(username, password):
    if username == "admin" and password == "admin":
        return ("admin", None, None)  # Indicate admin login

    conn = databaseconnection.connect()
    query = "SELECT * FROM users WHERE username = %s AND password = %s;"
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    data = cursor.fetchall()
    conn.close()

    if data:
        # Return the first row as a tuple (user_id, username)
        return (True, data[0][0], data[0][1])
    else:
        return (False, None, None)

@app.before_request
def before_request():
    # Check if the user is logged in before each request
    if 'user_id' not in session and request.endpoint not in ['login', 'index', 'static', 'register']:
        return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    auth_result = authenticate(username, password)

    if auth_result[0] == "admin":
        session['user_id'] = -1
        return redirect(url_for('admin'))  # Redirect to admin route
    elif auth_result[0]:
        # Successful login, store user_id in session and redirect to the dashboard
        session['user_id'] = auth_result[1]
        return redirect(url_for('dashboard', userid=auth_result[1]))
    else:
        # Failed login, redirect back to the login page
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            registerUser.register(username, password)
        return redirect(url_for('index'))
    else:
        return render_template('createUser.html')

@app.route('/admin')
def admin():
    if session.get('user_id') == -1:
        return render_template("admin.html")
    else:
        return redirect(url_for('index'))

@app.route('/submit_results', methods=['POST'])
def submit_results():
    if request.method == 'POST':
        track_id = request.form.get('track')
        racesession = request.form.get('racesession')
        driver_positions = request.form.getlist('driver_positions[]')
        driver_ids = request.form.getlist('driver_ids[]')

        lst = []
        for driver_id, position in zip(driver_ids, driver_positions):
            lst.append((driver_id, position))

        resultsScript.insert_results(track_id, lst, racesession)
    return redirect(url_for('admin'))

@app.route('/results')
def resultsData():
    drivers = getDriverTrack.getDriver()
    tracks = getDriverTrack.getTracks()
    return render_template("addResults.html", drivers=drivers, tracks=tracks)

@app.route('/get_results', methods=['POST'])
def get_results():
    print("test")
    track_id = request.form.get('track')
    results = getDriverTrack.getResult(track_id)
    
    return jsonify(results=results)


@app.route('/addData')
def addData():
    drivers = getDriverTrack.getDriver()
    tracks = getDriverTrack.getTracks()
    return render_template("addData.html", drivers=drivers, tracks=tracks)

import calcPoints as cp
@app.route('/calcPoints', methods=['GET', 'POST'])
def calcPoints():
    if request.method == 'POST':
        track_id = request.form.get('track')
        racesession = request.form.get('racesession')
        try:
            if racesession == "qualiresults":
                cp.calcQualiPoints(track_id)
            else:
                cp.calcRacePoints(track_id)
        except:
            print("error calculating points")
    tracks = getDriverTrack.getTracks()
    raceresults = []
    qualiresults = []
    for x in tracks:
        raceresults.append(getDriverTrack.getRaceResult(x[0]))
        qualiresults.append(getDriverTrack.getQualiResult(x[0]))
    return render_template("calcPoints.html", tracks=tracks, qualiresults=qualiresults, raceresults=raceresults)


@app.route('/add_driver', methods=['POST'])
def add_driver():
    driver_name = request.form.get('driver_name')
    driver_team = request.form.get('driver_team')

    resultsScript.insert_driver(driver_name, driver_team)

    return redirect('/addData')

@app.route('/add_track', methods=['POST'])
def add_track():
    track_name = request.form.get('track_name')
    quali_date = request.form.get('quali_date')
    race_date = request.form.get('race_date')

    resultsScript.insert_track(track_name, quali_date, race_date)

    return redirect('/addData')

@app.route('/dashboard')
def dashboard(): 
    user_id = session.get('user_id')
    poules = getPouleData.getPoules(user_id)
    return render_template("dashboard.html", poules=poules)

@app.route('/poule/<int:poule>')
def poule(poule):
    session['poule'] = poule
    users = getPouleData.getPouleUsers(poule)
    return render_template('poule.html', poule=poule, users=users)

@app.route('/predictList/<poule>')
def predictList(poule):
    tracks = getDriverTrack.getTracks()
    print(tracks)
    avaTracks = []
    disTracks = []
    for x in tracks:
        if x[2] > datetime.now():
            avaTracks.append(x)
        else:
            disTracks.append(x)
    return render_template('predictList.html', avaTracks=avaTracks, disTracks=disTracks, poule=poule)

@app.route('/joinPoule', methods=['POST'])
def joinPoule():
    poule_name = request.form.get('poulename')
    userid = session.get('user_id')
    getPouleData.joinPoule(poule_name, userid)
    return redirect(url_for('dashboard'))

@app.route('/predict/<trackid>', methods=['GET', 'POST'])
def predict(trackid):
    user_id = session.get('user_id')
    poule = session.get('poule')            
    drivers = getDriverTrack.getDriver()
    tracks = getDriverTrack.getTracks()

    top3 = getPouleData.getTop3Open(poule, user_id, trackid)
    top5 = getPouleData.getTop5Open(poule, user_id, trackid)

    # Access flashed messages within the context of the template
    message = str(get_flashed_messages(category_filter=['message']))[2:-2]
    ontime = str(get_flashed_messages(category_filter=['ontime']))[1:-1]
    if ontime == "False":
        ontime = False
    else:
        ontime = True

    print(top3)
    # Set default values for top3 and top5 if they exist
    top3_default = top3 or (1, 1, 1)
    top5_default = top5 or (1, 1, 1, 1, 1)

    print(top3_default)

    # Zip the values in Python and pass them to the template
    top3_zipped = list(zip(range(1, 4), top3_default))
    top5_zipped = list(zip(range(1, 6), top5_default))

    return render_template("predict.html", userid=user_id, trackid=trackid, drivers=drivers, tracks=tracks, poule=poule, message=message, ontime=ontime, top3_zipped=top3_zipped, top5_zipped=top5_zipped)



@app.route('/predict_top3/<trackid>', methods=['POST'])
def predict_top3(trackid):
    trackData = getDriverTrack.getTrackData(trackid)
    if trackData[0][2] < datetime.now():
        flash('Your qualifying prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        user_id = session.get('user_id')
        poule = session.get('poule')
        track = trackid

        # Predictions for top 3 qualifying
        top3_qualifying = [request.form.get(f'top3_qualifying_{place}') for place in range(1, 4)]
        top3_qualifying.append(track)
        top3_qualifying.append(poule)
        print('Top 3 Qualifying:', top3_qualifying)
        storeTop3(user_id, top3_qualifying)
        flash('Your qualifying prediction is submitted', 'message')
        flash(False, 'ontime')

    return redirect(url_for('predict', trackid=trackid))

@app.route('/predict_top5/<trackid>', methods=['POST'])
def predict_top5(trackid):
    trackData = getDriverTrack.getTrackData(trackid)
    if trackData[0][3] < datetime.now():
        flash('Your race prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        user_id = session.get('user_id')
        poule = session.get('poule')
        track = trackid
        # Predictions for top 5 race
        top5_race = [request.form.get(f'top5_race_{place}') for place in range(1, 6)]
        top5_race.append(track)
        top5_race.append(poule)
        print('Top 5 Race:', top5_race)
        storeTop5(user_id, top5_race)
        flash('Your race prediction is submitted', 'message')
        flash(False, 'ontime')

    return redirect(url_for('predict', trackid=trackid))


@app.route('/predictResults/<trackid>')
def predictResults(trackid):
    user_id = session.get('user_id')
    poule = session.get('poule')
    top3 = getPouleData.getTop3Closed(poule, user_id, trackid)
    top5 = getPouleData.getTop5Closed(poule, user_id, trackid)
    
    return render_template('predictResults.html', top3=top3, top5=top5, poule=poule)

def storeTop3(user_id, prediction):
    conn = databaseconnection.connect()
    # Convert driver IDs to integers
    driver1_id = int(prediction[0])
    driver2_id = int(prediction[1])
    driver3_id = int(prediction[2])

    # Insert or update into the database (upsert)
    query = """
        INSERT INTO top3_quali (user_id, driver1_id, driver2_id, driver3_id, track, date, poule)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
        ON CONFLICT (user_id, track, poule)
        DO UPDATE SET 
            driver1_id = EXCLUDED.driver1_id, 
            driver2_id = EXCLUDED.driver2_id, 
            driver3_id = EXCLUDED.driver3_id,
            date = CURRENT_TIMESTAMP;
    """
    cursor = conn.cursor()
    cursor.execute(query, (user_id, driver1_id, driver2_id, driver3_id, prediction[3], prediction[4]))
    conn.commit()
    conn.close()

def storeTop5(user_id, prediction):
    conn = databaseconnection.connect()
    # Convert driver IDs to integers
    driver1_id = int(prediction[0])
    driver2_id = int(prediction[1])
    driver3_id = int(prediction[2])
    driver4_id = int(prediction[3])
    driver5_id = int(prediction[4])

    # Insert or update into the database (upsert)
    query = """
        INSERT INTO top5_race (user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, track, date, poule)
        VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
        ON CONFLICT (user_id, track, poule)
        DO UPDATE SET 
            driver1_id = EXCLUDED.driver1_id, 
            driver2_id = EXCLUDED.driver2_id, 
            driver3_id = EXCLUDED.driver3_id,
            driver4_id = EXCLUDED.driver4_id,
            driver5_id = EXCLUDED.driver5_id,
            date = CURRENT_TIMESTAMP;
    """
    cursor = conn.cursor()
    cursor.execute(query, (user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, prediction[5], prediction[6]))
    conn.commit()
    conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    # Clear user_id from session on logout
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5050")
