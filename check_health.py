"""
Universe 2200 - System Health Check
Run this script to verify that all simulation engines are generating data.
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/public")

def check_file(filename, description):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"❌ {description}: MISSING ({filename})")
        return False
    
    try:
        mtime = path.stat().st_mtime
        age = time.time() - mtime
        
        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine status based on age (Process A runs every second)
        # If age is > 10s, something might be stuck or slow
        status = "✅" if age < 10 else "⚠️" if age < 60 else "❌"
        
        print(f"{status} {description}:")
        print(f"   • File Age: {age:.1f}s ago")
        
        if isinstance(data, dict):
            ts = data.get('timestamp', 'N/A')
            tick = data.get('tick', 'N/A')
            print(f"   • Tick: {tick} ({ts})")
            
            # Context specific checks
            if 'data' in data:
                content = data['data']
                if isinstance(content, list):
                    print(f"   • Count: {len(content)} items")
                    if len(content) > 0 and 'type' in content[0]: 
                         print(f"   • Sample: {content[0]['type']}")
                elif isinstance(content, dict):
                     print(f"   • Metrics: {', '.join(list(content.keys())[:3])}...")
        
        print("")
        return True
    except Exception as e:
        print(f"❌ {description}: Error reading file ({e})\n")
        return False

def main():
    print(f"\n🔍 Universe 2200 Health Check\n   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Data Dir: " + str(DATA_DIR.absolute()) + "\n")
    
    if not DATA_DIR.exists():
        print(f"❌ Data Directory {DATA_DIR} not found!")
        return

    print("-" * 40)
    check_file("public_metrics.json", "Simulation Engine (Metrics)")
    check_file("public_news.json", "Content Pipeline (News)")
    check_file("public_social_x.json", "Social Engine (X Platform)")
    check_file("public_social_insta.json", "Social Engine (Insta Platform)")
    print("-" * 40)
    print("Legend: ✅=Healthy (<10s)  ⚠️=Lagging (<60s)  ❌=Stalled/Missing")

if __name__ == "__main__":
    main()
