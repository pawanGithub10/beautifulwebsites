"""
Review Response Generator Plugin

AI-powered review response generator with sentiment analysis.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json

from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest, PromptContext

logger = logging.getLogger(__name__)


class ReviewResponsePlugin:
    """
    Review Response Generator Plugin.

    Features:
    - Sentiment analysis (positive, neutral, negative)
    - Tone-matched responses
    - Personalization (business name, reviewer name)
    - Issue identification and addressing
    - Batch response generation
    - Multi-language support

    Example:
        plugin = ReviewResponsePlugin(ai_engine=engine)

        result = await plugin.generate_response(
            review_data={
                "rating": 5,
                "reviewer_name": "Sarah",
                "review_text": "Amazing service! Staff was incredibly helpful..."
            },
            business_name="Green Valley Salon"
        )

        print(result["response_text"])
    """

    def __init__(self, ai_engine: AIEngine):
        """
        Initialize plugin.

        Args:
            ai_engine: Configured AIEngine instance
        """
        self.ai_engine = ai_engine
        self.prompts = self._load_prompts()

        logger.info("Review Response Plugin initialized")

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

        # Fallback prompts
        if not prompts:
            prompts.update(self._get_default_prompts())

        return prompts

    def _get_default_prompts(self) -> Dict[str, str]:
        """Get default prompt templates."""
        return {
            "positive": """Generate a warm, grateful response to this positive review.

Review: {review_text}
Rating: {rating}/5
Reviewer: {reviewer_name}
Business: {business_name}

Guidelines:
1. Express genuine gratitude
2. Mention specific details from their review
3. Reinforce what they loved
4. Invite them back
5. Keep it personal but professional
6. Max 100 words

Output JSON:
{{
  "response_text": "...",
  "tone": "grateful",
  "sentiment": "positive"
}}""",

            "negative": """Generate an empathetic, solution-focused response to this negative review.

Review: {review_text}
Rating: {rating}/5
Reviewer: {reviewer_name}
Business: {business_name}

Guidelines:
1. Acknowledge their frustration
2. Apologize sincerely
3. Address specific issues mentioned
4. Offer a solution or next steps
5. Provide contact info
6. Keep it professional and caring
7. Max 150 words

