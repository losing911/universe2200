"""
Activity Pipeline for Universe 2200

Orchestrates population activity generation and persistence.
Handles comment saving and social network registration.
"""

import logging
from typing import List, Dict, Any, Optional
from core.tick_context import TickContext

logger = logging.getLogger("ActivityPipeline")


class ActivityPipeline:
    """
    Pipeline for processing population activity.
    
    Responsibilities:
    - Generate daily activity from PopulationEngine
    - Save comments via CommentManager
    - Register activity with SocialNetwork
    - Track affected posts
    
    Does NOT modify world state (that's handled elsewhere).
    """
    
    def __init__(self, 
                 population_engine,
                 comment_manager,
                 social_network=None):
        """
        Initialize activity pipeline.
        
        Args:
            population_engine: PopulationEngine instance
            comment_manager: CommentManager instance
            social_network: Optional SocialNetworkCore instance
        """
        self.population_engine = population_engine
        self.comment_manager = comment_manager
        self.social_network = social_network
        
    def run(self, 
            tick_context: TickContext,
            world_state_dict: Dict[str, Any],
            posts: List[Dict]) -> List[str]:
        """
        Execute activity pipeline for one tick.
        
        Args:
            tick_context: Tick context with deterministic seed
            world_state_dict: Current world state as dictionary
            posts: Available posts for interaction
            
        Returns:
            List of post IDs that received activity
        """
        affected_post_ids = set()
        
        logger.debug(f"Running activity pipeline for tick {tick_context.tick_number}")
        
        # 1. Generate population activity (deterministic via tick_seed)
        activity = self.population_engine.generate_daily_activity(
            world_state_dict, 
            posts, 
            tick_seed=tick_context.tick_seed
        )
        
        logger.info(f"Generated {len(activity)} actions for tick {tick_context.tick_number}")
        
        # 2. Process each action
        for action in activity:
            action_type = action.get('type', 'unknown')
            
            # Track which posts were affected
            if 'post_id' in action:
                affected_post_ids.add(action['post_id'])
            
            # 3. Save comments via CommentManager
            if action_type == 'comment':
                # CommentManager.add_comment expects (post_id, user_handle, content)
                self.comment_manager.add_comment(
                    post_id=action.get('post_id'),
                    user_handle=action.get('user_id'),  # user_id serves as handle
                    content=action.get('content')
                )
                logger.debug(f"Saved comment on post {action.get('post_id')}")
            
            # 4. Register with social network
            if self.social_network:
                if action_type == 'create_post':
                    if hasattr(self.social_network, 'register_post'):
                        # Add author_id to post data
                        post_data = {
                            'author_id': action.get('user_id'),
                            'content': action.get('content'),
                            'category': action.get('category'),
                            'timestamp': action.get('timestamp', 'now')
                        }
                        self.social_network.register_post(post_data)
                        logger.debug(f"Registered post by {action.get('user_id')}")
                
                elif action_type == 'comment':
                    if hasattr(self.social_network, 'register_comment'):
                        self.social_network.register_comment(action)
                
                elif action_type == 'reaction':
                    if hasattr(self.social_network, 'register_reaction'):
                        self.social_network.register_reaction(action)
                
                elif action_type == 'repost':
                    if hasattr(self.social_network, 'register_repost'):
                        self.social_network.register_repost(action)
        
        affected_list = list(affected_post_ids)
        logger.info(f"Affected {len(affected_list)} posts")
        
        return affected_list
