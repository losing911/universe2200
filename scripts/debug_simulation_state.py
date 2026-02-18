
import sys
import json
import os
from pathlib import Path

# Fix path to import core modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.name_generator import NameGenerator
    from simulation.population_engine import PopulationEngine, UserProfile
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def check_codebase_state():
    print("🔍 DIAGNOSTIC: Checking Codebase State...")
    
    # Check NameGenerator
    print(f"   NameGenerator file: {NameGenerator.__module__}")
    try:
        sample = NameGenerator.generate_name()
        print(f"   Sample Name: {sample}")
        if 'gender' in sample:
            print("   ✅ NameGenerator has 'gender' logic.")
        else:
            print("   ❌ NameGenerator MISSING 'gender' logic.")
    except Exception as e:
        print(f"   ❌ NameGenerator Error: {e}")

    # Check PopulationEngine
    try:
        pe = PopulationEngine(size=1)
        user = pe.population[0]
        print(f"   Sample User: {user}")
        if hasattr(user, 'handle') and hasattr(user, 'gender'):
            print("   ✅ PopulationEngine generating 'handle' and 'gender'.")
        else:
            print("   ❌ PopulationEngine MISSING attributes.")
    except Exception as e:
        print(f"   ❌ PopulationEngine Error: {e}")

def check_persistence_state():
    print("\n🔍 DIAGNOSTIC: Checking Persistence State...")
    path = Path("data/social_users.json")
    if not path.exists():
        print("   ❌ data/social_users.json NOT FOUND.")
        return
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                print("   ⚠️  File is empty.")
                return
                
            first_user = list(data.values())[0]
            print(f"   File User [0]: {first_user}")
            
            if 'handle' in first_user and 'gender' in first_user:
                 print("   ✅ JSON file has valid schema.")
            else:
                 print("   ❌ JSON file has OLD schema (missing fields).")
                 
    except Exception as e:
        print(f"   ❌ Read Error: {e}")

if __name__ == "__main__":
    check_codebase_state()
    check_persistence_state()
