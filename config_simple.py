"""
Minimal configuration for Social Media Content Generator
API keys, model names, platform limits.
"""

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# =======================
# API KEYS
# =======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")   # ✅ Add this

# =======================
# LLM MODELS (Groq)
# =======================
PRIMARY_MODEL = "llama-3.1-8b-instant"

FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048

# =======================
# IMAGE GENERATION (HF Free)
# =======================
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
IMAGE_TIMEOUT = 120

# ======================
# PLATFORM CONFIGS
# =======================
PLATFORMS = {
    "instagram": {
        "name": "Instagram",
        "max_caption": 2200,
        "emoji_friendly": True,
    },
    "tiktok": {
        "name": "TikTok",
        "max_caption": 2200,
        "emoji_friendly": True,
    },
    "linkedin": {
        "name": "LinkedIn",
        "max_caption": 3000,
        "emoji_friendly": False,
    },
    "twitter": {
        "name": "Twitter/X",
        "max_caption": 280,
        "emoji_friendly": True,
    },
    "facebook": {
        "name": "Facebook",
        "max_caption": 63206,
        "emoji_friendly": True,
    },
}

TONES = ["casual", "professional", "humorous", "inspirational", "promotional"]
CONTENT_TYPES = ["product_highlight", "sales_promotion", "educational", "brand_story"]

# =======================
# STORAGE
# =======================
DATA_DIR = "data"
LOG_DIR = "logs"

# =======================
# APP
# =======================
APP_TITLE = "📱 Social Media Content Pack Generator"
APP_ICON = "📱"
print("HF KEY LOADED:", HF_API_KEY)