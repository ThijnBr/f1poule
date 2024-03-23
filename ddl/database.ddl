CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE poules (
    poule_id SERIAL PRIMARY KEY,
    poule_name VARCHAR(50) NOT NULL
);

CREATE TABLE user_poule (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    poule_id INT REFERENCES poules(poule_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, poule_id),
    CONSTRAINT unique_user_poule UNIQUE (user_id, poule_id)
);

CREATE TABLE driver (
    driver_id SERIAL PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    driver_team VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS track (
    id SERIAL PRIMARY KEY,
    track_name VARCHAR(50),
    track_quali_date TIMESTAMP,
    track_race_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS top3_quali (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    driver1_id INTEGER REFERENCES driver(driver_id),
    driver2_id INTEGER REFERENCES driver(driver_id),
    driver3_id INTEGER REFERENCES driver(driver_id),
    driver1points INTEGER DEFAULT 0,
    driver2points INTEGER DEFAULT 0,
    driver3points INTEGER DEFAULT 0,
    track INTEGER REFERENCES track(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    poule INTEGER REFERENCES poules(poule_id)
);

CREATE TABLE IF NOT EXISTS top5_race (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    driver1_id INTEGER REFERENCES driver(driver_id),
    driver2_id INTEGER REFERENCES driver(driver_id),
    driver3_id INTEGER REFERENCES driver(driver_id),
    driver4_id INTEGER REFERENCES driver(driver_id),
    driver5_id INTEGER REFERENCES driver(driver_id),
    driver1points INTEGER DEFAULT 0,
    driver2points INTEGER DEFAULT 0,
    driver3points INTEGER DEFAULT 0,
    driver4points INTEGER DEFAULT 0,
    driver5points INTEGER DEFAULT 0,
    track INTEGER REFERENCES track(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    poule INTEGER REFERENCES poules(poule_id)
);

CREATE TABLE IF NOT EXISTS raceresults (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES track(id),
    position INTEGER,
    driver_id INTEGER REFERENCES driver(driver_id),
    dnf BOOLEAN,
    result_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS qualiresults (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES track(id),
    position INTEGER,
    driver_id INTEGER REFERENCES driver(driver_id),
    result_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dnf BOOLEAN,
);
CREATE TABLE IF NOT EXISTS headtohead(
	id SERIAL PRIMARY KEY,
	driver1_id INT REFERENCES driver(driver_id),
	driver2_id INT REFERENCES driver(driver_id)
);
CREATE TABLE IF NOT EXISTS headtoheadprediction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    headtohead_id INTEGER REFERENCES headtohead(id),
    driverselected BOOLEAN,
    track INTEGER REFERENCES track(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	points INT,
    poule INTEGER REFERENCES poules(poule_id)
);

CREATE TABLE IF NOT EXISTS bonusprediction(
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(user_id),
	poule INTEGER REFERENCES poules(poule_id),
	track INTEGER REFERENCES track(id),
	fastestlap INT REFERENCES driver(driver_id),
	dnf INT REFERENCES driver(driver_id),
	dod INT REFERENCES driver(driver_id),
	flpoints INT,
	dnfpoints INT,
	dodpoints INT
);

CREATE TABLE IF NOT EXISTS bonusresults(
	id SERIAL PRIMARY KEY,
	fl INT REFERENCES driver(driver_id),
	dod INT REFERENCES driver(driver_id),
    track INTEGER REFERENCES track(id) UNIQUE,
);

-- Add a unique constraint to top3_quali
ALTER TABLE top3_quali ADD CONSTRAINT unique_user_track_combination UNIQUE (user_id, track, poule);
ALTER TABLE top5_race ADD CONSTRAINT unique_user_track_combination1 UNIQUE (user_id, track, poule);
ALTER TABLE top5_race ADD CONSTRAINT unique_user_track_combination1 UNIQUE (user_id, track, poule);
ALTER TABLE headtoheadprediction ADD CONSTRAINT unique_prediction_constraint UNIQUE (user_id, headtohead_id, track, poule);
ALTER TABLE bonusprediction ADD CONSTRAINT unique_bonus_constraint UNIQUE (user_id, track, poule);