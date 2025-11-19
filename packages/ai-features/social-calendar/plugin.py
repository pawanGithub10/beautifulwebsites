"""
Social Media Content Calendar Generator Plugin

AI-powered 30-day social media content calendar with platform variations.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json

from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest, PromptContext

logger = logging.getLogger(__name__)


class SocialCalendarPlugin:
    """
    Social Media Content Calendar Generator Plugin.

    Features:
    - 30-day content calendar generation
    - Content mix (40% promo, 30% edu, 20% engage, 10% testimonial)
    - Platform variations (Instagram, Facebook, Twitter, LinkedIn)
    - Hashtag research and suggestions
    - Image prompts for each post
    - Optimal timing recommendations
    - Theme-based content planning

    Example:
        plugin = SocialCalendarPlugin(ai_engine=engine)

        result = await plugin.generate_calendar(
            month="2025-02",
            business_context={
                "business_type": "salon",
                "brand_voice": "friendly",
                "target_audience": "women 25-45"
            }
        )

        print(f"Generated {len(result['posts'])} posts")
    """

    def __init__(self, ai_engine: AIEngine):
        """
        Initialize plugin.

        Args:
            ai_engine: Configured AIEngine instance
        """
        self.ai_engine = ai_engine
        self.prompts = self._load_prompts()

        # Content mix ratios
        self.content_mix = {
            "promotional": 0.40,    # 40% - Products, offers, sales
            "educational": 0.30,    # 30% - Tips, how-tos, guides
            "engagement": 0.20,     # 20% - Questions, polls, UGC
            "testimonial": 0.10     # 10% - Reviews, success stories
        }

        logger.info("Social Calendar Plugin initialized")

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from YAML files."""
        prompts = {}
        prompts_dir = Path(__file__).parent / "prompts"

        if prompts_dir.exists():
            for yaml_file in prompts_dir.glob("*.yaml"):
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        prompts[data['name']] = data['template']
                except Exception as e:
                    logger.warning(f"Failed to load prompt {yaml_file}: {e}")

        if not prompts:
            prompts["calendar"] = self._get_default_prompt()

        return prompts

    def _get_default_prompt(self) -> str:
        """Get default calendar generation prompt."""
        return """Generate a {posts_count}-post social media content calendar for {month}.

Business Context:
- Type: {business_type}
- Brand Voice: {brand_voice}
- Target Audience: {target_audience}
- Key Themes: {key_themes}

Content Mix:
- 40% Promotional (products, offers, sales)
- 30% Educational (tips, how-tos, industry insights)
- 20% Engagement (questions, polls, user content)
- 10% Testimonial (reviews, success stories, UGC)

Requirements:
1. Create {posts_count} posts distributed throughout {month}
2. Follow the content mix above
3. Include varied posting times (morning, afternoon, evening)
4. Each post should have:
   - Engaging text (150-200 chars for Instagram)
   - 3-5 relevant hashtags
   - Image description/prompt
   - Post category
   - Best time to post

Output ONLY valid JSON array:
[
  {{
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "post_text": "...",
    "hashtags": ["tag1", "tag2", "tag3"],
    "image_prompt": "...",
    "category": "promotional|educational|engagement|testimonial"
  }}
]"""

    async def generate_calendar(
        self,
        month: str,
        business_context: Dict[str, Any],
        posts_per_week: int = 5,
        themes: Optional[List[str]] = None,
        products_to_feature: Optional[List[Dict]] = None,
        site_id: Optional[str] = None,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate social media content calendar.

        Args:
            month: Target month (YYYY-MM)
            business_context: Business information dict with:
                - business_type: Type of business (required)
                - brand_voice: Brand voice/tone (required)
                - target_audience: Target demographic (optional)
            posts_per_week: Number of posts per week (default: 5)
            themes: Key themes to cover (optional)
            products_to_feature: Products to promote (optional)
            site_id: Site ID for tracking (optional)
            model: AI model to use

        Returns:
            Dict with:
                - calendar_id: Generated calendar ID
                - month: Target month
                - total_posts: Number of posts
                - posts: List of post dicts
                - tokens_used: Token count

        Raises:
            ValueError: If required context is missing
        """
        # Validate input
        if not business_context.get("business_type"):
            raise ValueError("business_type is required")
        if not business_context.get("brand_voice"):
            raise ValueError("brand_voice is required")

        # Calculate posts needed
        # Approximately 4 weeks per month
        total_posts = posts_per_week * 4

        # Build themes string
        if not themes:
            themes = ["industry trends", "seasonal content", "customer stories"]
        themes_str = ", ".join(themes)

        # Build products string
        products_str = "no specific products"
        if products_to_feature:
            products_str = ", ".join([p.get("name", "") for p in products_to_feature[:3]])

        # Build prompt
        prompt_template = self.prompts.get("calendar", self._get_default_prompt())

        prompt = prompt_template.format(
            posts_count=total_posts,
            month=month,
            business_type=business_context.get("business_type"),
            brand_voice=business_context.get("brand_voice"),
            target_audience=business_context.get("target_audience", "general audience"),
            key_themes=themes_str
        )

        # Add products context if provided
        if products_to_feature:
            prompt += f"\n\nProducts to feature: {products_str}"

        # Create AI request
        request = AIRequest(
            prompt=prompt,
            system_prompt="You are a social media marketing expert. Output ONLY valid JSON array, no markdown.",
            model=model,
            temperature=0.8,  # Higher creativity for social content
            max_tokens=3000,  # Longer for full calendar
            response_format="json"
        )

        # Generate with tracking
        context = PromptContext(
            variables=business_context,
            site_id=site_id,
            feature="social_calendar"
        )

        logger.info(f"Generating {total_posts}-post calendar for {month}")

        response = await self.ai_engine.generate(request, context)

        # Parse JSON response
        try:
            posts = json.loads(response.content)

            # Validate and enhance posts
            enhanced_posts = []
            for i, post in enumerate(posts):
                # Ensure required fields
                post.setdefault("date", self._calculate_date(month, i, total_posts))
                post.setdefault("time", self._suggest_time(i))
                post.setdefault("category", self._assign_category(i, total_posts))

                enhanced_posts.append(post)

            calendar_id = f"cal_{month}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            result = {
                "calendar_id": calendar_id,
                "month": month,
                "business_type": business_context.get("business_type"),
                "total_posts": len(enhanced_posts),
                "posts": enhanced_posts,
                "tokens_used": response.tokens_used,
                "model": response.model,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Generated calendar with {len(enhanced_posts)} posts ({response.tokens_used} tokens)")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")

            # Fallback: create simple calendar
            return {
                "calendar_id": f"cal_{month}_fallback",
                "month": month,
                "total_posts": 0,
                "posts": [],
                "tokens_used": response.tokens_used,
                "error": "JSON parse failed"
            }

    async def generate_single_post(
        self,
        topic: str,
        business_context: Dict[str, Any],
        post_type: str = "promotional",
        platforms: Optional[List[str]] = None,
        site_id: Optional[str] = None,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate a single social media post.

        Args:
            topic: Post topic/theme
            business_context: Business information
            post_type: Type of post (promotional, educational, etc.)
            platforms: Target platforms (Instagram, Facebook, etc.)
            site_id: Site ID for tracking
            model: AI model to use

        Returns:
            Post dict with platform variations
        """
        if not platforms:
            platforms = ["instagram", "facebook"]

        prompt = f"""Generate a {post_type} social media post about: {topic}

Business: {business_context.get('business_type')}
Brand Voice: {business_context.get('brand_voice')}

Create versions for: {', '.join(platforms)}

Include:
- Engaging text (optimized for each platform)
- 3-5 hashtags
- Image description
- Call-to-action

Output JSON:
{{
  "main_text": "...",
  "hashtags": [...],
  "image_prompt": "...",
  "platforms": {{
    "instagram": {{"text": "...", "hashtags": [...]}},
    "facebook": {{"text": "...", "hashtags": [...]}}
  }}
}}"""

        request = AIRequest(
            prompt=prompt,
            system_prompt="You are a social media expert. Output ONLY valid JSON.",
            model=model,
            temperature=0.8,
            max_tokens=800,
            response_format="json"
        )

        context = PromptContext(
            variables={"topic": topic},
            site_id=site_id,
            feature="social_post"
        )

        response = await self.ai_engine.generate(request, context)

        try:
            result = json.loads(response.content)
            result["tokens_used"] = response.tokens_used
            result["topic"] = topic
            result["post_type"] = post_type

            return result

        except json.JSONDecodeError:
            return {
                "main_text": response.content,
                "hashtags": [],
                "image_prompt": "",
                "tokens_used": response.tokens_used,
                "error": "JSON parse failed"
            }

    def _calculate_date(self, month: str, index: int, total: int) -> str:
        """Calculate post date based on index."""
        year, month_num = month.split("-")
        start_date = datetime(int(year), int(month_num), 1)

        # Spread posts evenly throughout month
        days_in_month = 30  # Approximate
        day_increment = days_in_month / total

        post_date = start_date + timedelta(days=int(index * day_increment))

        return post_date.strftime("%Y-%m-%d")

    def _suggest_time(self, index: int) -> str:
        """Suggest optimal posting time."""
        # Vary times throughout the day
        times = ["09:00", "12:00", "15:00", "18:00", "20:00"]
        return times[index % len(times)]

    def _assign_category(self, index: int, total: int) -> str:
        """Assign category based on content mix."""
        position = index / total

        if position < 0.40:
            return "promotional"
        elif position < 0.70:
            return "educational"
        elif position < 0.90:
            return "engagement"
        else:
            return "testimonial"
