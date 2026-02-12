"""
Impact Pipeline for Universe 2200

Processes social media impact on world state.
Fetches comments and AI replies, then applies impact calculations.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("ImpactPipeline")


class ImpactPipeline:
    """
    Pipeline for processing social impact on world state.
    
    Responsibilities:
    - Fetch comments for affected posts
    - Fetch AI replies if available
    - Apply social impact to world state
    
    Does NOT generate replies (that's a separate pipeline).
    """
    
    def __init__(self,
                 social_impact_processor,
                 reply_manager,
                 comment_manager):
        """
        Initialize impact pipeline.
        
        Args:
            social_impact_processor: SocialImpactProcessor instance
            reply_manager: ReplyManager instance
            comment_manager: CommentManager instance
        """
        self.social_impact_processor = social_impact_processor
        self.reply_manager = reply_manager
        self.comment_manager = comment_manager
    
    def run(self,
            post_ids: List[str],
            world_state,
            posts: List[Dict]) -> None:
        """
        Execute impact pipeline for affected posts.
        
        Args:
            post_ids: List of post IDs that received activity
            world_state: WorldState object (will be modified in-place)
            posts: List of post dictionaries for context
        """
        if not post_ids:
            logger.debug("No posts to process for impact")
            return
        
        logger.info(f"Processing social impact for {len(post_ids)} posts")
        
        # Create a lookup map for posts
        posts_by_id = {p.get('id'): p for p in posts if 'id' in p}
        
        for post_id in post_ids:
            try:
                # 1. Fetch comments for this post
                comments = self.comment_manager.get_comments_for_post(post_id)
                
                if not comments:
                    logger.debug(f"No comments found for post {post_id}")
                    continue
                
                logger.debug(f"Found {len(comments)} comments for post {post_id}")
                
                # 2. Fetch AI reply if available
                ai_reply = self.reply_manager.get_reply(post_id)
                
                if ai_reply:
                    logger.debug(f"Found AI reply for post {post_id}")
                
                # 3. Get post data for context
                post_data = posts_by_id.get(post_id)
                
                if not post_data:
                    logger.warning(f"Post {post_id} not found in posts list, skipping impact")
                    continue
                
                # 4. Apply social impact
                # The processor modifies world_state in-place
                self.social_impact_processor.apply_impact(
                    post=post_data,
                    comments=comments,
                    ai_reply=ai_reply,
                    world_state=world_state
                )
                
                logger.debug(f"Applied social impact for post {post_id}")
                
            except Exception as e:
                # Log error but continue processing other posts
                logger.error(f"Error processing impact for post {post_id}: {e}", exc_info=True)
                continue
        
        logger.info("Social impact processing complete")
