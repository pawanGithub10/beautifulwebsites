"""
Flask Example Application

Demonstrates integration of AI features with Flask framework.
"""

from flask import Flask, request, jsonify, render_template_string
from functools import wraps
import asyncio
import sys
import os
import logging

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from ai_core.application.AIEngine import AIEngine, AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.product_description.plugin import ProductDescriptionPlugin
from ai_features.review_response.plugin import ReviewResponsePlugin
from ai_features.social_calendar.plugin import SocialCalendarPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize AI components (global)
ai_engine = None
product_plugin = None
review_plugin = None
calendar_plugin = None


def initialize_ai():
    """Initialize AI engine and plugins"""
    global ai_engine, product_plugin, review_plugin, calendar_plugin

    logger.info("🚀 Initializing AI Platform...")

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️  OPENAI_API_KEY not set. Using mock provider.")

    # Create provider
    provider = OpenAIProvider(api_key=api_key)

    # Build AI engine
    builder = AIEngineBuilder()
    builder.with_provider(provider)
    builder.with_cache_enabled(os.getenv("ENABLE_CACHE", "false").lower() == "true")
    ai_engine = builder.build()

    # Initialize plugins
    product_plugin = ProductDescriptionPlugin(ai_engine=ai_engine)
    review_plugin = ReviewResponsePlugin(ai_engine=ai_engine)
    calendar_plugin = SocialCalendarPlugin(ai_engine=ai_engine)

    logger.info("✅ AI Platform initialized successfully!")


# Initialize on startup
initialize_ai()


# ============================================================================
# DECORATORS
# ============================================================================

