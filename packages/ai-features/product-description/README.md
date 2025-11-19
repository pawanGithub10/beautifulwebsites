# Product Description Generator Plugin

AI-powered product description generator with category-specific prompts.

## Features

- ✅ Category-specific prompts (grocery, electronics, fashion, general)
- ✅ Tone control (professional, casual, luxury, playful)
- ✅ Length control (short, medium, long)
- ✅ SEO optimization (title, meta description, tags)
- ✅ JSON structured output
- ✅ Batch generation support
- ✅ Cost estimation
- ✅ Token tracking

## Installation

```bash
pip install ai-platform-core ai-platform-openai pyyaml
```

## Quick Start

```python
from ai_features.product_description import ProductDescriptionPlugin
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

# Setup
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider)
plugin = ProductDescriptionPlugin(ai_engine=engine)

# Generate description
result = await plugin.generate_description(
    product_data={
        "name": "Organic Green Tea 100g",
        "category": "Beverages",
        "price": 299,
        "features": ["organic", "antioxidant-rich", "imported"],
        "currency": "INR"
    },
    category="grocery",  # Use grocery-specific prompt
    tone="professional",
    length="medium"
)

print(result["description"])
print(result["meta_title"])
print(result["tags"])
```

## Output Format

```json
{
  "description": "Discover the pure essence of nature with our Organic Green Tea...",
  "short_description": "Premium organic green tea with rich antioxidants",
  "meta_title": "Organic Green Tea 100g - Antioxidant Rich | YourStore",
  "meta_description": "Buy premium organic green tea 100g. Rich in antioxidants...",
  "tags": ["organic", "green tea", "health", "antioxidants", "beverages"],
  "tokens_used": 450,
  "model": "gpt-4",
  "tone": "professional",
  "length": "medium"
}
```

## Categories

### General (base)
For any product. Balanced approach.

```python
result = await plugin.generate_description(
    product_data={...},
    category="base"  # or None
)
```

### Grocery
Emphasizes freshness, health benefits, quality, origin.

```python
result = await plugin.generate_description(
    product_data={...},
    category="grocery"
)
```

### Electronics
Focuses on specs, compatibility, innovation, performance.

```python
result = await plugin.generate_description(
    product_data={...},
    category="electronics"
)
```

### Fashion
Highlights style, material, fit, occasions, comfort.

```python
result = await plugin.generate_description(
    product_data={...},
    category="fashion"
)
```

## Tone Options

- **professional** - Formal, trustworthy
- **casual** - Friendly, conversational
- **luxury** - Premium, exclusive
- **playful** - Fun, energetic

```python
result = await plugin.generate_description(
    product_data={...},
    tone="luxury"
)
```

## Length Options

- **short** - 50-100 words
- **medium** - 150-250 words (recommended)
- **long** - 300-500 words

```python
result = await plugin.generate_description(
    product_data={...},
    length="long"
)
```

## Batch Generation

Generate descriptions for multiple products:

```python
products = [
    {"name": "Organic Tea", "price": 299, ...},
    {"name": "Premium Coffee", "price": 499, ...},
    {"name": "Herbal Mix", "price": 199, ...}
]

results = await plugin.generate_batch(
    products=products,
    category="grocery",
    tone="professional"
)

for result in results:
    print(f"{result['product_name']}: {result['success']}")
```

## Cost Estimation

Estimate cost before generating:

```python
cost = await plugin.estimate_cost(
    product_data={
        "name": "Product Name",
        "category": "Electronics",
        ...
    },
    category="electronics",
    model="gpt-4"
)

print(f"Estimated cost: ${cost:.4f}")
```

## Custom Prompts

Add your own category prompts:

1. Create `prompts/custom.yaml`:

```yaml
name: custom_description
category: custom
description: Custom product category

template: |
  You are an expert copywriter for {category} products.

  Product: {product_name}
  Price: {price} {currency}
  Features: {features}

  Generate a {tone} description ({length} length).

  Output JSON:
  {{
    "description": "...",
    "short_description": "...",
    "meta_title": "...",
    "meta_description": "...",
    "tags": [...]
  }}
```

2. Use it:

```python
result = await plugin.generate_description(
    product_data={...},
    category="custom"
)
```

## Integration with Storefront Service

```python
# domain-services/storefront-service/app/ai.py
from ai_features.product_description import ProductDescriptionPlugin
from ai_core import container

# Initialize once
product_plugin = ProductDescriptionPlugin(ai_engine=container.get_engine())

# Use in routes
@router.post("/products/{id}/ai-description")
async def generate_description(id: str):
    product = await get_product(id)

    result = await product_plugin.generate_description(
        product_data={
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "features": product.features
        },
        site_id=product.site_id
    )

    # Update product in database
    await update_product_description(id, result["description"])

    return result
```

## A/B Testing

Generate multiple versions:

```python
versions = []

for tone in ["professional", "casual", "luxury"]:
    result = await plugin.generate_description(
        product_data={...},
        tone=tone
    )
    versions.append(result)

# Test which converts better
```

## Performance

- **Time**: 1-2 seconds per description (with API call)
- **Cache hit**: <10ms (instant)
- **Cost**: ~$0.02-0.04 per description (GPT-4)
- **Cost**: ~$0.001-0.002 per description (GPT-3.5)

## Best Practices

1. **Use GPT-3.5 for bulk generation** - 20x cheaper
2. **Use category-specific prompts** - Better quality
3. **Enable caching** - Reduce costs by 30-50%
4. **Batch similar products** - More efficient
5. **Track usage** - Monitor costs per site

## Examples

### E-commerce Store

```python
# Generate for all products
products = await get_all_products()

results = await plugin.generate_batch(
    products=products,
    category="grocery",
    tone="professional",
    site_id="store-123"
)

# Update database
for result in results:
    if result["success"]:
        await update_product(result)
```

### New Product Addition

```python
@router.post("/products")
async def create_product(product: ProductCreate):
    # Create product
    new_product = await db.create_product(product)

    # Auto-generate description
    if product.auto_generate_description:
        description = await product_plugin.generate_description(
            product_data=product.dict(),
            site_id=product.site_id
        )

        new_product.description = description["description"]
        await db.update_product(new_product)

    return new_product
```

## Pricing

Based on OpenAI pricing:

- **GPT-4**: $0.03 per 1K tokens (~$0.02-0.04 per description)
- **GPT-3.5**: $0.001 per 1K tokens (~$0.001-0.002 per description)

Monthly costs:
- 100 products: $2-4 (GPT-4) or $0.10-0.20 (GPT-3.5)
- 1000 products: $20-40 (GPT-4) or $1-2 (GPT-3.5)
