from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
import databaseconnection
import getDriverTrack
import getPouleData
import results as resultsScript
from datetime import datetime
import hth as headtoHead
import registerUser
import bonus
import test as getResults
import os
import psycopg2

os.path.join("/var/www/f1poule")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
conn = databaseconnection.connect()
hth = headtoHead.getHeadToHead(conn)
drivers = getDriverTrack.getDriver(conn)
tracks = getDriverTrack.getTracks(conn)
# Replace this with your actual authentication logic
def authenticate(username, password, conn):
    if username == "admin" and password == "admin":
        return ("admin", None, None)

    query = "SELECT * FROM users WHERE username = %s AND password = %s;"
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    data = cursor.fetchall()

    if data:
        return (True, data[0][0], data[0][1])
    else:
        return (False, None, None)


@app.before_request
def before_request():
    global conn
    # Check if `conn` is a valid psycopg2 connection, else reconnect
    if not isinstance(conn, psycopg2.extensions.connection) or conn.closed:
        conn = databaseconnection.connect()
    # Check if the user is logged in before each request
    if 'user_id' not in session and request.endpoint not in ['login', 'index', 'static', 'register']:
        return redirect(url_for('index'))

@app.route('/')
def index():
    global conn
    conn.close()
    conn = databaseconnection.connect()
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    auth_result = authenticate(username, password, conn)  # Pass connection

    if auth_result[0] == "admin":
        session['user_id'] = -1
        return redirect(url_for('admin'))  # Redirect to admin route
    elif auth_result[0]:
        session['user_id'] = auth_result[1]
        return redirect(url_for('dashboard', userid=auth_result[1]))
    else:
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

        dnfs = []
        # Get DNF status from the hidden input as a list of integers (1 or 0)
        driver_dnfs = request.form.getlist('driver_dnf[]')
        for test in zip(driver_ids, driver_positions):
            if test[0] in driver_dnfs:
                dnfs.append("1")
            else:
                dnfs.append("0")

        print("Driver DNFs:", driver_dnfs)  # Debugging output

        lst = []
        for driver_id, position, dnf in zip(driver_ids, driver_positions, dnfs):
            lst.append((driver_id, position, dnf))

        fl = request.form.get('fl')
        dod = request.form.get('dod')
        if racesession == "raceresults":
            resultsScript.insertBonusResults(track_id, fl, dod)
        resultsScript.insert_results(track_id, lst, racesession)

    return redirect(url_for('admin'))



@app.route('/results', methods=['GET', 'POST'])
def resultsData():
    classified_tracks = getResults.get_available_races()
    track_link = None
    if request.method == 'POST':
        load_track = request.form.get('classified_tracks')
        
        data_type = request.form.get('type')  # Get the type of data (race or qualifying)
        # Load data based on the type
        if data_type == 'qualifying':
            # Fetch qualifying data
            results = getResults.get_final_quali_results(load_track)
            track_link = getResults.PDF_BASE_QUALI_URL.format(load_track.replace(' ', '%20'))
        else:
            # Fetch race data
            results = getResults.get_final_race_results(load_track)
            track_link = getResults.PDF_BASE_URL.format(load_track.replace(' ', '%20'))

        # Extract individual components from the results
        final_results = results[0]  # List of final results (driver positions)
        dnfs = results[1]           # List of drivers who did not finish
        fastest_lap = results[2]    # Fastest lap driver name

    else:
        final_results = []
        dnfs = []
        fastest_lap = ''

    # Assuming you have `drivers` and `tracks` available from somewhere
    return render_template("addResults.html", drivers=drivers, tracks=tracks, 
                           final_results=final_results, dnfs=dnfs, 
                           fastest_lap=fastest_lap, classified_tracks=classified_tracks, track_link= track_link)

@app.route('/get_results', methods=['POST'])
def get_results():
    track_id = request.form.get('track')
    results = getDriverTrack.getResult(track_id)
    
    return jsonify(results=results)


@app.route('/addData')
def addData():
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
                cp.calcHeadtoHead(track_id, conn)
                cp.getBonusPredictions(track_id, conn)
        except Exception as E:
            print("error calculating points")
            print(E)
    tracks = getDriverTrack.getTracks(conn)
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
    user_id = session.get('user_id')
    return render_template('poule.html', poule=poule, users=users, user_id=user_id)

@app.route('/predictList/<poule>/<userid>')
def predictList(poule, userid):
    tracks = getDriverTrack.getTracks(conn)
    avaTracks = []
    disTracks = []
    for x in tracks:
        if x[3] > datetime.now():
            if int(userid) == int(session.get('user_id')):
                avaTracks.append(x)
        else:
            disTracks.append(x)
    return render_template('predictList.html', avaTracks=avaTracks, disTracks=disTracks, poule=poule, userid=userid)

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
    
    
    hthData = headtoHead.getPredictions(user_id, trackid, poule, conn)

    hthList = []
    for x in hth:
        hthList.append(list(x))

    for x in hthList:
        for y in hthData:
            if x[0] == y[0]:
                x.append(y[1])

    top3 = getPouleData.getTop3Open(poule, user_id, trackid, conn)
    top5 = getPouleData.getTop5Open(poule, user_id, trackid, conn)
    try:
        bonusDefault = bonus.getBonus(user_id, poule, trackid, conn)[0]
    except:
        bonusDefault = None
    # Access flashed messages within the context of the template
    message = str(get_flashed_messages(category_filter=['message']))[2:-2]
    ontime = str(get_flashed_messages(category_filter=['ontime']))[1:-1]
    if ontime == "False":
        ontime = False
    else:
        ontime = True
    # Set default values for top3 and top5 if they exist
    top3_default = top3 or (0, 0, 0)
    top5_default = top5 or (0, 0, 0, 0, 0)
    bonusValues = bonusDefault or (0,0,0)

    # Zip the values in Python and pass them to the template
    top3_zipped = list(zip(range(1, 4), top3_default))
    top5_zipped = list(zip(range(1, 6), top5_default))

    user_name, track_name, poule_name = getDriverTrack.getUserInfo(user_id, trackid, poule, conn)

    return render_template("predict.html", 
                       userid=user_id, 
                       trackid=trackid, 
                       drivers=drivers, 
                       tracks=tracks, 
                       poule=poule, 
                       message=message, 
                       ontime=ontime, 
                       top3_zipped=top3_zipped, 
                       top5_zipped=top5_zipped,
                       headtohead=hthList,
                       bonusValues=bonusValues,
                       track_name=track_name,
                       user_name=user_name,
                       poule_name=poule_name) 



