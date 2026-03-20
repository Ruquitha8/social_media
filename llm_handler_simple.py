"""
Simple LLM Handler for Groq
Direct API calls with fallback model retry on decommission.
"""

import json
import re
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config_simple import (
    GROQ_API_KEY,
    PRIMARY_MODEL,
    FALLBACK_MODELS,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
)


class LLMHandler:
    """Simple LLM handler for generating social media content."""

    def __init__(self):
        """Initialize with primary model."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")

        self.api_key = GROQ_API_KEY
        self.current_model = PRIMARY_MODEL
        self.llm = self._init_client(self.current_model)

    def _init_client(self, model_name: str):
        """Initialize ChatGroq client with given model."""
        return ChatGroq(
            model_name=model_name,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            groq_api_key=self.api_key,
        )

    def _try_with_fallback(self, messages: List[Any]) -> Any:
        """Try invoking LLM; if model decommissioned, retry with fallbacks."""
        try:
            return self.llm.invoke(messages)
        except Exception as e:
            error_msg = str(e).lower()
            if "decommission" in error_msg or "model_decommissioned" in error_msg:
                print(f"⚠️  Model {self.current_model} decommissioned. Trying fallbacks...")
                for fallback in FALLBACK_MODELS:
                    if fallback == self.current_model:
                        continue
                    try:
                        print(f"🔄 Switching to {fallback}...")
                        self.llm = self._init_client(fallback)
                        self.current_model = fallback
                        result = self.llm.invoke(messages)
                        print(f"✅ Success with {fallback}")
                        return result
                    except Exception as inner_e:
                        print(f"⚠️  Fallback {fallback} failed: {inner_e}")
            raise

    def generate_post(
        self,
        product_name: str,
        product_description: str,
        platform: str,
        tone: str,
        content_type: str,
        additional_context: str = "",
    ) -> Dict[str, Any]:
        """Generate social media post content."""
        system_prompt = f"""You are an expert social media content creator specializing in e-commerce.
Generate high-quality, engaging social media content for {platform}.

Return ONLY valid JSON with these exact keys:
- caption: Main post text
- hashtags: List of hashtags (no # symbol)
- ad_copy: Short promotional text (50 words max)
- description: Product description (200 words max)"""

        user_prompt = f"""Generate content for:
Product: {product_name}
Description: {product_description}
Tone: {tone}
Content Type: {content_type}"""

        if additional_context:
            user_prompt += f"\nContext: {additional_context}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self._try_with_fallback(messages)
            content = response.content
            return self._parse_json(content)
        except Exception as e:
            raise Exception(f"Failed to generate post: {e}")

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        try:
            # Try to find JSON in the response
            match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
            if match:
                json_str = match.group()
            else:
                json_str = text

            parsed = json.loads(json_str)

            # Ensure required keys
            defaults = {
                "caption": "",
                "hashtags": [],
                "ad_copy": "",
                "description": "",
            }
            for key in defaults:
                if key not in parsed:
                    parsed[key] = defaults[key]

            # Convert hashtags to list if string
            if isinstance(parsed.get("hashtags"), str):
                parsed["hashtags"] = [h.strip() for h in parsed["hashtags"].split(",")]

            return parsed
        except json.JSONDecodeError:
            # Fallback: return text as description
            return {
                "caption": text[:500],
                "hashtags": [],
                "ad_copy": "",
                "description": text,
            }