Output JSON:
{{
  "response_text": "...",
  "tone": "apologetic",
  "sentiment": "negative",
  "issues_addressed": [...]
}}"""
        }

    async def analyze_sentiment(
        self,
        review_text: str,
        rating: int
    ) -> Dict[str, Any]:
        """
        Analyze review sentiment.

        Args:
            review_text: Review text
            rating: Star rating (1-5)

        Returns:
            Sentiment analysis dict
        """
        # Simple rule-based sentiment (can be enhanced with AI)
        if rating >= 4:
            sentiment = "positive"
            score = 0.8
        elif rating == 3:
            sentiment = "neutral"
            score = 0.5
        else:
            sentiment = "negative"
            score = 0.2

        # Extract keywords
        keywords = []
        positive_words = ["great", "amazing", "excellent", "wonderful", "fantastic", "love", "best"]
        negative_words = ["bad", "poor", "terrible", "worst", "awful", "horrible", "disappointed"]

        text_lower = review_text.lower()

        for word in positive_words:
            if word in text_lower:
                keywords.append(word)

        for word in negative_words:
            if word in text_lower:
                keywords.append(word)

        return {
            "sentiment": sentiment,
            "score": score,
            "keywords": keywords[:5],  # Top 5
            "rating": rating
        }

    async def generate_response(
        self,
        review_data: Dict[str, Any],
        business_name: str,
        owner_name: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        site_id: Optional[str] = None,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate AI review response.

        Args:
            review_data: Review information dict with:
                - rating: Star rating 1-5 (required)
                - review_text: Review content (required)
                - reviewer_name: Reviewer's name (optional)
                - reviewed_at: Review date (optional)
            business_name: Business name
            owner_name: Owner/manager name for signature (optional)
            custom_instructions: Additional instructions (optional)
            site_id: Site ID for tracking (optional)
            model: AI model to use

        Returns:
            Dict with:
                - response_text: Generated response
                - sentiment: Review sentiment (positive/neutral/negative)
                - tone: Response tone
                - issues_addressed: List of issues (if negative)
                - tokens_used: Token count

        Raises:
            ValueError: If required review data is missing
        """
        # Validate input
        if not review_data.get("rating"):
            raise ValueError("Review rating is required")
        if not review_data.get("review_text"):
            raise ValueError("Review text is required")

        # Analyze sentiment
        sentiment_analysis = await self.analyze_sentiment(
            review_text=review_data["review_text"],
            rating=review_data["rating"]
        )

        # Select prompt based on sentiment
        if sentiment_analysis["sentiment"] == "positive":
            prompt_key = "positive"
        elif sentiment_analysis["sentiment"] == "negative":
            prompt_key = "negative"
        else:
            prompt_key = "neutral"

        # Fallback to positive if prompt not found
        if prompt_key not in self.prompts:
            prompt_key = "positive"

        prompt_template = self.prompts[prompt_key]

        # Build prompt
        prompt = prompt_template.format(
            review_text=review_data["review_text"],
            rating=review_data["rating"],
            reviewer_name=review_data.get("reviewer_name", "valued customer"),
            business_name=business_name
        )

        # Add custom instructions
        if custom_instructions:
            prompt += f"\n\nAdditional instructions: {custom_instructions}"

        # Create AI request
        request = AIRequest(
            prompt=prompt,
            system_prompt="You are a professional customer service representative. Output ONLY valid JSON.",
            model=model,
            temperature=0.7,
            max_tokens=400,
            response_format="json"
        )

        # Generate with tracking
        context = PromptContext(
            variables=review_data,
            site_id=site_id,
            feature="review_response"
        )

        logger.info(f"Generating response for {sentiment_analysis['sentiment']} review (rating: {review_data['rating']})")

        response = await self.ai_engine.generate(request, context)

        # Parse JSON response
        try:
            result = json.loads(response.content)

            # Add metadata
            result["sentiment"] = sentiment_analysis["sentiment"]
            result["sentiment_score"] = sentiment_analysis["score"]
            result["keywords"] = sentiment_analysis["keywords"]
            result["tokens_used"] = response.tokens_used
            result["model"] = response.model

            # Add signature if owner name provided
            if owner_name:
                result["response_text"] += f"\n\n{owner_name}\n{business_name}"

            logger.info(f"Generated {sentiment_analysis['sentiment']} response ({response.tokens_used} tokens)")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")

            # Fallback
            return {
                "response_text": response.content,
                "sentiment": sentiment_analysis["sentiment"],
                "tone": "professional",
                "tokens_used": response.tokens_used,
                "model": response.model,
                "error": "JSON parse failed"
            }

    async def generate_batch(
        self,
        reviews: list[Dict[str, Any]],
        business_name: str,
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        Generate responses for multiple reviews.

        Args:
            reviews: List of review data dicts
            business_name: Business name
            **kwargs: Additional arguments for generate_response

        Returns:
            List of result dicts
        """
        results = []

        logger.info(f"Batch generating responses for {len(reviews)} reviews")

        for review_data in reviews:
            try:
                result = await self.generate_response(
                    review_data=review_data,
                    business_name=business_name,
                    **kwargs
                )
                result["review_id"] = review_data.get("review_id")
                result["success"] = True
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to generate response: {e}")
                results.append({
                    "review_id": review_data.get("review_id"),
                    "success": False,
                    "error": str(e)
                })

        success_count = sum(1 for r in results if r.get("success"))
        logger.info(f"Batch complete: {success_count}/{len(reviews)} successful")

        return results

    async def get_pending_reviews(
        self,
        reviews: list[Dict[str, Any]],
        filter_sentiment: Optional[list[str]] = None,
        limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Filter pending reviews for response generation.

        Args:
            reviews: List of all reviews
            filter_sentiment: Filter by sentiment (["positive", "negative"])
            limit: Maximum reviews to return

        Returns:
            Filtered list of reviews
        """
        filtered = []

        for review in reviews:
            # Analyze sentiment
            sentiment = await self.analyze_sentiment(
                review_text=review.get("review_text", ""),
                rating=review.get("rating", 3)
            )

            # Apply filters
            if filter_sentiment and sentiment["sentiment"] not in filter_sentiment:
                continue

            review["sentiment"] = sentiment["sentiment"]
            filtered.append(review)

            if len(filtered) >= limit:
                break

        return filtered
