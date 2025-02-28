# F1 Poule

A Formula 1 prediction pool application where users can join pools, make predictions for races, and earn points based on their predictions.

## Features

- User authentication and registration
- Create and join prediction pools
- Make predictions for qualifying and race results
- Head-to-head driver predictions
- Bonus predictions (fastest lap, DNF, driver of the day)
- Points calculation based on prediction accuracy
- Leaderboards for each pool

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd f1poule
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the database:
   - Update the database connection settings in `f1poule/config/default.py`
   - Make sure PostgreSQL is running and the database is created

4. Run the application:
   ```
   python -m f1poule.run
   ```

5. Access the application at http://localhost:5000

## Project Structure

```
f1poule/
├── app/
│   ├── controllers/      # Route handlers
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── database/         # Database connection
│   ├── templates/        # HTML templates
│   ├── static/           # Static files (CSS, JS)
│   └── utils/            # Utility functions
├── config/               # Configuration files
├── requirements.txt      # Dependencies
├── run.py                # Development server
└── wsgi.py               # Production WSGI entry point
``` 