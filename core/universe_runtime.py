"""
Universe 2200 Runtime

Refactored execution engine using pipeline architecture.
Orchestrates ActivityPipeline, ReplyPipeline, and ImpactPipeline.
"""

import time
import threading
import logging
from typing import Optional
from datetime import datetime

from core.config import RuntimeConfig
from core.tick_context import TickContext
from core.activity_pipeline import ActivityPipeline
from core.reply_pipeline import ReplyPipeline
from core.impact_pipeline import ImpactPipeline
from core.content_pipeline import ContentPipeline

# Configure logging
logger = logging.getLogger("UniverseRuntime")


class UniverseRuntime:
    """
    Main execution engine for Universe 2200.
    
    Uses pipeline architecture for clean separation of responsibilities:
    - ActivityPipeline: Generate and save population activity
    - ReplyPipeline: Generate AI replies to posts
    - ImpactPipeline: Process social impact on world state
    """
    
    def __init__(self,
                 config: RuntimeConfig,
                 world_state,
                 activity_pipeline: ActivityPipeline,
                 reply_pipeline: ReplyPipeline,
                 impact_pipeline: ImpactPipeline,
                 content_pipeline=None,
                 social_network=None,
                 influence_engine=None,
                 ai_reaction_engine=None,
                 drama_engine=None,
                 event_scheduler=None,
                 social_generator=None):
        """
        Initialize Universe Runtime.
        
        Args:
            config: RuntimeConfig with flags and settings
            world_state: WorldState instance
            activity_pipeline: ActivityPipeline instance
            reply_pipeline: ReplyPipeline instance
            impact_pipeline: ImpactPipeline instance
            content_pipeline: Optional[ContentPipeline] = None,
            social_network: Optional SocialNetworkCore
            influence_engine: Optional InfluenceEngine
            ai_reaction_engine: Optional AIReactionEngine
            event_scheduler: Optional EventScheduler
        """
        # Validate config
        config.validate()
        
        self.config = config
        self.world_state = world_state
        
        # Core Pipelines
        self.activity_pipeline = activity_pipeline
        self.reply_pipeline = reply_pipeline
        self.impact_pipeline = impact_pipeline
        self.content_pipeline = content_pipeline
        
        # Optional Components
        self.social_network = social_network
        self.influence_engine = influence_engine
        self.ai_reaction_engine = ai_reaction_engine
        self.drama_engine = drama_engine # New Drama Component
        self.event_scheduler = event_scheduler
        self.social_generator = social_generator # New component for feed generation
        
        # Runtime State
        self.running = False
        self.tick_count = 0
        self.thread = None
        
        # Delayed/Emergent Event Queue
        self.delayed_events = []
        
        logger.info(f"UniverseRuntime initialized in {config.mode} mode")
    
    def start(self):
        """Start the runtime in a background thread."""
        if self.running:
            logger.warning("Runtime already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Runtime started")
    
    def stop(self):
        """Stop the runtime."""
        if not self.running:
            logger.warning("Runtime not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Runtime stopped")
    
    def _loop(self):
        """Main execution loop."""
        while self.running:
            try:
                self.run_tick()
                time.sleep(self.config.tick_interval_seconds)
            except Exception as e:
                logger.error(f"Error in runtime loop: {e}", exc_info=True)
                # Continue running despite errors
    
    def run_tick(self):
        """Execute a single simulation tick."""
        self.tick_count += 1
        
        logger.debug(f"Starting tick {self.tick_count}")
        
        # 0. Process delayed events
        self._process_delayed_events()
        
        # 1. Create TickContext (deterministic seed)
        tick_ctx = TickContext(
            base_seed=self.config.base_seed,
            tick_number=self.tick_count,
            mode=self.config.mode
        )
        
        # 2. Fetch posts for activity generation
        posts = self._fetch_posts()
        world_state_dict = self.world_state.to_dict()
        
        # 3. Run ActivityPipeline (always runs)
        logger.debug("Running ActivityPipeline")
        affected_post_ids = self.activity_pipeline.run(
            tick_context=tick_ctx,
            world_state_dict=world_state_dict,
            posts=posts
        )
        
        # 4. Run ReplyPipeline (if enabled)
        if self.config.enable_ai_replies:
            logger.debug("Running ReplyPipeline")
            replied_post_ids = self.reply_pipeline.run(
                post_ids=affected_post_ids,
                posts=posts,
                world_state_dict=world_state_dict
            )
            logger.debug(f"Generated {len(replied_post_ids)} AI replies")
        
        # 5. Run ImpactPipeline (if enabled)
        if self.config.enable_social_impact:
            logger.debug("Running ImpactPipeline")
            self.impact_pipeline.run(
                post_ids=affected_post_ids,
                world_state=self.world_state,
                posts=posts
            )
        
        # 6. Process AI Reactions (if engine available)
        if self.ai_reaction_engine:
            self._process_ai_reactions(affected_post_ids, posts, world_state_dict)
        
        # 7. Check and trigger events (if scheduler available)
        if self.event_scheduler:
            self._process_events()
        
        # 8. Update influence scores (if engine available)
        if self.influence_engine:
            self._update_influence_scores(world_state_dict)
        
        # 9. Clamp world state metrics
        self._clamp_metrics()
        
        # 10. Run Content Pipeline (Broadcast)
        # This replaces the simple print summary in future steps, 
        # but for now we run it and print the headline/news.
        if self.content_pipeline:
            logger.debug("Running ContentPipeline")
            content_output = self.content_pipeline.run(
                tick_context=tick_ctx,
                world_state=self.world_state,
                recent_posts=posts
            )
            
            # Run Drama Engine
            if self.drama_engine:
                drama_events = self.drama_engine.generate_events(self.tick_count)
                if drama_events:
                     # Inject drama into news or separate field
                     # For now, let's treat them as "Social News" or append to news
                     for de in drama_events:
                         content_output["news"].append({
                             "title": f"Drama: {de['type'].title()}",
                             "summary": de["content"],
                             "type": "social_drama",
                             "timestamp": datetime.now().isoformat()
                         })
                     content_output["drama"] = drama_events
            
            # Print Dystopian Broadcast
            print("\n" + "="*50)
            print(f"📣 BROADCAST (Tick {self.tick_count})")
            print(f"Headline: {content_output['headline']}")
            
            if content_output['news']:
                print("\n📰 Latest News:")
                for article in content_output['news'][:2]: # Show top 2
                    print(f"  • {article['title']}")
                    
            if content_output['events_detected']:
                print(f"\n⚠️  Events: {', '.join(content_output['events_detected'])}")
            
            print("="*50 + "\n")
            
            # Return content output for external use (UI/API)
            return content_output
            
        logger.debug(f"Completed tick {self.tick_count}")
        return {}
    
    def _process_delayed_events(self):
        """Process delayed events scheduled for this tick."""
        remaining_events = []
        for event in self.delayed_events:
            if event["execute_at"] == self.tick_count:
                if event["type"] == "echo_unrest":
                    self.world_state.apply_effect(
                        "delayed_echo",
                        {"public_unrest": 0.02}
                    )
                    logger.debug(f"Executed delayed event: {event['type']}")
            elif event["execute_at"] > self.tick_count:
                remaining_events.append(event)
        
        self.delayed_events = remaining_events
    
    def _fetch_posts(self):
        """Fetch recent posts from social network."""
        posts = []
        if self.social_network and hasattr(self.social_network, 'posts'):
            posts = self.social_network.posts[-self.config.max_posts_per_tick:]
        return posts
    
    def _process_ai_reactions(self, post_ids, posts, world_state_dict):
        """Process AI reactions to posts."""
        system_ai = {
            "id": "System_AI",
            "chaos_affinity": 0.1,
            "faction_loyalty": {"corporate": 1.0}
        }
        
        posts_by_id = {p.get('id'): p for p in posts if 'id' in p}
        
        for post_id in post_ids:
            post_obj = posts_by_id.get(post_id)
            if not post_obj:
                continue
            
            target_entity = {
                "id": post_obj.get("author_id", "unknown"),
                "influence_score": 5.0,
                "reputation_score": 0.0,
                "faction": post_obj.get("author_faction", "neutral")
            }
            
            reaction = self.ai_reaction_engine.decide_reaction(
                ai_entity=system_ai,
                target_entity=target_entity,
                post=post_obj,
                world_state=world_state_dict
            )
            
            if reaction:
                # Apply world deltas
                world_deltas = reaction.get("world_deltas", {})
                if world_deltas:
                    self.world_state.apply_effect(
                        f"AI Reaction: {reaction['reaction_type']}",
                        world_deltas
                    )
                
                # Log non-ignore reactions
                if reaction['reaction_type'] != "ignore":
                    print(f"  [AI] {reaction['reaction_type'].upper()} on post {post_id} "
                          f"(Reason: {reaction.get('reason')})")
    
    def _process_events(self):
        """Check and apply global events."""
        triggered = self.event_scheduler.check_for_events(self.tick_count)
        if triggered:
            for evt in triggered:
                print(f"!!! GLOBAL EVENT TRIGGERED: {evt['name']} !!!")
        
        # Apply active event effects
        self.event_scheduler.apply_event_effects(self.world_state)
    
    def _update_influence_scores(self, world_state_dict):
        """Update user influence scores based on activity."""
        # This is a placeholder for influence score updates
        # In practice, this would be handled by the ActivityPipeline
        # or a separate InfluencePipeline if needed
        pass
    
    def _clamp_metrics(self):
        """Clamp world state metrics to [0, 1] range."""
        metrics_to_clamp = [
            'public_unrest', 'media_trust', 'surveillance_level',
            'information_noise', 'ai_dependency', 'market_confidence'
        ]
        
        for metric in metrics_to_clamp:
            val = self.world_state.get_metric(metric)
            clamped = max(0.0, min(1.0, val))
            if val != clamped:
                setattr(self.world_state, metric, clamped)
                logger.debug(f"Clamped {metric}: {val:.3f} -> {clamped:.3f}")
    
    def _print_summary(self, activity_count):
        """Print tick summary."""
        print(f"--- Tick {self.tick_count} ---")
        print(f"Unrest: {self.world_state.public_unrest:.3f}")
        print(f"Noise:  {self.world_state.information_noise:.3f}")
        
        # Print top influencers
        if self.influence_engine and hasattr(self.activity_pipeline, 'population_engine'):
            population = self.activity_pipeline.population_engine.population
            sorted_users = sorted(
                population,
                key=lambda u: getattr(u, 'influence_score', 0),
                reverse=True
            )
            top_5 = sorted_users[:5]
            print("Top Influencers:")
            for u in top_5:
                score = getattr(u, 'influence_score', 0)
                print(f"  - {u.user_id}: {score:.1f}")
        
        if activity_count > 0:
            print(f"Activity: {activity_count} new actions")
