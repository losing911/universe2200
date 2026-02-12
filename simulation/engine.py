"""
Simulation Engine Module

Core tick-based simulation engine that coordinates world state evolution.
"""

from typing import List, Dict, Any
from datetime import datetime

from core.world import WorldManager
from core.events import Event
from core.narrative_memory import NarrativeMemory
from core.observer import MetaObserver
from simulation.rules import RuleEngine
from content.dispatcher import ContentDispatcher
from content.feedback import FeedbackAnalyzer
from content.social_interaction import CommentManager, ReplyManager, SocialReplyGenerator
from content.social_impact import SocialImpactProcessor


class SimulationEngine:
    """
    Main simulation engine that drives the universe evolution.
    
    Executes daily ticks:
    1. Load current world state
    2. Apply all simulation rules
    3. Generate events based on rules
    4. Update world state with changes
    5. Record events in narrative memory (passive)
    6. Generate content from events
    7. Apply content feedback to world state (feedback loop)
    8. **Process Social Impact (New)**
       - Analyze comments on posts
       - Generate AI replies
       - Apply social impact to world state
    9. Save updated state and events
    10. Advance date
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the simulation engine.
        
        Args:
            data_dir: Path to data directory (optional)
        """
        self.world = WorldManager(data_dir)
        self.rule_engine = RuleEngine()
        self.content_dispatcher = ContentDispatcher(data_dir)
        self.feedback_analyzer = FeedbackAnalyzer(enabled=True)
        self.narrative_memory = NarrativeMemory(data_dir)
        self.meta_observer = MetaObserver(data_dir)
        
        # Social Impact Layer
        self.comment_manager = CommentManager(data_dir)
        self.reply_manager = ReplyManager(data_dir)
        self.reply_generator = SocialReplyGenerator()
        self.impact_processor = SocialImpactProcessor()
        
        self.tick_count = 0
        
        # Track history for observer
        self.recent_state_history = []
        self.recent_events_history = []
    
    def initialize(self):
        """Initialize the simulation by loading world data."""
        self.world.load_world()
        print(f"🌍 Simulation initialized")
        print(f"📅 Start date: {self.world.state.current_date.strftime('%Y-%m-%d')}")
        print(f"📊 Initial state loaded")
        print()
    
    def tick(self) -> Dict[str, Any]:
        """
        Execute one simulation tick (one day).
        
        Returns:
            Summary dictionary with:
            - date: Current date
            - events_generated: List of events
            - metric_changes: Changes to world state
        """
        self.tick_count += 1
        
        # Store previous state for comparison
        previous_state = {
            'water_price_index': self.world.state.water_price_index,
            'public_unrest': self.world.state.public_unrest,
            'energy_price_index': self.world.state.energy_price_index,
            'media_trust': self.world.state.media_trust
        }
        
        # Apply all simulation rules
        new_events, metric_changes = self.rule_engine.apply_rules(self.world.state)
        
        # Apply metric changes to world state
        for metric_name, delta in metric_changes.items():
            self.world.state.modify_metric(metric_name, delta)
        
        # Add all generated events to event log
        for event in new_events:
            self.world.events.add_event(event)
        
        # Advance the date
        current_date = self.world.state.current_date
        self.world.state.advance_date(days=1)
        
        # Save updated world state
        self.world.save_world()
        
        # Generate content from new events (content trigger layer)
        if new_events:
            generated_content = self.content_dispatcher.process_and_save(new_events)
            
            # Record events in narrative memory (passive tracking)
            for event in new_events:
                self.narrative_memory.record_event(event)
            self.narrative_memory.save_memory()
            
            # Process Social Impact
            if generated_content:
                self._process_social_activity(generated_content)
        
        # Apply content feedback to world state (feedback loop)
        self._apply_content_feedback()
        
        # Track history for observer
        self.recent_state_history.append(self.world.state.to_dict())
        self.recent_events_history.extend(new_events)
        
        # Meta Observer Check (weekly)
        if self.tick_count > 0 and self.tick_count % 7 == 0:
            self._run_meta_observer()
        
        # Prepare summary
        summary = {
            'tick': self.tick_count,
            'date': current_date.strftime('%Y-%m-%d'),
            'events_generated': new_events,
            'metric_changes': metric_changes,
            'previous_state': previous_state,
            'current_state': {
                'water_price_index': self.world.state.water_price_index,
                'public_unrest': self.world.state.public_unrest,
                'energy_price_index': self.world.state.energy_price_index,
                'media_trust': self.world.state.media_trust
            }
        }
        
        return summary
    
    def _process_social_activity(self, content_items: List[Dict[str, Any]]):
        """
        Process social media posts, comments, and AI replies.
        Apply social impact to world state.
        
        Args:
            content_items: List of generated content items from dispatcher
        """
        for item in content_items:
            # Only process MindLink social posts
            if item.get("platform") != "MindLink" or item.get("content_type") != "social_post":
                continue
                
            # Construct a deterministic post ID since one might not exist in the item
            post_id = f"post_{item.get('event_id', 'unknown')}_{item.get('platform', 'mindlink')}"
            
            # Enhance item with ID for processing
            post_data = item.copy()
            post_data["id"] = post_id
            
            # 1. Retrieve Comments
            comments = self.comment_manager.get_comments_for_post(post_id)
            
            # 2. Generate AI Reply (if comments exist and no reply yet)
            ai_reply = self.reply_manager.get_reply(post_id)
            
            if comments and not ai_reply:
                # Generate new reply
                ai_reply = self.reply_generator.generate_reply(
                    post=post_data,
                    comments=comments,
                    world_state=self.world.state.to_dict(),
                    narrative_memory=None # Future: Pass memory
                )
                
                if ai_reply:
                    self.reply_manager.save_reply(post_id, ai_reply)
            
            # 3. Apply Social Impact using Processor
            # Note: We pass the WorldState object to be modified in-place
            self.impact_processor.apply_impact(
                post=post_data,
                comments=comments,
                ai_reply=ai_reply,
                world_state=self.world.state
            )
            
            # Save world state if changes occurred in the loop?
            # efficient to save once at end of tick, but apply_impact modifies in-place instantly.
            # We already save at end of tick, but apply_rules happened before content generation.
            # So creating a second save might be needed if we want these impacts persisted immediately for this day.
            # However, the next tick will load the state from memory (object) mostly? 
            # Actually tick() loads from self.world.state which is kept in memory.
            # But we should save eventually. tick() saves at step 9 (before content generation).
            # So we should probably save again if we changed things.
            self.world.save_world()

    def run_simulation(self, num_days: int = 30) -> List[Dict[str, Any]]:
        """
        Run the simulation for a specified number of days.
        
        Args:
            num_days: Number of days to simulate
            
        Returns:
            List of tick summaries
        """
        summaries = []
        
        print(f"⚙️  Running simulation for {num_days} days...")
        print("=" * 70)
        print()
        
        for day in range(num_days):
            summary = self.tick()
            summaries.append(summary)
            
            # Print summary for this tick
            self._print_tick_summary(summary)
        
        print()
        print("=" * 70)
        print(f"✅ Simulation complete after {num_days} days")
        print(f"📊 Total events generated: {len(self.world.events.events)}")
        
        return summaries
    
    def _print_tick_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary of a simulation tick."""
        print(f"📅 Day {summary['tick']}: {summary['date']}")
        
        # Print generated events
        if summary['events_generated']:
            print(f"   📰 Events generated: {len(summary['events_generated'])}")
            for event in summary['events_generated']:
                print(f"      • {event.type.upper()}: {event.description}")
                print(f"        Location: {event.location}, Scale: {event.scale:.2f}")
        else:
            print(f"   📰 No events generated")
        
        # Print significant metric changes
        if summary['metric_changes']:
            print(f"   📈 Metric changes:")
            for metric, delta in summary['metric_changes'].items():
                current = summary['current_state'].get(metric, 0)
                sign = "+" if delta > 0 else ""
                print(f"      • {metric}: {sign}{delta:.3f} → {current:.3f}")
        
        # Print key metrics
        state = summary['current_state']
        print(f"   🔍 Key metrics: Unrest={state['public_unrest']:.2f}, "
              f"Water=${state['water_price_index']:.2f}, "
              f"Media Trust={state['media_trust']:.2f}")
        
        print()
    
    def _apply_content_feedback(self):
        """
        Apply content feedback effects to world state.
        This creates the feedback loop: Content → World State.
        """
        if not self.feedback_analyzer.enabled:
            return
        
        # Load content queue
        self.content_dispatcher.load_content_queue()
        content_queue = self.content_dispatcher.content_queue
        
        if not content_queue:
            return
        
        # Apply feedback effects
        effects = self.feedback_analyzer.apply_feedback(content_queue, self.world.state)
        
        # Save updated state if effects were applied
        if effects:
            self.world.save_world()
        
        # Clear content queue after processing
        self.content_dispatcher.content_queue = []
        self.content_dispatcher.save_content_queue()
    
    def _run_meta_observer(self):
        """Run meta observer analysis and apply adjustments."""
        current_date = self.world.state.current_date
        
        # Run observation
        adjustments = self.meta_observer.observe(
            current_date,
            self.recent_events_history,
            self.recent_state_history
        )
        
        # Apply adjustments
        for adj in adjustments:
            self.rule_engine.apply_adjustment(adj)
            
        # Clear recent history after check
        self.recent_state_history = []
        self.recent_events_history = []

