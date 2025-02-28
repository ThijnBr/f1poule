from app.database.connection import get_db_cursor

class Team:
    """Team model for F1 teams."""
    
    @classmethod
    def get_all(cls):
        """Get all teams."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT team_id, team_name FROM team ORDER BY team_name")
            return cursor.fetchall()
    
    @classmethod
    def create(cls, team_name):
        """Create a new team."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO team (team_name) VALUES (%s) RETURNING team_id",
                (team_name,)
            )
            return cursor.fetchone()[0]
            
    @classmethod
    def update(cls, team_id, team_name):
        """Update a team's name."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE team SET team_name = %s WHERE team_id = %s",
                (team_name, team_id)
            )
            
    @classmethod
    def delete(cls, team_id):
        """Delete a team if it has no associated drivers."""
        with get_db_cursor(commit=True) as cursor:
            # First check if team has any drivers
            cursor.execute("SELECT COUNT(*) FROM driver WHERE team_id = %s", (team_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete team with associated drivers")
                
            cursor.execute("DELETE FROM team WHERE team_id = %s", (team_id,))
            
    @classmethod
    def get_by_id(cls, team_id):
        """Get a team by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT team_id, team_name FROM team WHERE team_id = %s", (team_id,))
            return cursor.fetchone() 