import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

from core.config import RuntimeConfig
from simulation.scheduler import DailyScheduler
from core.llm_client import LLMClient

def check_status():
    print("🔍 DIAGNOSTIC: Checking AI Content Generation Status\n")
    
    # 1. Check Environment Variables
    print("1. Environment Variables:")
    load_dotenv(project_root / ".env")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"   ✅ LLM_API_KEY found: {masked_key}")
    else:
        print("   ❌ LLM_API_KEY NOT found in environment.")

    # 2. Check Content Config
    print("\n2. Content Configuration:")
    config_path = project_root / "config" / "content_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                mode = data.get("content_mode", "unknown")
                print(f"   ✅ content_mode: {mode}")
                if mode != "ai":
                     print("   ⚠️  WARNING: content_mode should be 'ai'")
        except Exception as e:
            print(f"   ❌ Failed to read content_config.json: {e}")
    else:
        print("   ❌ content_config.json NOT found.")

    # 3. Check Runtime Configuration (Simulation Instantiation)
    print("\n3. Simulation Runtime Config:")
    
    # Initialize Scheduler (this is what run_simulation.py does)
    try:
        scheduler = DailyScheduler(data_dir=str(project_root / "data"))
        
        # Manually trigger init logic to see what config gets
        # Note: We simulate what scheduler.initialize() does for config
        
        # Load env vars explicitly as DailyScheduler might fail to without python-dotenv in code
        config = RuntimeConfig(
             mode="simulation",
             ai_api_key=api_key if api_key else ""
        )
        
        print(f"   RuntimeConfig ai_api_key set: {'Yes' if config.ai_api_key else 'No'}")
        
        # Check LLM Client Init
        from core.llm_client import LLMConfig
        llm_config = LLMConfig(
            provider=config.ai_provider,
            api_key=config.ai_api_key
        )
        
        if config.ai_api_key:
            client = LLMClient(llm_config)
            if client.client:
                 print("   ✅ LLMClient initialized successfully.")
                 print("   ✅ AI Generation should work if prompt logic is correct.")
            else:
                 print("   ❌ LLMClient failed to create internal client.")
        else:
             print("   ❌ RuntimeConfig has no API Key -> LLMClient will be None -> Fallback to Templates.")

    except Exception as e:
        print(f"   ❌ Error initializing scheduler: {e}")

    print("\n==================================================")
    print("CONCLUSION:")
    if not api_key:
        print("❌ CRITICAL: Missing LLM_API_KEY environment variable.")
        print("   -> Content defaulted to English templates because AI client could not initialize.")
        print("\n   FIX:")
        print("   1. Create a file named '.env' in: c:\\Users\\pc\\Desktop\\core\\universe_2200")
        print("   2. Add the following line to it:")
        print("      LLM_API_KEY=your_api_key_here")
        print("   3. Run this script again to verify.")
    elif config.ai_api_key:
        print("✅ Configuration looks correct. Next step: Check actual generation logs.")
        print("   -> Try running 'python verify_ai_content.py' without mock to test connectivity.")
    else:
        print("⚠️  API Key exists in env but not passed to RuntimeConfig.")

if __name__ == "__main__":
    check_status()
