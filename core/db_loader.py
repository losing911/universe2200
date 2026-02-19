
import os
import pymysql
from typing import List, Dict
import logging

logger = logging.getLogger("DBLoader")

class DBLoader:
    """
    Fetches real users from the MySQL database to be used in the simulation.
    """
    
    def __init__(self):
        # Load config from env
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "qbook_db"),
            "cursorclass": pymysql.cursors.DictCursor
        }
        
    def fetch_users(self) -> List[Dict]:
        """
        Fetch all users from MySQL.
        Returns a list of dicts compatible with SocialMediaGenerator.
        """
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # Select users who are NOT bots (or all users? Let's get all for now, maybe filter bots if we want only 'real' humans)
                # Actually, if we want the DB users to be active, we should fetch them.
                # Assuming 'is_bot' might be used to distinguish system bots from user accounts if we added it.
                # For now, let's fetch everyone who has a handle.
                
                sql = "SELECT id, handle, display_name, avatar, role, faction, bio FROM users"
                cursor.execute(sql)
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    users.append({
                        "id": row["id"],
                        "handle": row["handle"],
                        "display_name": row["display_name"],
                        "avatar": row["avatar"],
                        "role": row["role"] or "citizen",
                        "faction": row["faction"] or "Neutral",
                        "traits": ["Real User"], # Marker trait
                        "bio": row["bio"]
                    })
                
                logger.debug(f"Fetched {len(users)} users from DB.")
                return users
                
        except Exception as e:
            logger.error(f"Failed to fetch users from DB: {e}")
            return []
        finally:
            if 'connection' in locals() and connection.open:
                connection.close()
