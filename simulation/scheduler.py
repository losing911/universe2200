from datetime import datetime
from typing import Optional, Dict, Any

from core.world import WorldManager
from core.config import RuntimeConfig
from core.llm_client import LLMClient, LLMConfig
from core.universe_runtime import UniverseRuntime
from core.activity_pipeline import ActivityPipeline
from core.reply_pipeline import ReplyPipeline
from core.impact_pipeline import ImpactPipeline
from core.content_pipeline import ContentPipeline
from simulation.population_engine import PopulationEngine
from simulation.social_network_core import SocialNetworkCore
from simulation.influence_engine import InfluenceEngine
from simulation.ai_reaction_engine import AIReactionEngine
from simulation.event_scheduler import EventScheduler
from content.social_impact import SocialImpactProcessor
from content.social_interaction import CommentManager, ReplyManager, SocialReplyGenerator
from content.social_media_generator import SocialMediaGenerator
from content.drama_engine import DramaEngine

class DailyScheduler:
    """
    Scheduler for running daily simulation ticks using the modern UniverseRuntime.
    Orchestrates the new engines: Population, Social Network, Influence, AI.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the scheduler.
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = data_dir if data_dir is not None else "data"
        self.is_initialized = False
        
        # Components
        self.world_manager = None
        self.runtime = None
        self.social_network = None
        
    def initialize(self):
        """Initialize the UniverseRuntime and all dependencies."""
        if self.is_initialized:
            return
            
        print("⚙️  Initializing Universe 2200 Engines...")
        
        # 1. World State
        self.world_manager = WorldManager(self.data_dir)
        self.world_manager.load_world()
        
        # 2. Persistent Components
        self.social_network = SocialNetworkCore(self.data_dir)
        comment_manager = CommentManager(self.data_dir)
        reply_manager = ReplyManager(self.data_dir)
        
        # 3. Engines
        population_engine = PopulationEngine(size=1000)  # Default size
        
        # Ingest population into Social Network
        print("   Population ingested into Social Network.")
        self.social_network.ingest_population(population_engine.population)
        
        social_impact_processor = SocialImpactProcessor()
        reply_generator = SocialReplyGenerator()
        influence_engine = InfluenceEngine()
        ai_reaction_engine = AIReactionEngine()
        event_scheduler = EventScheduler()
        
        # 4. Create Pipelines
        activity_pipeline = ActivityPipeline(
            population_engine=population_engine,
            comment_manager=comment_manager,
            social_network=self.social_network
        )
        
        reply_pipeline = ReplyPipeline(
            reply_generator=reply_generator,
            reply_manager=reply_manager,
            comment_manager=comment_manager
        )
        
        impact_pipeline = ImpactPipeline(
            social_impact_processor=social_impact_processor,
            reply_manager=reply_manager,
            comment_manager=comment_manager
        )
        
        content_pipeline = ContentPipeline()
        
        # 5. Create RuntimeConfig
        config = RuntimeConfig(
            mode="simulation",
            tick_interval_seconds=0,  # We run manually
            base_seed=42,
            enable_ai_replies=True,
            enable_social_impact=True,
            enable_real_users=False
        )
        
        # 5.5 Initialize LLM Client
        llm_config = LLMConfig(
            provider=config.ai_provider,
            api_key=config.ai_api_key,
            base_url=config.ai_base_url,
            model=config.ai_model
        )
        llm_client = LLMClient(llm_config) if config.ai_api_key or config.ai_base_url else None
        
        # Re-initialize ContentPipeline with LLM Client
        content_pipeline = ContentPipeline(llm_client=llm_client)
        
        # Initialize SocialMediaGenerator with LLM Client
        social_generator = SocialMediaGenerator(llm_client=llm_client)
        
        # Initialize DramaEngine
        drama_engine = DramaEngine(self.social_network)
        
        self.runtime = UniverseRuntime(
            config=config,
            world_state=self.world_manager.state,
            activity_pipeline=activity_pipeline,
            reply_pipeline=reply_pipeline,
            impact_pipeline=impact_pipeline,
            content_pipeline=content_pipeline,
            social_network=self.social_network,
            influence_engine=influence_engine,
            ai_reaction_engine=ai_reaction_engine,
            drama_engine=drama_engine,
            event_scheduler=event_scheduler,
            social_generator=social_generator
        )
        
        self.is_initialized = True
        print(f"🌍 Simulation initialized at {self.world_manager.state.current_date}")
    
    def run_daily_tick(self):
        """
        Execute a single daily tick.
        """
        if not self.is_initialized:
            self.initialize()
        
        # 1. Run Runtime Tick (Behavior, Events, Impact)
        content_data = self.runtime.run_tick()
        
        # 2. End of Day Processing
        # Cleanup social network (viral calculation, clamping)
        self.social_network.end_of_day_cleanup()
        
        # 3. Advance Date
        self.world_manager.state.advance_date(days=1)
        
        # 4. Persist State
        self.world_manager.save_world()
        
        return {
            "date": self.world_manager.state.current_date,
            "tick": self.runtime.tick_count,
            "content": content_data 
        }
    
    def run_for_days(self, num_days: int):
        """
        Run simulation for specified number of days.
        """
        if not self.is_initialized:
            self.initialize()
            
        print(f"🚀 Running simulation for {num_days} days...")
        
        for i in range(num_days):
            self.run_daily_tick()
            
        print("✅ Simulation complete.")
        
    def get_current_state(self):
        """Get current state summary."""
        if not self.is_initialized:
            self.initialize()
            
        return {
            "date": self.world_manager.state.current_date,
            "num_events": len(self.world_manager.events.events), # Legacy check
            "metrics": {
                "public_unrest": self.world_manager.state.public_unrest,
                "information_noise": self.world_manager.state.information_noise,
                "media_trust": self.world_manager.state.media_trust
            }
        }