def async_route(f):
    """Decorator to run async functions in Flask"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return decorated_function


def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": "Validation Error", "detail": str(e)}), 400
        except PermissionError as e:
            return jsonify({"error": "Permission Denied", "detail": str(e)}), 403
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500
    return decorated_function


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def home():
    """Landing page"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask AI API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .feature {
                background: #f0f7ff;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 10px;
                margin: 5px 0;
                font-family: monospace;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Flask AI API</h1>
            <p>AI-powered features integrated with Flask</p>

            <h2>Available Features:</h2>

            <div class="feature">
                <h3>📝 Product Description Generator</h3>
                <div class="endpoint">POST /api/product/description</div>
            </div>

            <div class="feature">
                <h3>💬 Review Response Generator</h3>
                <div class="endpoint">POST /api/review/respond</div>
            </div>

            <div class="feature">
                <h3>📱 Social Media Calendar</h3>
                <div class="endpoint">POST /api/social/calendar</div>
                <div class="endpoint">POST /api/social/post</div>
            </div>

            <h3>System Endpoints:</h3>
            <div class="endpoint">GET /health</div>
            <div class="endpoint">GET /stats</div>
        </div>
    </body>
    </html>
    """)


@app.route('/health')
@async_route
@handle_errors
async def health():
    """Health check endpoint"""
    if ai_engine is None:
        return jsonify({"status": "unhealthy", "detail": "AI engine not initialized"}), 503

    provider_healthy = await ai_engine.provider.check_health()

    return jsonify({
        "status": "healthy" if provider_healthy else "degraded",
        "ai_provider": ai_engine.provider.__class__.__name__.replace("Provider", ""),
        "provider_healthy": provider_healthy,
        "cache_enabled": ai_engine.enable_cache
    })


@app.route('/stats')
def stats():
    """System statistics"""
    if ai_engine is None:
        return jsonify({"error": "AI engine not initialized"}), 503

    return jsonify({
        "system": {
            "status": "operational",
            "framework": "Flask",
            "version": "1.0.0"
        },
        "provider": {
            "name": ai_engine.provider.__class__.__name__.replace("Provider", ""),
            "pricing": ai_engine.provider.get_pricing()
        },
        "features": {
            "cache_enabled": ai_engine.enable_cache
        }
    })


# ============================================================================
# PRODUCT DESCRIPTION ROUTES
# ============================================================================

@app.route('/api/product/description', methods=['POST'])
@async_route
@handle_errors
async def generate_product_description():
    """Generate product description"""
    data = request.get_json()

    # Validate required fields
    if not data.get('product_name'):
        raise ValueError("product_name is required")
    if not data.get('features'):
        raise ValueError("features is required")

    # Build product data
    product_data = {
        "name": data['product_name'],
        "features": ", ".join(data['features'])
    }
    if data.get('price'):
        product_data["price"] = data['price']
    if data.get('target_audience'):
        product_data["target_audience"] = data['target_audience']

    # Generate description
    result = await product_plugin.generate_description(
        product_data=product_data,
        category=data.get('category'),
        tone=data.get('tone', 'professional'),
        length=data.get('length', 'medium'),
        site_id=data.get('site_id'),
        model=data.get('model', 'gpt-4')
    )

    return jsonify(result)


# ============================================================================
# REVIEW RESPONSE ROUTES
# ============================================================================

@app.route('/api/review/respond', methods=['POST'])
@async_route
@handle_errors
async def generate_review_response():
    """Generate review response"""
    data = request.get_json()

    # Validate required fields
    if not data.get('review_text'):
        raise ValueError("review_text is required")
    if not data.get('rating'):
        raise ValueError("rating is required")
    if not data.get('business_name'):
        raise ValueError("business_name is required")

    # Validate rating
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")

    # Build review data
    review_data = {
        "review_text": data['review_text'],
        "rating": rating
    }
    if data.get('reviewer_name'):
        review_data["reviewer_name"] = data['reviewer_name']
    if data.get('platform'):
        review_data["platform"] = data['platform']

    # Generate response
    result = await review_plugin.generate_response(
        review_data=review_data,
        business_name=data['business_name'],
        business_type=data.get('business_type'),
        site_id=data.get('site_id'),
        model=data.get('model', 'gpt-4')
    )

    return jsonify(result)


@app.route('/api/review/analyze', methods=['POST'])
@async_route
@handle_errors
async def analyze_review():
    """Analyze review sentiment"""
    data = request.get_json()

    if not data.get('review_text'):
        raise ValueError("review_text is required")
    if not data.get('rating'):
        raise ValueError("rating is required")

    result = await review_plugin.analyze_sentiment(
        review_text=data['review_text'],
        rating=int(data['rating'])
    )

    return jsonify(result)


# ============================================================================
# SOCIAL CALENDAR ROUTES
# ============================================================================

@app.route('/api/social/calendar', methods=['POST'])
@async_route
@handle_errors
async def generate_social_calendar():
    """Generate social media calendar"""
    data = request.get_json()

    # Validate required fields
    if not data.get('month'):
        raise ValueError("month is required")
    if not data.get('business_type'):
        raise ValueError("business_type is required")
    if not data.get('brand_voice'):
        raise ValueError("brand_voice is required")

    # Build business context
    business_context = {
        "business_type": data['business_type'],
        "brand_voice": data['brand_voice']
    }
    if data.get('target_audience'):
        business_context["target_audience"] = data['target_audience']

    # Generate calendar
    result = await calendar_plugin.generate_calendar(
        month=data['month'],
        business_context=business_context,
        posts_per_week=data.get('posts_per_week', 5),
        themes=data.get('themes'),
        products_to_feature=data.get('products_to_feature'),
        site_id=data.get('site_id'),
        model=data.get('model', 'gpt-4')
    )

    return jsonify(result)


@app.route('/api/social/post', methods=['POST'])
@async_route
@handle_errors
async def generate_social_post():
    """Generate single social post"""
    data = request.get_json()

    # Validate required fields
    if not data.get('topic'):
        raise ValueError("topic is required")
    if not data.get('business_type'):
        raise ValueError("business_type is required")
    if not data.get('brand_voice'):
        raise ValueError("brand_voice is required")

    # Build business context
    business_context = {
        "business_type": data['business_type'],
        "brand_voice": data['brand_voice']
    }

    # Generate post
    result = await calendar_plugin.generate_single_post(
        topic=data['topic'],
        business_context=business_context,
        post_type=data.get('post_type', 'promotional'),
        platforms=data.get('platforms', ['instagram', 'facebook']),
        site_id=data.get('site_id'),
        model=data.get('model', 'gpt-4')
    )

    return jsonify(result)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. API calls will use mock data.")

    print("\n🚀 Starting Flask AI API Server")
    print("=" * 60)
    print(f"📍 Server: http://localhost:5000")
    print(f"💚 Health: http://localhost:5000/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
