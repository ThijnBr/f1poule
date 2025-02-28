-- Users and Poules tables
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS poules (
    poule_id SERIAL PRIMARY KEY,
    poule_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_poule (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    poule_id INT REFERENCES poules(poule_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, poule_id),
    CONSTRAINT unique_user_poule UNIQUE (user_id, poule_id)
);

CREATE TABLE IF NOT EXISTS driver (
    driver_id SERIAL PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    team_id INTEGER
);

CREATE TABLE IF NOT EXISTS track (
    id SERIAL PRIMARY KEY,
    track_name VARCHAR(50),
    track_quali_date TIMESTAMP,
    track_race_date TIMESTAMP
);

-- Prediction tables
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

-- Results tables
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
    dnf BOOLEAN
);

-- Head to Head tables
CREATE TABLE IF NOT EXISTS headtohead (
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

-- Bonus prediction tables
CREATE TABLE IF NOT EXISTS bonusprediction (
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

CREATE TABLE IF NOT EXISTS bonusresults (
    id SERIAL PRIMARY KEY,
    fl INT REFERENCES driver(driver_id),
    dod INT REFERENCES driver(driver_id),
    track INTEGER REFERENCES track(id) UNIQUE
);

CREATE TABLE IF NOT EXISTS team (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS headtohead_combinations (
    id SERIAL PRIMARY KEY,
    driver1_id INT REFERENCES driver(driver_id),
    driver2_id INT REFERENCES driver(driver_id),
    track INTEGER REFERENCES track(id)
);

-- Add unique constraints
DO $$ 
BEGIN
    -- Check and add unique_user_track_combination for top3_quali
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_user_track_combination'
    ) THEN
        ALTER TABLE top3_quali ADD CONSTRAINT unique_user_track_combination UNIQUE (user_id, track, poule);
    END IF;

    -- Check and add unique_user_track_combination1 for top5_race
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_user_track_combination1'
    ) THEN
        ALTER TABLE top5_race ADD CONSTRAINT unique_user_track_combination1 UNIQUE (user_id, track, poule);
    END IF;

    -- Check and add unique_prediction_constraint for headtoheadprediction
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_prediction_constraint'
    ) THEN
        ALTER TABLE headtoheadprediction ADD CONSTRAINT unique_prediction_constraint UNIQUE (user_id, headtohead_id, track, poule);
    END IF;

    -- Check and add unique_bonus_constraint for bonusprediction
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_bonus_constraint'
    ) THEN
        ALTER TABLE bonusprediction ADD CONSTRAINT unique_bonus_constraint UNIQUE (user_id, track, poule);
    END IF;
END $$;

-- Migration to update driver table to reference team
DO $$ 
BEGIN
    -- Add team_id column to driver table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'driver' AND column_name = 'team_id'
    ) THEN
        -- Add the new column
        ALTER TABLE driver ADD COLUMN team_id INTEGER;

        -- First ensure all teams exist in the team table
        INSERT INTO team (team_name)
        SELECT DISTINCT driver_team 
        FROM driver 
        WHERE driver_team IS NOT NULL
        ON CONFLICT (team_name) DO NOTHING;

        -- Update team_id based on existing driver_team values
        UPDATE driver d
        SET team_id = t.team_id
        FROM team t
        WHERE d.driver_team = t.team_name;

        -- Verify all drivers have a team_id
        IF EXISTS (SELECT 1 FROM driver WHERE team_id IS NULL) THEN
            RAISE EXCEPTION 'Some drivers do not have a team assigned. Please check data consistency.';
        END IF;

        -- Add foreign key constraint and make not null
        ALTER TABLE driver 
        ADD CONSTRAINT fk_driver_team 
        FOREIGN KEY (team_id) 
        REFERENCES team(team_id);

        ALTER TABLE driver ALTER COLUMN team_id SET NOT NULL;

        -- Remove the old driver_team column
        ALTER TABLE driver DROP COLUMN driver_team;
    END IF;
END $$;

-- Add active column to driver table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'driver' AND column_name = 'active'
    ) THEN
        ALTER TABLE driver ADD COLUMN active BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Add year column to poules table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'poules' AND column_name = 'year'
    ) THEN
        -- Add the year column with default value of current year
        ALTER TABLE poules ADD COLUMN year INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE);        
        -- Make the year column not null
        ALTER TABLE poules ALTER COLUMN year SET NOT NULL;
    END IF;
END $$;

WITH unique_predictions 
AS (SELECT DISTINCT h.driver1_id, h.driver2_id, hp.track FROM headtoheadprediction hp JOIN headtohead h 
ON hp.headtohead_id = h.id 
WHERE NOT EXISTS 
(SELECT 1 FROM headtohead_combinations hc 
WHERE hc.track = hp.track 
AND ((hc.driver1_id = h.driver1_id 
AND hc.driver2_id = h.driver2_id) 
OR (hc.driver1_id = h.driver2_id 
AND hc.driver2_id = h.driver1_id)))) 
INSERT INTO headtohead_combinations (driver1_id, driver2_id, track) 
SELECT driver1_id, driver2_id, track 
FROM unique_predictions;

-- Migration to update headtoheadprediction to reference headtohead_combinations
DO $$
BEGIN
    -- First, drop the existing foreign key constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'headtoheadprediction_headtohead_id_fkey'
    ) THEN
        ALTER TABLE headtoheadprediction 
        DROP CONSTRAINT headtoheadprediction_headtohead_id_fkey;
    END IF;

    -- Add new foreign key constraint to reference headtohead_combinations
    ALTER TABLE headtoheadprediction 
    ADD CONSTRAINT headtoheadprediction_headtohead_id_fkey 
    FOREIGN KEY (headtohead_id) 
    REFERENCES headtohead_combinations(id);

    -- Drop the old headtohead table if it exists and is no longer needed
    DROP TABLE IF EXISTS headtohead;
END $$;