@app.route('/predict_top3/<trackid>', methods=['POST'])
def predict_top3(trackid):
    trackData = getDriverTrack.getTrackData(trackid, conn)
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
        storeTop3(user_id, top3_qualifying)
        flash(False, 'ontime')
        return '', 204

    return redirect(url_for('predict', trackid=trackid))

@app.route('/predict_top5/<trackid>', methods=['POST'])
def predict_top5(trackid):
    trackData = getDriverTrack.getTrackData(trackid, conn)
    if trackData[0][3] < datetime.now():
        flash('Your race prediction is too late', 'message')
        flash(False, 'ontime')
    else:
        user_id = session.get('user_id')
        poule = session.get('poule')
        track = trackid
        
        fastestlap = request.form.get("fastestlap")
        dnf = request.form.get("dnf")
        if dnf == 'No DNF':
            dnf = None
        dod = request.form.get("dod")

        if dod in ['None', '0']:
            dod = None
        if dnf in ['None', '0']:
            dnf = None
        if fastestlap in ['None', '0']:
            fastestlap = None

        # Predictions for top 5 race
        top5_race = [request.form.get(f'top5_race_{place}') for place in range(1, 6)]
        top5_race.append(track)
        top5_race.append(poule)
        storeTop5(user_id, top5_race)
        bonus.insertBonus(user_id, poule, track, fastestlap, dnf, dod, conn)
        flash(False, 'ontime')
        return '', 204

    return redirect(url_for('predict', trackid=trackid))

@app.route('/headtohead/<trackid>', methods=['POST'])
def headtohead(trackid):
    trackData = getDriverTrack.getTrackData(trackid, conn)
    if trackData[0][3] > datetime.now():
        driver = request.form.get('driver_selection')
    
        user_id = session.get('user_id')
        headtohead_id = driver.split('-')[0]
        driverselected = driver.split('-')[1]
        poule = session.get('poule')
        headtoHead.makePredictions(user_id, headtohead_id, driverselected, trackid, poule, conn)
        return '', 204
    else:
        flash('Prediction is too late', 'message')
        flash(False, 'ontime')
        return redirect(url_for('predict', trackid=trackid))

@app.route('/predictResults/<trackid>/<user_id>')
def predictResults(trackid, user_id):
    poule = session.get('poule')
    top3 = getPouleData.getTop3Closed(poule, user_id, trackid, conn)
    top5 = getPouleData.getTop5Closed(poule, user_id, trackid, conn)
    hth = headtoHead.getHeadToHead(conn)
    hthData = headtoHead.getPredictions(user_id, trackid, poule, conn)
    bonusData = bonus.bonusResultClosed(trackid, user_id, poule, conn)
    if bonusData != []:
        bonusData = bonusData[0]

    hthList = []
    for x in hth:
        hthList.append(list(x))

    for x in hthList:
        for y in hthData:
            if x[0] == y[0]:
                x.append(y[1])
    
    hthPoints = headtoHead.getHthPoints(user_id,trackid,poule)
    
    return render_template('predictResults.html', top3=top3, top5=top5, poule=poule, hth=hthList, hthPoints=hthPoints, bonusData=bonusData)

def storeTop3(user_id, prediction):
    print(prediction)
    # Convert driver IDs to integers
    driver1_id = int(prediction[0]) if prediction[0] not in ['None', '0'] else None
    driver2_id = int(prediction[1]) if prediction[1] not in ['None', '0'] else None
    driver3_id = int(prediction[2]) if prediction[2] not in ['None', '0'] else None

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
    try:
        cursor.execute(query, (user_id, driver1_id, driver2_id, driver3_id, prediction[3], prediction[4]))
    except:
        conn.rollback()
    conn.commit()

def storeTop5(user_id, prediction):
    print(prediction)
    # Convert driver IDs to integers
    driver1_id = int(prediction[0]) if prediction[0] not in ['None', '0'] else None
    driver2_id = int(prediction[1]) if prediction[1] not in ['None', '0'] else None
    driver3_id = int(prediction[2]) if prediction[2] not in ['None', '0'] else None
    driver4_id = int(prediction[3]) if prediction[3] not in ['None', '0'] else None
    driver5_id = int(prediction[4]) if prediction[4] not in ['None', '0'] else None


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
    try:
        cursor.execute(query, (user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, prediction[5], prediction[6]))
    except:
        conn.rollback()
    conn.commit()

@app.route('/logout', methods=['POST'])
def logout():
    # Clear user_id from session on logout
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
