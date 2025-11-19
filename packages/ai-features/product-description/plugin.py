"""
Product Description Generator Plugin

AI-powered product description generator with category-specific prompts.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json

from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest, PromptContext

logger = logging.getLogger(__name__)


class ProductDescriptionPlugin:
    """
    Product Description Generator Plugin.

    Features:
    - Category-specific prompts (grocery, electronics, fashion, etc.)
    - Tone control (professional, casual, luxury, playful)
    - Length control (short, medium, long)
    - SEO optimization
    - JSON output with structured data
    - Batch generation support

    Example:
        plugin = ProductDescriptionPlugin(ai_engine=engine)

        result = await plugin.generate_description(
            product_data={
                "name": "Organic Green Tea",
                "category": "Beverages",
                "price": 299,
                "features": ["organic", "antioxidant-rich"]
            },
            tone="professional",
            length="medium"
        )

        print(result["description"])
    """

    def __init__(self, ai_engine: AIEngine):
        """
        Initialize plugin.

        Args:
            ai_engine: Configured AIEngine instance
        """
        self.ai_engine = ai_engine
        self.prompts = self._load_prompts()

        logger.info("Product Description Plugin initialized")

    def _load_prompts(self) -> Dict[str, str]:
        """
        Load prompt templates from YAML files.

        Returns:
            Dict of prompt templates
        """
        prompts = {}
        prompts_dir = Path(__file__).parent / "prompts"

        if prompts_dir.exists():
            for yaml_file in prompts_dir.glob("*.yaml"):
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        prompts[data['name']] = data['template']
                        logger.debug(f"Loaded prompt: {data['name']}")
                except Exception as e:
                    logger.warning(f"Failed to load prompt {yaml_file}: {e}")

        # Fallback base prompt if no files found
        if not prompts:
            prompts["base"] = self._get_default_prompt()

        return prompts

    def _get_default_prompt(self) -> str:
        """Get default prompt template."""
        return """You are an expert e-commerce copywriter. Generate a compelling product description.

Product Information:
- Name: {product_name}
- Category: {category}
- Price: {price} {currency}
- Key Features: {features}

Requirements:
1. Tone: {tone} (professional, casual, luxury, or playful)
2. Length: {length} (short: 50-100 words, medium: 150-250 words, long: 300-500 words)
3. Include SEO keywords naturally
4. Highlight benefits, not just features
5. Create urgency or desire
6. End with a call-to-action

Output ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "description": "Full product description here",
  "short_description": "1-2 sentence summary",
  "meta_title": "SEO-optimized title (max 60 chars)",
  "meta_description": "SEO meta description (max 160 chars)",
  "tags": ["tag1", "tag2", "tag3"]
}}"""

    async def generate_description(
        self,
        product_data: Dict[str, Any],
        category: Optional[str] = None,
        tone: str = "professional",
        length: str = "medium",
        site_id: Optional[str] = None,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate AI product description.

        Args:
            product_data: Product information dict with:
                - name: Product name (required)
                - category: Product category (optional)
                - price: Product price (optional)
                - features: List of features (optional)
                - currency: Price currency (default: INR)
            category: Prompt category to use (grocery, electronics, etc.)
            tone: Description tone (professional, casual, luxury, playful)
            length: Description length (short, medium, long)
            site_id: Site ID for tracking (optional)
            model: AI model to use

        Returns:
            Dict with:
                - description: Full product description
                - short_description: Brief summary
                - meta_title: SEO title
                - meta_description: SEO description
                - tags: List of tags
                - tokens_used: Token count
                - model: Model used

        Raises:
            ValueError: If required product data is missing
        """
        # Validate input
        if not product_data.get("name"):
            raise ValueError("Product name is required")

        # Select prompt template
        prompt_key = f"{category}_description" if category else "base"
        if prompt_key not in self.prompts:
            prompt_key = "base"

        prompt_template = self.prompts[prompt_key]

        # Build prompt
        features_str = ", ".join(product_data.get("features", []))
        currency = product_data.get("currency", "INR")

        prompt = prompt_template.format(
            product_name=product_data.get("name", ""),
            category=product_data.get("category", "General"),
            price=product_data.get("price", "Contact for price"),
            currency=currency,
            features=features_str or "high quality product",
            tone=tone,
            length=length
        )

        # Create AI request
        request = AIRequest(
            prompt=prompt,
            system_prompt="You are a professional e-commerce copywriter. Output ONLY valid JSON, no markdown formatting.",
            model=model,
            temperature=0.7,
            max_tokens=800,
            response_format="json"
        )

        # Generate with tracking
        context = PromptContext(
            variables=product_data,
            site_id=site_id,
            feature="product_description"
        )

        logger.info(f"Generating description for: {product_data.get('name')}")

        response = await self.ai_engine.generate(request, context)

        # Parse JSON response
        try:
            result = json.loads(response.content)

            # Add metadata
            result["tokens_used"] = response.tokens_used
            result["model"] = response.model
            result["tone"] = tone
            result["length"] = length

            logger.info(
                f"Generated description ({response.tokens_used} tokens, "
                f"model: {response.model})"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {response.content}")

            # Fallback: return raw text
            return {
                "description": response.content,
                "short_description": response.content[:200],
                "meta_title": product_data.get("name", "Product"),
                "meta_description": response.content[:160],
                "tags": [],
                "tokens_used": response.tokens_used,
                "model": response.model,
                "error": "JSON parse failed, returned raw text"
            }

    async def generate_batch(
        self,
        products: list[Dict[str, Any]],
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        Generate descriptions for multiple products.

        Args:
            products: List of product data dicts
            **kwargs: Additional arguments passed to generate_description

        Returns:
            List of result dicts
        """
        results = []

        logger.info(f"Batch generating descriptions for {len(products)} products")

        for product_data in products:
            try:
                result = await self.generate_description(
                    product_data=product_data,
                    **kwargs
                )
                result["product_name"] = product_data.get("name")
                result["success"] = True
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to generate for {product_data.get('name')}: {e}")
                results.append({
                    "product_name": product_data.get("name"),
                    "success": False,
                    "error": str(e)
                })

        success_count = sum(1 for r in results if r.get("success"))
        logger.info(f"Batch complete: {success_count}/{len(products)} successful")

        return results

    async def estimate_cost(
        self,
        product_data: Dict[str, Any],
        category: Optional[str] = None,
        model: str = "gpt-4"
    ) -> float:
        """
        Estimate cost for generating description.

        Args:
            product_data: Product information
            category: Prompt category
            model: Model to use

        Returns:
            Estimated cost in USD
        """
        # Build a sample prompt to estimate tokens
        prompt_key = f"{category}_description" if category else "base"
        if prompt_key not in self.prompts:
            prompt_key = "base"

        prompt_template = self.prompts[prompt_key]

        features_str = ", ".join(product_data.get("features", []))

        prompt = prompt_template.format(
            product_name=product_data.get("name", "Product"),
            category=product_data.get("category", "General"),
            price=product_data.get("price", "0"),
            currency="INR",
            features=features_str,
            tone="professional",
            length="medium"
        )

        # Estimate cost
        cost = await self.ai_engine.estimate_cost(prompt, model=model)

        return cost
