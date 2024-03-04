import databaseconnection

conn = databaseconnection.connect()
cursor = conn.cursor()

drivers = [['Max Verstappen', 'Red Bull'], ['Lewis Hamilton', 'Mercedes'],['George Russel', 'Mercedes'], ['Carlos Sainz', 'Ferrari'], ['Charles Leclerc', "Ferrari"]]
tracks = [['Bahrain', '2024-03-01:1500','2024-03-02:1700'], ['Saudi Arabia', '2024-03-9:1500','2024-03-10:1700']]  # Corrected date format

query = "INSERT INTO users (username, password) VALUES ('thijn', 'thijn')"
cursor.execute(query)
query = "INSERT INTO users (username, password) VALUES ('test', 'test')"
cursor.execute(query)
query = "INSERT INTO poules (poule_name) VALUES ('f1')"
cursor.execute(query)
query = "INSERT INTO poules (poule_name) VALUES ('peeps')"
cursor.execute(query)

for x in drivers:
    query = f"INSERT INTO driver (driver_name, driver_team) VALUES ('{x[0]}', '{x[1]}')"
    cursor.execute(query)

for x in tracks:
    query = f"INSERT INTO track (track_name, track_quali_date, track_race_date) VALUES ('{x[0]}', '{x[1]}', '{x[2]}')"
    cursor.execute(query)

conn.commit()

cursor.close()
conn.close()

#TRUNCATE TABLE users, poules, user_poule,  driver, track, top3_quali, top5_race;
