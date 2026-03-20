"""
Intelligent Conversation Manager using LLM
Extracts product info from natural conversation, asks smart questions, generates content.
"""

import json
import re
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config_simple import (
    GROQ_API_KEY,
    PRIMARY_MODEL,
    FALLBACK_MODELS,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    PLATFORMS,
    TONES,
    CONTENT_TYPES,
)


class IntelligentConversationManager:
    """
    Smart conversation manager using simple message history.
    Extracts product info from natural conversation, asks intelligent follow-ups.
    """

    def __init__(self):
        """Initialize with LLM and conversation history."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")

        self.api_key = GROQ_API_KEY
        self.current_model = PRIMARY_MODEL
        self.llm = self._init_client(self.current_model)

        # Simple conversation history tracking for context awareness
        self.conversation_history = []

        # Extracted product info (gets populated as we talk)
        self.product_info = {
            "name": None,
            "description": None,
            "platform": None,
            "tone": None,
            "content_type": None,
            "additional_context": None,
        }

        # Track which info we have
        self.info_collected = set()

    def _init_client(self, model_name: str):
        """Initialize ChatGroq client."""
        return ChatGroq(
            model_name=model_name,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            groq_api_key=self.api_key,
        )

    def _try_with_fallback(self, messages):
        """Try LLM invoke; fallback to next model if decommissioned."""
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

    def extract_info_from_input(self, user_input: str) -> Dict[str, Any]:
        """
        Use LLM to extract product info from user input.
        Returns extracted data and updates product_info.
        """
        extraction_prompt = f"""You are an intelligent assistant extracting product information from user conversation.

User said: "{user_input}"

Extract and return ONLY valid JSON with these fields (null if not mentioned):
{{
    "product_name": "product name if mentioned",
    "product_description": "description/features if mentioned",
    "platform": "instagram/tiktok/linkedin/twitter/facebook if mentioned (lowercase)",
    "tone": "casual/professional/humorous/inspirational/promotional if mentioned (lowercase)",
    "content_type": "product_highlight/sales_promotion/educational/brand_story if mentioned (lowercase)",
    "additional_context": "any other relevant info"
}}

Return ONLY JSON, no extra text."""

        messages = [SystemMessage(content=extraction_prompt)]

        try:
            response = self._try_with_fallback(messages)
            extracted = self._parse_json(response.content)

            # Update product_info with extracted data
            for key, value in extracted.items():
                if value is not None:
                    if key == "product_name" and value:
                        self.product_info["name"] = value
                        self.info_collected.add("name")
                    elif key == "product_description" and value:
                        self.product_info["description"] = value
                        self.info_collected.add("description")
                    elif key == "platform" and value:
                        self.product_info["platform"] = value
                        self.info_collected.add("platform")
                    elif key == "tone" and value:
                        self.product_info["tone"] = value
                        self.info_collected.add("tone")
                    elif key == "content_type" and value:
                        self.product_info["content_type"] = value
                        self.info_collected.add("content_type")
                    elif key == "additional_context" and value:
                        self.product_info["additional_context"] = value

            return extracted

        except Exception as e:
            print(f"⚠️  Extraction failed: {e}")
            return {}

    def generate_intelligent_response(self, user_input: str) -> str:
        """
        Generate intelligent bot response.
        Extract info, identify what's missing, ask smart follow-ups.
        """
        # Extract info from user input
        extracted = self.extract_info_from_input(user_input)

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Determine what's missing
        required_fields = {"name", "description", "platform", "tone", "content_type"}
        missing = required_fields - self.info_collected

        # Format conversation history for context
        history_str = ""
        for msg in self.conversation_history:
            if msg["role"] == "user":
                history_str += f"👤 You: {msg['content']}\n"
            else:
                history_str += f"🤖 Bot: {msg['content']}\n"

        # Generate response
        response_prompt = f"""You are a friendly, intelligent social media content assistant.

Conversation history so far:
{history_str}

Current product info collected:
- Product Name: {self.product_info['name'] or 'Not yet'}
- Description: {self.product_info['description'] or 'Not yet'}
- Platform: {self.product_info['platform'] or 'Not yet'}
- Tone: {self.product_info['tone'] or 'Not yet'}
- Content Type: {self.product_info['content_type'] or 'Not yet'}

Missing info: {', '.join(missing) if missing else 'None - Ready to generate!'}

User just said: "{user_input}"

Instructions:
1. If user provided new info, acknowledge it with specific praise (e.g., "Love that eco-friendly angle!")
2. If ALL info is collected (all 5 fields filled), respond: "Perfect! I have everything needed. Let me generate your social media content pack now."
3. If info is MISSING, ask 2-3 smart follow-up questions to get the missing info. Make questions contextual.
4. When asking about missing fields, provide helpful examples in parentheses:
   - For description: e.g., "(e.g., made from recycled materials, waterproof, eco-friendly)"
   - For platform: e.g., "(e.g., Instagram, TikTok, LinkedIn)"
   - For tone: e.g., "(e.g., casual, professional, humorous, inspirational)"
   - For content_type: e.g., "(e.g., product highlight, sales promotion, educational, brand story)"
5. Keep responses conversational, friendly, max 2-3 sentences.
6. Never list all options - just give 1-2 relevant examples.

Respond naturally, not as a form."""

        messages = [SystemMessage(content=response_prompt)]

        try:
            response = self._try_with_fallback(messages)
            bot_response = response.content

            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})

            return bot_response

        except Exception as e:
            return f"⚠️  Error: {e}"

    def is_ready_to_generate(self) -> bool:
        """Check if we have all required info to generate content."""
        required = {"name", "description", "platform", "tone", "content_type"}
        return required.issubset(self.info_collected)

    def get_product_info(self) -> Dict[str, Any]:
        """Get collected product info."""
        return self.product_info.copy()

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from text."""
        try:
            match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
            if match:
                json_str = match.group()
            else:
                json_str = text
            return json.loads(json_str)
        except:
            return {}

    def get_history(self) -> str:
        """Get conversation history as formatted string."""
        history = ""
        for msg in self.conversation_history:
            if msg["role"] == "user":
                history += f"👤 You: {msg['content']}\n"
            else:
                history += f"🤖 Bot: {msg['content']}\n"
        return history
