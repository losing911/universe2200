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
    print(f"   Project Root: {project_root}")
    
    # 1. Check Environment Variables
    print("\n1. Environment Variables:")
    env_path = project_root / ".env"
    load_dotenv(env_path)
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if api_key:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"   ✅ LLM_API_KEY found: {masked_key}")
    else:
        print(f"   ❌ LLM_API_KEY NOT found in environment.")
        print(f"      Checked file: {env_path}")
        if not env_path.exists():
             print("      (File does not exist)")

    # 1.5 Check Provider Config
    print("\n1.5. Provider Configuration:")
    provider = os.getenv("AI_PROVIDER", "openai")
    base_url = os.getenv("AI_BASE_URL", "")
    print(f"   AI_PROVIDER: {provider}")
    print(f"   AI_BASE_URL: {base_url}")
    
    if provider == "openrouter":
        if not base_url:
            print("   ⚠️  AI_PROVIDER is 'openrouter' but AI_BASE_URL is not set.")
            print("       Iterally, it should be: https://openrouter.ai/api/v1")
            print("       (LLMClient might default to it, but explicit is better)")
            
    # 2. Check Content Config
    print("\n2. Content Configuration:")
    config_path = project_root / "config" / "content_config.json"
    print(f"   Checking config at: {config_path}")
    
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
        data_dir = project_root / "data"
        scheduler = DailyScheduler(data_dir=str(data_dir))
        
        # Manually trigger init logic to see what config gets
        # Note: We simulate what scheduler.initialize() does for config
        
        # Load env vars explicitly as DailyScheduler might fail to without python-dotenv in code
        config = RuntimeConfig(
             mode="simulation",
             ai_api_key=api_key if api_key else "",
             ai_provider=provider,
             ai_base_url=base_url
        )
        
        print(f"   RuntimeConfig ai_api_key set: {'Yes' if config.ai_api_key else 'No'}")
        print(f"   RuntimeConfig provider: {config.ai_provider}")
        
        # Check LLM Client Init
        from core.llm_client import LLMConfig
        llm_config = LLMConfig(
            provider=config.ai_provider,
            api_key=config.ai_api_key,
            base_url=config.ai_base_url,
            model=os.getenv("AI_MODEL", "gpt-4o-mini")
        )
        
        if config.ai_api_key:
            client = LLMClient(llm_config)
            if client.client:
                 print("   ✅ LLMClient initialized successfully.")
                 print(f"   ✅ Provider: {llm_config.provider}")
                 if llm_config.base_url:
                     print(f"   ✅ Base URL: {llm_config.base_url}")
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
        print(f"   1. Create a file named '.env' in: {project_root}")
        print("   2. Add the following lines to it:")
        print("      AI_PROVIDER=openrouter")
        print("      LLM_API_KEY=sk-or-your_key_here")
        print("      AI_BASE_URL=https://openrouter.ai/api/v1")
        print("      AI_MODEL=openai/gpt-4o-mini")
        print("   3. Run this script again to verify.")
    elif config.ai_api_key:
        print("✅ Configuration looks correct. Next step: Check actual generation logs.")
        print("   -> Try running 'python verify_ai_content.py' without mock to test connectivity.")
    else:
        print("⚠️  API Key exists in env but not passed to RuntimeConfig.")

if __name__ == "__main__":
    check_status()
