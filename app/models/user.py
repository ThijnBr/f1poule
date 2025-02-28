from app.database.connection import get_db_cursor
import bcrypt

class User:
    """User model for authentication and user management."""
    
    def __init__(self, user_id=None, username=None, password=None):
        self.user_id = user_id
        self.username = username
        self.password = password
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                return cls(user_id=user_data[0], username=user_data[1])
            return None
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate a user with username and password."""
        with get_db_cursor() as cursor:
            # First, get the user by username
            cursor.execute(
                "SELECT user_id, username, password FROM users WHERE username = %s",
                (username,)
            )
            user_data = cursor.fetchone()
            
            if user_data:
                stored_password = user_data[2]
                # Check if the password is hashed (starts with $2b$)
                if stored_password.startswith('$2b$'):
                    # Verify the hashed password
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                        return cls(user_id=user_data[0], username=user_data[1])
                else:
                    # For backward compatibility with non-hashed passwords
                    if password == stored_password:
                        # Update to hashed password for future logins
                        cls._update_password_to_hashed(user_data[0], password)
                        return cls(user_id=user_data[0], username=user_data[1])
            return None
    
    @classmethod
    def _update_password_to_hashed(cls, user_id, plain_password):
        """Update a user's password to a hashed version."""
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE user_id = %s",
                (hashed_password, user_id)
            )
    
    @classmethod
    def register(cls, username, password):
        """Register a new user with a hashed password."""
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id",
                (username, hashed_password)
            )
            user_id = cursor.fetchone()[0]
            return cls(user_id=user_id, username=username)
    
    def get_poules(self):
        """Get all poules that the user is a member of."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT poules.poule_id, poules.poule_name, poules.year
                FROM user_poule
                JOIN poules ON user_poule.poule_id = poules.poule_id
                WHERE user_poule.user_id = %s
                ORDER BY poules.year DESC, poules.poule_name
            """, (self.user_id,))
            return cursor.fetchall()
    
    def join_poule(self, poule_name):
        """Join a poule by name."""
        with get_db_cursor(commit=True) as cursor:
            # Get poule ID
            cursor.execute("SELECT poule_id FROM poules WHERE poule_name = %s", (poule_name,))
            poule_id = cursor.fetchone()
            
            if poule_id:
                # Add user to poule
                cursor.execute(
                    "INSERT INTO user_poule (user_id, poule_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (self.user_id, poule_id[0])
                )
                return True
            return False 