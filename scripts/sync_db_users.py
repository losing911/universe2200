
import json
import os
import pymysql
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.append(str(Path(__file__).parent.parent))

from core.config import RuntimeConfig

# Database Configuration (Load from .env or hardcode for now based on qbook/.env.local)
# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "qbook_db"),
    "cursorclass": pymysql.cursors.DictCursor
}

def load_simulation_users():
    """Load users from simulation JSON storage."""
    users_path = Path("data/social_users.json")
    if not users_path.exists():
        print(f"❌ Users file not found at {users_path}")
        return []
    
    with open(users_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # data is a dict of user_id -> user_obj
        return list(data.values())

def ensure_schema(connection):
    """Ensure the users table has required columns for simulation profiles."""
    with connection.cursor() as cursor:
        # Check if columns exist
        cursor.execute("DESCRIBE users")
        columns = [row['Field'] for row in cursor.fetchall()]
        
        alter_statements = []
        if 'display_name' not in columns:
            alter_statements.append("ADD COLUMN display_name VARCHAR(255)")
        if 'avatar' not in columns:
            alter_statements.append("ADD COLUMN avatar VARCHAR(255)")
        if 'bio' not in columns:
            alter_statements.append("ADD COLUMN bio TEXT")
        if 'is_bot' not in columns:
            alter_statements.append("ADD COLUMN is_bot BOOLEAN DEFAULT FALSE")
        if 'simulation_id' not in columns:
            alter_statements.append("ADD COLUMN simulation_id VARCHAR(50) UNIQUE")
        if 'gender' not in columns:
            alter_statements.append("ADD COLUMN gender VARCHAR(20) DEFAULT 'unknown'")

        for stmt in alter_statements:
            print(f"🔄 Applying schema update: {stmt}")
            cursor.execute(f"ALTER TABLE users {stmt}")
        
    connection.commit()

def sync_users():
    print("🚀 Starting User Sync...")
    
    # 1. Load Simulation Users
    sim_users = load_simulation_users()
    print(f"📦 Loaded {len(sim_users)} users from simulation.")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Connected to Database.")
        
        # 2. Update Schema
        ensure_schema(connection)
        
        # 3. Upsert Users
        with connection.cursor() as cursor:
            count = 0
            for user in sim_users:
                # Map simulation user to DB schema
                # user_id -> simulation_id
                # handle (@foo) -> username (foo)
                # display_name -> display_name
                # avatar -> avatar
                
                handle = user.get("handle", "").replace("@", "")
                if not handle: continue
                
                sim_id = user.get("id")
                display_name = user.get("display_name", handle)
                avatar = user.get("avatar", "")
                bio = f"Role: {user.get('role', 'Citizen')} | Faction: {user.get('faction', 'Neutral')}"
                
                # SQL Upsert
                sql = """
                INSERT INTO users (username, password_hash, role, display_name, avatar, bio, is_bot, simulation_id, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    avatar = VALUES(avatar),
                    bio = VALUES(bio),
                    gender = VALUES(gender),
                    simulation_id = VALUES(simulation_id)
                """
                
                # Default password for bots (they can't login anyway effectively, or we give them dummy hash)
                # Using a dummy bcrypt hash or empty string
                dummy_hash = "$2b$12$eXgZy..." 
                
                cursor.execute(sql, (
                    handle, 
                    dummy_hash, 
                    "bot", 
                    display_name, 
                    avatar, 
                    bio, 
                    True, 
                    sim_id,
                    user.get("gender", "unknown")
                ))
                count += 1
                
                if count % 100 == 0:
                    print(f"   Processed {count} users...")
                    connection.commit()
            
            connection.commit()
            print(f"✅ Successfully synced {count} users to MySQL.")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    sync_users()
