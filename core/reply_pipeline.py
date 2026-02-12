"""
Reply Pipeline for Universe 2200

Generates AI replies to posts with comments.
Handles reply generation and persistence.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("ReplyPipeline")


class ReplyPipeline:
    """
    Pipeline for generating AI replies to social media posts.
    
    Responsibilities:
    - Check for posts with comments that need replies
    - Generate AI replies using reply_generator
    - Save replies via reply_manager
    - Track which posts received replies
    
    Does NOT modify world state (that's ImpactPipeline's job).
    """
    
    def __init__(self,
                 reply_generator,
                 reply_manager,
                 comment_manager):
        """
        Initialize reply pipeline.
        
        Args:
            reply_generator: SocialReplyGenerator instance
            reply_manager: ReplyManager instance
            comment_manager: CommentManager instance
        """
        self.reply_generator = reply_generator
        self.reply_manager = reply_manager
        self.comment_manager = comment_manager
    
    def run(self,
            post_ids: List[str],
            posts: List[Dict],
            world_state_dict: Dict[str, Any]) -> List[str]:
        """
        Execute reply pipeline for affected posts.
        
        Args:
            post_ids: List of post IDs that received activity
            posts: List of post dictionaries for context
            world_state_dict: Current world state as dictionary
            
        Returns:
            List of post IDs where replies were generated
        """
        if not post_ids:
            logger.debug("No posts to process for replies")
            return []
        
        logger.info(f"Processing reply generation for {len(post_ids)} posts")
        
        # Create lookup map for posts
        posts_by_id = {p.get('id'): p for p in posts if 'id' in p}
        
        replied_posts = []
        
        for post_id in post_ids:
            try:
                # 1. Check if comments exist
                comments = self.comment_manager.get_comments_for_post(post_id)
                
                if not comments:
                    logger.debug(f"No comments for post {post_id}, skipping reply")
                    continue
                
                # 2. Check if reply already exists
                existing_reply = self.reply_manager.get_reply(post_id)
                
                if existing_reply:
                    logger.debug(f"Reply already exists for post {post_id}, skipping")
                    continue
                
                # 3. Get post data
                post_data = posts_by_id.get(post_id)
                
                if not post_data:
                    logger.warning(f"Post {post_id} not found in posts list, skipping")
                    continue
                
                logger.debug(f"Generating reply for post {post_id} ({len(comments)} comments)")
                
                # 4. Generate reply
                # Reply generator is deterministic based on content, not random
                ai_reply = self.reply_generator.generate_reply(
                    post=post_data,
                    comments=comments,
                    world_state=world_state_dict,
                    narrative_memory=None  # Future: pass memory context
                )
                
                if not ai_reply:
                    logger.debug(f"No reply generated for post {post_id}")
                    continue
                
                # 5. Save reply
                self.reply_manager.save_reply(post_id, ai_reply)
                replied_posts.append(post_id)
                
                logger.debug(f"Reply saved for post {post_id}")
                
            except Exception as e:
                # Log error but continue processing other posts
                logger.error(f"Error generating reply for post {post_id}: {e}", exc_info=True)
                continue
        
        logger.info(f"Generated {len(replied_posts)} new replies")
        
        return replied_posts
