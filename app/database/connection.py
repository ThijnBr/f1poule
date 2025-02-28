import psycopg2
from flask import current_app, g
from contextlib import contextmanager

def get_db():
    """Get a database connection from the Flask application context."""
    if 'db' not in g:
        g.db = connect()
    return g.db

def connect():
    """Create a new database connection using the application configuration."""
    config = current_app.config['DB_CONFIG']
    conn = psycopg2.connect(**config)
    return conn

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for database operations.
    
    Args:
        commit (bool): Whether to commit the transaction after the operation.
    
    Yields:
        cursor: A database cursor.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close() 